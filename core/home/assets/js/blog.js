const articles = JSON.parse(document.getElementById('stackArticles').textContent);
const layers = [...document.querySelectorAll('[data-sheet]')];
const older = document.getElementById('olderSheet');
const newer = document.getElementById('newerSheet');
const count = document.getElementById('sheetCount');
const status = document.getElementById('sheetStatus');
let selected = articles.length - 1;

// The back corner anchors the turn. The two free edges follow with a deeper
// bend, so the sheet catches light as it clears the sheet beneath it.
function drawBend(surface, parts, progress, hasImprint) {
  const bend = Math.sin(Math.PI * progress);
  // Pull the turning sheet out from under the already-turned stack.
  surface.setAttribute('transform', `translate(${-39 * bend} ${24 * bend})`);
  const cornerLift = 47 * bend * (1 + .55 * (1 - 2 * progress));
  const frontLift = 59 * bend * (1 - .38 * (1 - 2 * progress));
  const left = [61 + bend * 5, 147 - cornerLift];
  const front = [283 - bend * 9, 258 - frontLift];
  const backCurve = [178, 95 - cornerLift * .12];
  const rightCurve = [401, 203.5 - frontLift * .21];
  const frontCurve = [172 - bend * 9, 202.5 - cornerLift * .9 - frontLift * .72];
  parts.face.setAttribute('d',
    `M${left}Q${backCurve} 295 43L519 149Q${rightCurve} ${front}Q${frontCurve} ${left}Z`);

  const below = ([x, y], thickness) => [x, y + thickness];
  const lowerLip = thickness =>
    `Q${below(rightCurve, thickness)} ${below(front, thickness)}Q${below(frontCurve, thickness)} ${below(left, thickness)}`;
  parts.edge.setAttribute('d',
    `M${left}Q${frontCurve} ${front}Q${rightCurve} 519 149L519 151.8${lowerLip(2.8)}Z`);
  parts.rim.setAttribute('d', `M519 151.4${lowerLip(2.4)}`);
  parts.marker.setAttribute('opacity', 1 - progress);
  parts.light.setAttribute('opacity', bend * .87);
  parts.shadow.setAttribute('opacity', bend * .27);
  parts.shadow.setAttribute('transform', `translate(${bend * 3} ${bend * 7})`);
  if (hasImprint) {
    // The stamp rides the local slope of the face.
    parts.imprint.setAttribute('transform',
      `translate(270 150) matrix(1 ${bend * .08} 0 ${1 - bend * .22} 0 ${-frontLift * .37}) translate(-270 -150)`);
  }
}

function paperMotion() {
  const surface = document.getElementById('turningPaper');
  if (!surface) return;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const parts = Object.fromEntries(
    ['face', 'edge', 'rim', 'marker', 'light', 'shadow', 'imprint'].map(name =>
      [name, document.getElementById('turn' + name[0].toUpperCase() + name.slice(1))])
  );
  let activeLayer, underSheet, frame, position = 0, grip = 0;
  let copyAnimation;

  function finish() {
    cancelAnimationFrame(frame);
    surface.setAttribute('display', 'none');
    if (activeLayer) {
      activeLayer.classList.remove('turning-sheet');
      underSheet.classList.remove('under-turn');
      activeLayer.style.transform = underSheet.style.transform = '';
    }
    activeLayer = null;
  }

  function pickUp(index, start) {
    cancelAnimationFrame(frame);
    if (activeLayer === layers[index]) return;
    finish();
    activeLayer = layers[index];
    underSheet = layers[index - 1];
    activeLayer.append(surface);
    activeLayer.classList.add('turning-sheet');
    underSheet.classList.add('under-turn');
    surface.setAttribute('display', 'inline');
    parts.imprint.setAttribute('visibility', index === layers.length - 1 ? 'visible' : 'hidden');
    position = start;
    grip = 0;
  }

  function paint(progress, pull) {
    position = progress;
    grip = pull;
    // At rest these are exactly the selected and lifted poses from the stylesheet.
    activeLayer.style.transform = `translate(${-20 + 42 * progress + pull}px, ${-25 * progress}px)`;
    underSheet.style.transform = `translateX(${-20 * progress}px)`;
    drawBend(surface, parts, progress, activeLayer === layers[layers.length - 1]);
  }

  function settle(destination) {
    if (!activeLayer) return;
    cancelAnimationFrame(frame);
    const from = position;
    const startPull = grip;
    const started = performance.now();
    const duration = Math.max(120, 650 * Math.abs(destination - from));
    function tick(now) {
      const t = Math.min(1, Math.max(0, (now - started) / duration));
      const eased = t * t * (3 - 2 * t);
      paint(from + (destination - from) * eased, startPull * (1 - eased));
      if (t === 1) finish();
      else frame = requestAnimationFrame(tick);
    }
    tick(started);
  }

  motion.addEventListener('change', () => {
    if (motion.matches) {
      finish();
      copyAnimation?.cancel();
    }
  });
  // Horizontal position of the flexible face on its unassisted path.
  function offsetAt(progress) {
    return -20 + 42 * progress - 39 * Math.sin(Math.PI * progress);
  }
  return {
    turn(previous, next) {
      if (motion.matches) return;
      const destination = next < previous ? 1 : 0;
      pickUp(Math.max(previous, next), 1 - destination);
      settle(destination);
      copyAnimation?.cancel();
      copyAnimation = document.getElementById('previewCopy')?.animate?.([
        { opacity: .76, transform: `translateY(${destination ? 4 : -4}px)` },
        { opacity: 1, transform: 'translateY(0)' },
      ], { duration: 240, easing: 'cubic-bezier(.18,.7,.25,1)' });
    },
    grab(index, rest) {
      if (motion.matches) return { progress: rest, x: offsetAt(rest) };
      pickUp(index, rest);
      return { progress: position, x: offsetAt(position) + grip };
    },
    drag(index, progress, x) {
      if (motion.matches) return;
      pickUp(index, progress);
      paint(progress, x - offsetAt(progress));
    },
    settle,
    finish,
  };
}
const paper = paperMotion();

