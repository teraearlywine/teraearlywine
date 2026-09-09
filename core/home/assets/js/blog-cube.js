import * as THREE from '../vendor/three/three.module.js';
import { getCubePositions, getCubeConnections } from './blog-layout.js';

const REST_ROTATION = { x: -0.04, y: -0.12 };
const SPACING = 0.96;
const UP = new THREE.Vector3(0, 1, 0);

/** A real, progressively growing glass sculpture with accessible DOM controls. */
export async function createBlogCube({
  canvas,
  pointLayer,
  articles,
  environmentUrl,
  onSelect = () => {},
  onProject = () => {},
  onReady = () => {},
  onError = () => {},
}) {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
  } catch (error) {
    onError(error);
    return null;
  }

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x3b3a38);
  const camera = new THREE.OrthographicCamera(-3, 3, 2.5, -2.5, 0.1, 80);
  camera.position.set(5.8, 3.9, 7.5);
  camera.lookAt(0, -0.08, 0);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.96;

  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const surface = canvas.parentElement;
  const disposables = new Set();
  const cleanups = [];
  const keep = (resource) => { disposables.add(resource); return resource; };
  const listen = (target, type, callback, options) => {
    target.addEventListener(type, callback, options);
    cleanups.push(() => target.removeEventListener(type, callback, options));
  };

  const pmrem = new THREE.PMREMGenerator(renderer);
  let environmentTarget;
  try {
    if (environmentUrl) {
      const image = await new THREE.TextureLoader().loadAsync(environmentUrl);
      image.mapping = THREE.EquirectangularReflectionMapping;
      image.colorSpace = THREE.SRGBColorSpace;
      environmentTarget = pmrem.fromEquirectangular(image);
      image.dispose();
    }
  } catch (error) {
    // A failed decorative image must not take the article explorer offline.
    console.warn('The cube is using its built-in studio lighting.', error);
  }
  if (!environmentTarget) environmentTarget = makeStudioEnvironment(pmrem);
  scene.environment = environmentTarget.texture;
  keep(environmentTarget);
  pmrem.dispose();

  const sculpture = new THREE.Group();
  sculpture.rotation.set(REST_ROTATION.x, REST_ROTATION.y, 0);
  scene.add(sculpture);
  scene.add(new THREE.AmbientLight(0xe9e3d8, 0.65));
  const keyLight = new THREE.DirectionalLight(0xfff1df, 2.1);
  keyLight.position.set(-3, 6, 5);
  scene.add(keyLight);
  const rimLight = new THREE.DirectionalLight(0xf7f4ed, 2.2);
  rimLight.position.set(4, 1, -4);
  scene.add(rimLight);

  const coordinates = getCubePositions(articles.length);
  const side = Math.max(3, Math.ceil(Math.cbrt(articles.length)));
  const center = (side - 1) / 2;
  const sphereGeometry = keep(new THREE.SphereGeometry(0.145, 36, 24));
  const sphereMaterial = keep(new THREE.MeshPhysicalMaterial({
    envMap: environmentTarget.texture,
    color: 0xffffff,
    metalness: 0,
    roughness: 0.035,
    transmission: 0.92,
    thickness: 0.3,
    attenuationColor: new THREE.Color(0x655748),
    attenuationDistance: 0.3,
    ior: 1.49,
    clearcoat: 1,
    clearcoatRoughness: 0.06,
    envMapIntensity: 5,
    transparent: false,
    opacity: 1,
  }));
  const selectedMaterial = keep(sphereMaterial.clone());
  selectedMaterial.color.set(0xfff4e1);
  selectedMaterial.emissive.set(0xf4dec0);
  selectedMaterial.emissiveIntensity = 0.45;
  selectedMaterial.envMapIntensity = 6;

  const nodes = coordinates.map((coordinate, index) => {
    const mesh = new THREE.Mesh(sphereGeometry, sphereMaterial);
    mesh.position.set((coordinate.x - center) * SPACING, (center - coordinate.y) * SPACING, (coordinate.z - center) * SPACING);
    sculpture.add(mesh);

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'cube-pin';
    button.dataset.index = String(index);
    button.setAttribute('aria-label', articles[index].title);
    button.setAttribute('aria-pressed', 'false');
    button.style.position = 'absolute';
    button.style.transform = 'translate(-50%, -50%)';
    // Native focus/click provides the same article selection on keyboard and touch.
    listen(button, 'pointerenter', (event) => {
      if (event.pointerType === 'mouse') activate(index, 'pointer');
    });
    listen(button, 'focus', () => activate(index, 'keyboard'));
    listen(button, 'click', () => activate(index, 'click'));
    pointLayer.append(button);
    return { mesh, button, coordinate, baseZ: mesh.position.z };
  });

  const strutGeometry = keep(new THREE.CylinderGeometry(0.009, 0.009, 1, 8));
  const strutMaterial = keep(new THREE.MeshStandardMaterial({
    color: 0xb6aa96, metalness: 0.83, roughness: 0.24, envMapIntensity: 1.55,
  }));
  const struts = getCubeConnections(coordinates).map(([a, b]) => {
    const mesh = new THREE.Mesh(strutGeometry, strutMaterial);
    sculpture.add(mesh);
    return { a, b, mesh };
  });

  const layerMaterial = keep(new THREE.MeshPhysicalMaterial({
    color: 0xe9decc, metalness: 0.08, roughness: 0.12,
    transmission: 0.68, thickness: 0.012, transparent: true, opacity: 0.095,
    side: THREE.DoubleSide, depthWrite: false, envMapIntensity: 1.1,
  }));
  const layerWidth = (side - 1) * SPACING + 0.44;
  const layerGeometry = keep(new THREE.PlaneGeometry(layerWidth, layerWidth));
  const edgeGeometry = keep(new THREE.EdgesGeometry(layerGeometry));
  const edgeMaterial = keep(new THREE.LineBasicMaterial({ color: 0xe3d4bd, transparent: true, opacity: 0.52 }));
  const layers = Array.from({ length: side }, (_, z) => {
    const group = new THREE.Group();
    const pane = new THREE.Mesh(layerGeometry, layerMaterial);
    const edge = new THREE.LineSegments(edgeGeometry, edgeMaterial);
    group.add(pane, edge);
    group.position.z = (z - center) * SPACING - 0.01;
    sculpture.add(group);
    return { group, offset: 0, target: 0, baseZ: group.position.z };
  });

  const haloMaterial = keep(new THREE.MeshBasicMaterial({ color: 0xf4dec0, transparent: true, opacity: 0.62, depthTest: false }));
  const halo = new THREE.Mesh(keep(new THREE.TorusGeometry(0.213, 0.003, 6, 64)), haloMaterial);
  halo.visible = false;
  halo.renderOrder = 10;
  scene.add(halo);
  const glowTexture = keep(radialTexture());
  const glowMaterial = keep(new THREE.SpriteMaterial({ map: glowTexture, color: 0xf9d8ac, transparent: true, opacity: 0.32, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending }));
  const glow = new THREE.Sprite(glowMaterial);
  glow.scale.setScalar(0.83);
  glow.visible = false;
  glow.renderOrder = 9;
  scene.add(glow);

  const floorY = -center * SPACING - 0.18;
  const contact = new THREE.Mesh(keep(new THREE.PlaneGeometry(side * 1.9, side * 1.9)), keep(new THREE.MeshBasicMaterial({
    map: glowTexture, color: 0x000000, transparent: true, opacity: 0.42, depthWrite: false,
  })));
  contact.rotation.x = -Math.PI / 2;
  contact.position.y = floorY + 0.002;
  scene.add(contact);

  let count = articles.length;
  let selected = null;
  let disposed = false;
  let contextLost = false;
  let offscreen = false;
  let frameId = 0;
  let lastFrameTime = 0;
  let width = 1;
  let height = 1;
  let targetX = REST_ROTATION.x;
  let targetY = REST_ROTATION.y;
  const projected = new THREE.Vector3();
  const direction = new THREE.Vector3();
  const world = new THREE.Vector3();

  function activate(index, source) {
    if (disposed || index >= count) return;
    setSelected(index);
    onSelect(index, source);
  }

  function setSelected(index) {
    if (index !== null && (!Number.isInteger(index) || index < 0 || index >= count)) return;
    selected = index;
    // The point under the cursor stays in place while its article is explored.
    targetX = sculpture.rotation.x;
    targetY = sculpture.rotation.y;
    const selectedLayer = index === null ? -1 : nodes[index].coordinate.z;
    layers.forEach((layer, layerIndex) => { layer.target = layerIndex === selectedLayer ? 0.25 : 0; });
    nodes.forEach(({ mesh, button }, nodeIndex) => {
      mesh.material = nodeIndex === selected ? selectedMaterial : sphereMaterial;
      button.classList.toggle('is-selected', nodeIndex === selected);
      button.setAttribute('aria-pressed', String(nodeIndex === selected));
    });
    halo.visible = glow.visible = selected !== null;
    requestFrame();
  }

  function setCount(nextCount) {
    if (!Number.isFinite(nextCount)) return;
    count = Math.max(0, Math.min(articles.length, Math.floor(nextCount)));
    nodes.forEach(({ mesh, button }, index) => {
      mesh.visible = index < count;
      button.hidden = index >= count;
    });
    struts.forEach(({ mesh, a, b }) => { mesh.visible = a < count && b < count; });
    layers.forEach(({ group }, index) => { group.visible = nodes.some((node, nodeIndex) => nodeIndex < count && node.coordinate.z === index); });
    if (selected !== null && selected >= count) setSelected(null);
    requestFrame();
  }

  function reset() {
    setSelected(null);
    targetX = REST_ROTATION.x;
    targetY = REST_ROTATION.y;
    requestFrame();
  }

  function requestFrame() {
    if (!disposed && !contextLost && !offscreen && !document.hidden && !frameId) {
      frameId = requestAnimationFrame(render);
    }
  }

  function render(now) {
    frameId = 0;
    if (disposed || contextLost || offscreen || document.hidden) return;
    const delta = Math.min(0.06, (now - (lastFrameTime || now - 16)) / 1000);
    lastFrameTime = now;
    const easing = motionPreference.matches ? 1 : 1 - Math.exp(-delta * 8);
    let unsettled = false;
    for (const [axis, target] of [['x', targetX], ['y', targetY]]) {
      const remaining = target - sculpture.rotation[axis];
      sculpture.rotation[axis] += remaining * easing;
      if (Math.abs(remaining) > 0.0001) unsettled = true;
    }
    layers.forEach((layer) => {
      const remaining = layer.target - layer.offset;
      layer.offset += remaining * easing;
      layer.group.position.z = layer.baseZ + layer.offset;
      if (Math.abs(remaining) > 0.0001) unsettled = true;
    });
    nodes.forEach((node) => { node.mesh.position.z = node.baseZ + layers[node.coordinate.z].offset; });
    struts.forEach(({ mesh, a, b }) => {
      const start = nodes[a].mesh.position;
      const end = nodes[b].mesh.position;
      mesh.position.copy(start).add(end).multiplyScalar(0.5);
      direction.subVectors(end, start);
      mesh.scale.y = direction.length();
      mesh.quaternion.setFromUnitVectors(UP, direction.normalize());
    });
    sculpture.updateMatrixWorld(true);
    camera.updateMatrixWorld(true);
    nodes.forEach(({ mesh, button }, index) => {
      if (index >= count) return;
      mesh.getWorldPosition(world);
      projected.copy(world).project(camera);
      const x = (projected.x * 0.5 + 0.5) * width;
      const y = (-projected.y * 0.5 + 0.5) * height;
      button.style.left = `${x.toFixed(2)}px`;
      button.style.top = `${y.toFixed(2)}px`;
      button.style.zIndex = String(100 + Math.round((1 - projected.z) * 100));
      if (index === selected) {
        halo.position.copy(world);
        halo.quaternion.copy(camera.quaternion);
        glow.position.copy(world);
        onProject({ x, y, index });
      }
    });
    renderer.render(scene, camera);
    if (unsettled) requestFrame();
  }

  function resize() {
    const rect = canvas.getBoundingClientRect();
    width = Math.max(1, rect.width || surface.clientWidth);
    height = Math.max(1, rect.height || surface.clientHeight);
    const aspect = width / height;
    // Keep the sculpture generous on wide screens, with a width guard on phones.
    const span = aspect > 1.3
      ? Math.max(side * 1.18, side * 1.55 / aspect)
      : Math.max(side * 1.48, side * 1.5 / aspect);
    camera.left = -span * aspect / 2;
    camera.right = span * aspect / 2;
    camera.top = span / 2;
    camera.bottom = -span / 2;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
    requestFrame();
  }

  listen(surface, 'pointermove', (event) => {
    if (selected !== null || motionPreference.matches || event.pointerType !== 'mouse') return;
    const rect = canvas.getBoundingClientRect();
    const x = THREE.MathUtils.clamp((event.clientX - rect.left) / width - 0.5, -0.5, 0.5);
    const y = THREE.MathUtils.clamp((event.clientY - rect.top) / height - 0.5, -0.5, 0.5);
    targetY = REST_ROTATION.y + x * 0.38;
    targetX = REST_ROTATION.x + y * 0.2;
    requestFrame();
  }, { passive: true });
  listen(surface, 'pointerleave', () => {
    if (selected === null) reset();
  });
  listen(document, 'visibilitychange', () => {
    lastFrameTime = 0;
    if (document.hidden && frameId) { cancelAnimationFrame(frameId); frameId = 0; }
    else requestFrame();
  });
  listen(motionPreference, 'change', () => { if (motionPreference.matches) reset(); else requestFrame(); });
  listen(canvas, 'webglcontextlost', (event) => {
    event.preventDefault();
    contextLost = true;
    if (frameId) cancelAnimationFrame(frameId);
    frameId = 0;
    nodes.forEach(({ button }) => { button.hidden = true; });
    onError(new Error('The 3D canvas lost its graphics context. The article list is still available.'));
  });
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(surface);
  cleanups.push(() => resizeObserver.disconnect());
  if ('IntersectionObserver' in window) {
    const visibilityObserver = new IntersectionObserver(([entry]) => {
      offscreen = !entry.isIntersecting;
      if (offscreen && frameId) { cancelAnimationFrame(frameId); frameId = 0; }
      if (!offscreen) { lastFrameTime = 0; requestFrame(); }
    }, { rootMargin: '100px' });
    visibilityObserver.observe(canvas);
    cleanups.push(() => visibilityObserver.disconnect());
  }

  function dispose() {
    if (disposed) return;
    disposed = true;
    if (frameId) cancelAnimationFrame(frameId);
    cleanups.forEach((cleanup) => cleanup());
    nodes.forEach(({ button }) => button.remove());
    disposables.forEach((resource) => resource.dispose());
    renderer.dispose();
  }

  setCount(count);
  resize();
  const api = { setSelected, setCount, reset, dispose };
  onReady(api);
  return api;
}

function radialTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 96;
  const context = canvas.getContext('2d');
  const gradient = context.createRadialGradient(48, 48, 0, 48, 48, 48);
  gradient.addColorStop(0, 'rgba(255,255,255,0.8)');
  gradient.addColorStop(0.18, 'rgba(255,255,255,0.38)');
  gradient.addColorStop(0.48, 'rgba(255,255,255,0.12)');
  gradient.addColorStop(1, 'rgba(255,255,255,0)');
  context.fillStyle = gradient;
  context.fillRect(0, 0, 96, 96);
  return new THREE.CanvasTexture(canvas);
}

/** Local light cards keep real reflections if the optional studio image fails. */
function makeStudioEnvironment(pmrem) {
  const studio = new THREE.Scene();
  const shellGeometry = new THREE.SphereGeometry(20, 24, 12);
  const shellMaterial = new THREE.MeshBasicMaterial({ color: 0x44423e, side: THREE.BackSide });
  studio.add(new THREE.Mesh(shellGeometry, shellMaterial));
  const cardGeometry = new THREE.PlaneGeometry(6, 10);
  const cardMaterial = new THREE.MeshBasicMaterial({ color: new THREE.Color(5, 4.4, 3.6), side: THREE.DoubleSide });
  [[-7, 5, 5], [8, 4, -3], [0, 9, 0]].forEach(([x, y, z]) => {
    const card = new THREE.Mesh(cardGeometry, cardMaterial);
    card.position.set(x, y, z);
    card.lookAt(0, 0, 0);
    studio.add(card);
  });
  const result = pmrem.fromScene(studio, 0.04);
  [shellGeometry, shellMaterial, cardGeometry, cardMaterial].forEach((resource) => resource.dispose());
  return result;
}
