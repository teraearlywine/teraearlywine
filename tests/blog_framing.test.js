'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { test } = require('node:test');

const assets = path.join(__dirname, '../core/home/assets');
const source = fs.readFileSync(path.join(assets, 'js/blog-framing.js'), 'utf8');
const framing = import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
const three = import(pathToFileURL(path.join(assets, 'vendor/three/three.module.js')).href);

test('the approved 27-post desktop and phone compositions stay unchanged', async () => {
  const { getCubeCameraSpan } = await framing;
  for (const aspect of [350 / 365, 365 / 365, 400 / 365, 775 / 490, 2]) {
    const previous = aspect > 1.3
      ? Math.max(3 * 1.18, 3 * 1.55 / aspect)
      : Math.max(3 * 1.48, 3 * 1.5 / aspect);
    assert.equal(getCubeCameraSpan(3, aspect), previous);
  }
});

test('resizing through the old breakpoint no longer changes scale abruptly', async () => {
  const { getCubeCameraSpan } = await framing;
  const before = getCubeCameraSpan(3, 1.299);
  const after = getCubeCameraSpan(3, 1.301);
  assert.ok(Math.abs(after - before) / before < 0.003);
  for (let i = 600; i < 2000; i += 1) {
    const a = getCubeCameraSpan(3, i / 1000);
    const b = getCubeCameraSpan(3, (i + 1) / 1000);
    assert.ok(Math.abs(b - a) / a < 0.003, `Scale discontinuity near aspect ${i / 1000}`);
  }
});

test('larger archives keep their nodes, halos and opened panes inside the camera', async () => {
  const { getCubeCameraBounds, getCubeCameraSpan } = await framing;
  const THREE = await three;
  const camera = new THREE.OrthographicCamera(-3, 3, 2.5, -2.5, 0.1, 80);
  camera.position.set(5.8, 3.9, 7.5);
  camera.lookAt(0, -0.08, 0);
  camera.updateMatrixWorld(true);
  const point = new THREE.Vector3();
  const rotation = new THREE.Euler();

  for (const side of [4, 5, 6, 10]) {
    const half = (side - 1) * 0.96 / 2;
    const bounds = getCubeCameraBounds({
      side, spacing: 0.96, rotation: { x: -0.04, y: -0.12 },
      viewMatrix: camera.matrixWorldInverse.elements,
    });
    for (const aspect of [0.65, 1, 1.301, 775 / 490, 2]) {
      const span = getCubeCameraSpan(side, aspect, bounds);
      // Independently project a denser angle grid with Three.js, including
      // billboard halo radius and the full 0.25-unit layer opening.
      for (let pitch = 0; pitch <= 8; pitch += 1) {
        for (let yaw = 0; yaw <= 16; yaw += 1) {
          rotation.set(-0.14 + pitch * 0.025, -0.31 + yaw * 0.02375, 0);
          for (const shape of [
            { extent: half, near: -half, far: half + 0.25, radius: 0.216 },
            { extent: half + 0.22, near: -half - 0.01, far: half + 0.24, radius: 0 },
          ]) {
            for (const x of [-shape.extent, shape.extent]) {
              for (const y of [-shape.extent, shape.extent]) {
                for (const z of [shape.near, shape.far]) {
                  point.set(x, y, z).applyEuler(rotation).applyMatrix4(camera.matrixWorldInverse);
                  assert.ok(Math.abs(point.x) + shape.radius < span * aspect / 2,
                    `${side ** 3} posts exceeded horizontal camera bounds`);
                  assert.ok(Math.abs(point.y) + shape.radius < span / 2,
                    `${side ** 3} posts exceeded vertical camera bounds`);
                }
              }
            }
          }
        }
      }
    }
  }
});