function showSheet(index) {
  if (index < 0 || index >= articles.length) return;
  const previous = selected;
  selected = index;
  const article = articles[index];
  layers.forEach((layer, position) => {
    layer.classList.toggle('selected-sheet', position === index);
    layer.classList.toggle('lifted-sheet', position > index);
  });
  document.getElementById('previewTitle').textContent = article.title;
  document.getElementById('previewMeta').textContent = article.category + ' / ' + article.read_minutes + ' min read';
  document.getElementById('previewDek').textContent = article.dek;
  document.getElementById('previewLink').href = article.url;
  count.textContent = 'Sheet ' + (index + 1) + ' of ' + articles.length;
  older.setAttribute('aria-disabled', String(index === 0));
  newer.setAttribute('aria-disabled', String(index === articles.length - 1));
  status.textContent = count.textContent + '. ' + article.title;
  if (previous !== index) paper?.turn(previous, index);
}

function enableSwipe(hit) {
  let drag;

  hit.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'touch' || !event.isPrimary) return;
    const width = hit.getBoundingClientRect().width;
    if (!width) return;
    drag = {
      id: event.pointerId, x: event.clientX, y: event.clientY, origin: selected,
      travel: Math.min(170, Math.max(90, width * .5)),
      // The stationary SVG outline is 485 drawing units wide.
      scale: 485 / width, samples: [{ x: event.clientX, time: event.timeStamp }],
    };
  });

  function track(event) {
    if (!drag || event.pointerId !== drag.id) return;
    const dx = event.clientX - drag.x;
    const dy = event.clientY - drag.y;
    if (!drag.horizontal) {
      if (Math.max(Math.abs(dx), Math.abs(dy)) < 6) return;
      if (Math.abs(dx) <= Math.abs(dy)) {
        drag = null;
        return;
      }
      drag.horizontal = true;
      hit.setPointerCapture(event.pointerId);
    }

    // Keep a short release history: stopping the finger also stops a flick.
    drag.samples = drag.samples.filter(sample => event.timeStamp - sample.time <= 90);
    drag.samples.push({ x: event.clientX, time: event.timeStamp });
    const target = drag.origin + Math.sign(dx);
    if (!dx || target < 0 || target >= layers.length) {
      if (drag.target != null) paper.finish();
      drag.target = null;
      return;
    }
    if (target !== drag.target) {
      drag.startPose = paper.grab(Math.max(drag.origin, target), dx < 0 ? 0 : 1);
      drag.target = target;
    }
    drag.amount = Math.abs(dx) / drag.travel;
    const progress = Math.max(0, Math.min(1, drag.startPose.progress - dx / drag.travel));
    const desired = drag.startPose.x + dx * drag.scale;
    // Give the edge a little resistance near the border of the illustration.
    const excess = Math.max(0, Math.abs(desired) - 44);
    const x = Math.sign(desired) * (Math.min(Math.abs(desired), 44) + 12 * (1 - Math.exp(-excess / 12)));
    paper.drag(Math.max(drag.origin, target), progress, x);
  }

  function release(commit) {
    const held = drag;
    drag = null;
    if (held?.target == null || held.origin !== selected) return;
    if (commit) showSheet(held.target);
    else paper.settle(held.target < held.origin ? 0 : 1);
  }
  hit.addEventListener('pointermove', track);
  hit.addEventListener('pointerup', event => {
    if (!drag || drag.id !== event.pointerId) return;
    if (drag.horizontal) track(event);
    if (drag.target == null) return release(false);
    const dx = event.clientX - drag.x;
    const first = drag.samples[0];
    const velocity = (event.clientX - first.x) / Math.max(1, event.timeStamp - first.time);
    const forwardSpeed = velocity * Math.sign(dx);
    const flick = Math.abs(dx) >= 22 && forwardSpeed >= .5;
    release(flick || (drag.amount >= .5 && forwardSpeed > -.5));
  });
  function cancel(event) {
    if (event.pointerId === drag?.id) release(false);
  }
  hit.addEventListener('pointercancel', cancel);
  hit.addEventListener('lostpointercapture', cancel);
  return () => release(false);
}

if (articles.length) {
  showSheet(selected);
  if (articles.length > 1) {
    document.getElementById('stackNavigation').hidden = false;
    const hit = document.getElementById('stackHoverSurface');
    const cancelSwipe = paper && enableSwipe(hit);
    function navigate(step) {
      cancelSwipe?.();
      showSheet(selected + step);
    }
    older.addEventListener('click', () => navigate(-1));
    newer.addEventListener('click', () => navigate(1));
    hit.addEventListener('pointerenter', event => {
      if (event.pointerType === 'mouse') navigate(-1);
    });
    document.getElementById('stackHoverHint').hidden = false;
  }
}

const archive = document.getElementById('allEssays');
document.getElementById('archiveLink').addEventListener('click', () => { archive.open = true; });
if (window.location.hash === '#archive') archive.open = true;
