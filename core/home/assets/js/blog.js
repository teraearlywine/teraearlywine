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
  let activeLayer, frame, started, from, to;
  let copyAnimation;
  const duration = 650;
  function progressAt(now) {
    const distance = Math.max(0, now - started) / duration;
    return to > from ? Math.min(to, from + distance) : Math.max(to, from - distance);
  }
  function finish() {
    cancelAnimationFrame(frame);
    surface.setAttribute('display', 'none');
    if (activeLayer) activeLayer.classList.remove('turning-sheet');
    activeLayer = null;
  }
  function paint(now) {
    const t = progressAt(now);
    // Smoothstep gives the same path and zero landing velocity in either direction.
    drawBend(surface, parts, t * t * (3 - 2 * t), activeLayer === layers[layers.length - 1]);
    if (t === to) finish();
    else frame = requestAnimationFrame(paint);
  }
  motion.addEventListener('change', () => {
    if (motion.matches) {
      finish();
      copyAnimation?.cancel();
    }
  });
  return (previous, next) => {
    if (motion.matches) return;
    const olderTurn = next < previous;
    const layer = layers[Math.max(previous, next)];
    const now = performance.now();
    const destination = olderTurn ? 1 : 0;
    const start = layer === activeLayer ? progressAt(now) : 1 - destination;
    finish();
    from = start;
    to = destination;
    started = now;
    activeLayer = layer;
    layer.append(surface);
    layer.classList.add('turning-sheet');
    parts.imprint.setAttribute('visibility', layer === layers[layers.length - 1] ? 'visible' : 'hidden');
    surface.setAttribute('display', 'inline');
    paint(now);

    copyAnimation?.cancel();
    copyAnimation = document.getElementById('previewCopy')?.animate?.([
      { opacity: .76, transform: `translateY(${olderTurn ? 4 : -4}px)` },
      { opacity: 1, transform: 'translateY(0)' },
    ], { duration: 240, easing: 'cubic-bezier(.18,.7,.25,1)' });
  };
}
const turnPaper = paperMotion();

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
  if (previous !== index) turnPaper?.(previous, index);
}

if (articles.length) {
  showSheet(selected);
  if (articles.length > 1) {
    document.getElementById('stackNavigation').hidden = false;
    older.addEventListener('click', () => showSheet(selected - 1));
    newer.addEventListener('click', () => showSheet(selected + 1));
    document.getElementById('stackHoverSurface').addEventListener('pointerenter', event => {
      if (event.pointerType === 'mouse') showSheet(selected - 1);
    });
    document.getElementById('stackHoverHint').hidden = false;
  }
}

const archive = document.getElementById('allEssays');
document.getElementById('archiveLink').addEventListener('click', () => { archive.open = true; });
if (window.location.hash === '#archive') archive.open = true;
