'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

const scripts = path.join(__dirname, '..', 'core', 'home', 'assets', 'js');
function element() {
  const events = new Map();
  const classes = new Set();
  return {
    hidden: false, dataset: {}, textContent: '',
    style: { removeProperty(key) { delete this[key]; } },
    classList: {
      toggle(name, on) { if (on) classes.add(name); else classes.delete(name); },
      contains(name) { return classes.has(name); },
      add(name) { classes.add(name); },
      remove(name) { classes.delete(name); },
    },
    append(child) { child.parentElement = this; },
    setAttribute(key, value) { this[key] = value; },
    addEventListener(name, handle) { events.set(name, handle); },
    removeEventListener(name) { events.delete(name); },
    emit(name, event) { events.get(name)?.(event); },
  };
}

function stack(count, setup) {
  const articles = Array.from({ length: count }, (_, i) => ({
    title: 'Essay ' + i, dek: 'Summary ' + i, category: 'Topic ' + i,
    read_minutes: i + 1, url: '/blog/essay-' + i + '/',
  }));
  const elements = Object.fromEntries(['stackArticles', 'olderSheet', 'newerSheet', 'sheetCount',
    'sheetStatus', 'previewTitle', 'previewMeta', 'previewDek', 'previewLink', 'stackNavigation', 'stackHoverSurface',
    'stackHoverHint', 'archiveLink', 'allEssays'].map(id => [id, element()]));
  const layers = articles.map(element);
  elements.stackArticles.textContent = JSON.stringify(articles);
  elements.stackNavigation.hidden = true;
  const document = { getElementById: id => elements[id], querySelectorAll: () => layers };
  const context = { document, window: { location: { hash: '' } } };
  setup?.(elements, context);
  vm.runInNewContext(fs.readFileSync(path.join(scripts, 'blog.js'), 'utf8'), context);
  return { ...elements, layers };
}

test('newest sheet first; older/newer move by one, update the link and cannot leave the collection', () => {
  const p = stack(3);
  assert.equal(p.previewTitle.textContent, 'Essay 2');
  assert.equal(p.stackNavigation.hidden, false);
  assert.equal(p.newerSheet['aria-disabled'], 'true');
  p.newerSheet.emit('click'); p.olderSheet.emit('click');
  assert.equal(p.previewTitle.textContent, 'Essay 1');
  assert.equal(p.previewMeta.textContent, 'Topic 1 / 2 min read');
  assert.equal(p.previewDek.textContent, 'Summary 1');
  assert.equal(p.previewLink.href, '/blog/essay-1/');
  assert(p.layers[2].classList.contains('lifted-sheet'));
  assert(p.layers[1].classList.contains('selected-sheet'));
  p.olderSheet.emit('click'); p.olderSheet.emit('click');
  assert.equal(p.olderSheet['aria-disabled'], 'true');
  assert.equal(p.sheetStatus.textContent, 'Sheet 1 of 3. Essay 0');
  p.newerSheet.emit('click'); p.newerSheet.emit('click');
  assert.equal(p.sheetCount.textContent, 'Sheet 3 of 3');
});

test('browse the archive opens every title with one activation', () => {
  const p = stack(3); p.archiveLink.emit('click');
  assert.equal(p.allEssays.open, true);
});

test('each mouse entry turns one sheet and preserves its preview on the way to the essay', () => {
  const p = stack(3);
  const mouse = { pointerType: 'mouse' };
  p.stackHoverSurface.emit('pointerenter', { pointerType: 'touch' });
  assert.equal(p.previewTitle.textContent, 'Essay 2');
  p.stackHoverSurface.emit('pointerenter', mouse);
  p.stackHoverSurface.emit('pointermove', mouse);
  p.stackHoverSurface.emit('pointerleave', mouse);
  assert.equal(p.previewTitle.textContent, 'Essay 1');
  assert.equal(p.previewDek.textContent, 'Summary 1');
  assert.equal(p.previewMeta.textContent, 'Topic 1 / 2 min read');
  assert.equal(p.previewLink.href, '/blog/essay-1/');
  assert(p.layers[1].classList.contains('selected-sheet'));
  p.stackHoverSurface.emit('pointerenter', mouse);
  p.stackHoverSurface.emit('pointerenter', mouse);
  assert.equal(p.olderSheet['aria-disabled'], 'true');
  assert.equal(p.previewTitle.textContent, 'Essay 0');
  p.newerSheet.emit('click');
  assert.equal(p.previewTitle.textContent, 'Essay 1');
});

test('a single sheet has a readable article and no unnecessary controls', () => {
  const p = stack(1);
  assert.equal(p.stackNavigation.hidden, true);
  assert.equal(p.previewLink.href, '/blog/essay-0/');
});

function movingStack() {
  let now = 0, frameId = 0;
  const frames = new Map();
  const preference = element();
  preference.matches = false;
  const p = stack(3, (elements, context) => {
    for (const id of ['turningPaper', 'turnFace', 'turnEdge', 'turnRim', 'turnMarker', 'turnLight', 'turnShadow', 'turnImprint']) {
      elements[id] = element();
    }
    elements.turningPaper.display = 'none';
    const hit = elements.stackHoverSurface;
    const captured = new Set();
    hit.getBoundingClientRect = () => ({ width: 300, height: 200 });
    hit.setPointerCapture = id => captured.add(id);
    hit.hasPointerCapture = id => captured.has(id);
    hit.releasePointerCapture = id => captured.delete(id);
    context.window.matchMedia = () => preference;
    context.performance = { now: () => now };
    context.requestAnimationFrame = callback => {
      frames.set(++frameId, callback);
      return frameId;
    };
    context.cancelAnimationFrame = id => frames.delete(id);
  });
  function advance(milliseconds) {
    now += milliseconds;
    const pending = [...frames.values()];
    frames.clear();
    pending.forEach(callback => callback(now));
  }
  function touch(type, x, y = 100, extra = {}) {
    p.stackHoverSurface.emit(type, {
      pointerType: 'touch', pointerId: 1, isPrimary: true, button: 0,
      clientX: x, clientY: y, timeStamp: now, preventDefault() {}, ...extra,
    });
  }
  return { ...p, advance, touch, preference, frames };
}

function checkTurningLayer(p, expected) {
  const turning = p.layers.filter(layer => layer.classList.contains('turning-sheet'));
  if (expected) {
    assert.deepEqual(turning, [expected]);
    assert.equal(p.turningPaper.parentElement, expected);
    assert.equal(p.turningPaper.display, 'inline');
    assert.equal(p.frames.size, 1);
  } else {
    assert.deepEqual(turning, []);
    // SVG descendants can override visibility, so suppress the entire subtree, stamp included.
    assert.equal(p.turningPaper.display, 'none');
    assert.equal(p.frames.size, 0);
  }
}

test('an interrupted turn hands off one flexible face and reverses from its current bend', () => {
  const p = movingStack();
  p.olderSheet.emit('click');
  p.advance(120);
  checkTurningLayer(p, p.layers[2]);
  assert.equal(p.turnImprint.visibility, 'visible');
  p.olderSheet.emit('click');
  checkTurningLayer(p, p.layers[1]);
  assert.equal(p.turnImprint.visibility, 'hidden');

  const flat = p.turnFace.d;
  p.advance(150);
  const bent = p.turnFace.d;
  assert.notEqual(bent, flat);
  const marker = p.turnMarker.opacity;
  p.newerSheet.emit('click');
  assert.equal(p.turnFace.d, bent);
  checkTurningLayer(p, p.layers[1]);
  p.advance(60);
  assert.ok(p.turnMarker.opacity > marker, 'the corner retraces toward the selected position');
  p.advance(120);
  checkTurningLayer(p);
  assert.equal(p.sheetStatus.textContent, 'Sheet 2 of 3. Essay 1');
});

test('enabling reduced motion during the stamped turn immediately settles the selected sheet', () => {
  const p = movingStack();
  p.olderSheet.emit('click');
  p.advance(110);
  checkTurningLayer(p, p.layers[2]);
  assert.equal(p.turnImprint.visibility, 'visible');
  p.preference.matches = true;
  p.preference.emit('change');
  checkTurningLayer(p);
  assert.equal(p.previewLink.href, '/blog/essay-1/');
  p.newerSheet.emit('click');
  p.advance(800);
  checkTurningLayer(p);
  assert.equal(p.sheetStatus.textContent, 'Sheet 3 of 3. Essay 2');
});

test('a held sheet follows and retraces the finger, then commits a single essay on release', () => {
  const p = movingStack();
  p.touch('pointerdown', 200);
  p.touch('pointermove', 168);
  p.advance(16);
  assert.equal(p.turningPaper.display, 'inline');
  const shallow = p.turnFace.d;
  const shallowTransform = p.layers[2].style.transform;
  assert.ok(shallow);
  assert.ok(shallowTransform);
  p.touch('pointermove', 131);
  p.advance(16);
  const deep = p.turnFace.d;
  const deepTransform = p.layers[2].style.transform;
  assert.notEqual(deep, shallow);
  assert.notEqual(deepTransform, shallowTransform);
  p.advance(850);
  assert.equal(p.turnFace.d, deep, 'holding the finger still holds the curl');
  assert.equal(p.layers[2].style.transform, deepTransform);
  p.touch('pointermove', 168);
  p.advance(16);
  assert.equal(p.turnFace.d, shallow);
  assert.equal(p.layers[2].style.transform, shallowTransform);
  p.touch('pointermove', 65);
  p.advance(80);
  assert.equal(p.previewLink.href, '/blog/essay-2/');
  assert.equal(p.sheetStatus.textContent, 'Sheet 3 of 3. Essay 2');
  p.touch('pointerup', 65);
  p.advance(1000);
  assert.equal(p.previewLink.href, '/blog/essay-1/');
  assert.equal(p.sheetStatus.textContent, 'Sheet 2 of 3. Essay 1');
  checkTurningLayer(p);

  p.touch('pointerdown', 70);
  p.touch('pointermove', 202);
  p.advance(180);
  p.touch('pointerup', 202);
  p.advance(1000);
  assert.equal(p.sheetStatus.textContent, 'Sheet 3 of 3. Essay 2');
  checkTurningLayer(p);
});

test('a short drag settles back while a deliberate flick of the same distance turns once', () => {
  const p = movingStack();
  p.touch('pointerdown', 200);
  p.advance(85);
  p.touch('pointermove', 185);
  p.advance(360);
  p.touch('pointermove', 159);
  p.advance(200);
  p.touch('pointerup', 159);
  p.advance(1000);
  assert.equal(p.previewLink.href, '/blog/essay-2/');
  checkTurningLayer(p);

  p.touch('pointerdown', 200);
  p.advance(12);
  p.touch('pointermove', 185);
  p.advance(16);
  p.touch('pointermove', 159);
  p.advance(6);
  p.touch('pointerup', 159);
  p.advance(1000);
  assert.equal(p.previewLink.href, '/blog/essay-1/');
  checkTurningLayer(p);
});

test('a fresh swipe catches a settling sheet in place and starts moving it back', () => {
  const p = movingStack();
  p.touch('pointerdown', 200);
  p.touch('pointermove', 110);
  p.advance(140);
  p.touch('pointerup', 110);
  p.advance(50);
  // Translation of the flexible face includes its carrier and its own transform.
  const translateX = transform => Number(/translate\(([-.\d]+)/.exec(transform)[1]);
  const screenX = () => translateX(p.layers[2].style.transform) + translateX(p.turningPaper.transform);
  const xBefore = screenX();
  const progressBefore = 1 - p.turnMarker.opacity;
  p.touch('pointerdown', 120);
  p.touch('pointermove', 127);
  p.advance(16);
  assert.ok(1 - p.turnMarker.opacity < progressBefore, 'a rightward drag starts undoing the turn');
  const shift = screenX() - xBefore;
  assert.ok(shift > 0 && shift < 22, 'a 7px drag should move the sheet only a short way');
  p.touch('pointermove', 255);
  p.touch('pointerup', 255);
  p.advance(1000);
  assert.equal(p.sheetStatus.textContent, 'Sheet 3 of 3. Essay 2');
  checkTurningLayer(p);
});

test('cancellation, lost capture, scrolling and dragging past a boundary preserve the essay', () => {
  const p = movingStack();
  for (const end of ['pointercancel', 'lostpointercapture']) {
    p.touch('pointerdown', 200);
    p.touch('pointermove', 68);
    p.advance(20);
    assert.equal(p.turningPaper.display, 'inline');
    p.touch(end, 68);
    p.touch('pointerup', 68);
    p.advance(1000);
    assert.equal(p.sheetStatus.textContent, 'Sheet 3 of 3. Essay 2');
    checkTurningLayer(p);
  }
  p.touch('pointerdown', 150);
  p.touch('pointermove', 145, 160);
  p.touch('pointermove', 25, 180);
  p.advance(20);
  checkTurningLayer(p);
  p.touch('pointerup', 25, 180);
  p.touch('pointerdown', 70);
  p.touch('pointermove', 215);
  p.touch('pointerup', 215);
  p.advance(1000);
  assert.equal(p.sheetStatus.textContent, 'Sheet 3 of 3. Essay 2');
  checkTurningLayer(p);
});

test('only the primary touch controls a swipe and reduced motion still allows a turn', () => {
  const p = movingStack();
  const otherFinger = { pointerId: 2, isPrimary: false };
  p.preference.matches = true;
  p.preference.emit('change');
  p.touch('pointerdown', 200);
  p.touch('pointerdown', 140, 100, otherFinger);
  p.touch('pointermove', 10, 100, otherFinger);
  p.touch('pointerup', 10, 100, otherFinger);
  p.advance(16);
  assert.equal(p.previewLink.href, '/blog/essay-2/');
  p.touch('pointermove', 40);
  p.advance(32);
  checkTurningLayer(p);
  assert.equal(p.previewLink.href, '/blog/essay-2/');
  p.touch('pointerup', 40);
  assert.equal(p.previewLink.href, '/blog/essay-1/');
  checkTurningLayer(p);
});

function essay(reduced = false, fails = false) {
  const video = element();
  video.dataset.src = 'signoff.mp4'; video.parentElement = { querySelector: () => ({ src: 'final-still.webp' }) }; video.hidden = true;
  let plays = 0;
  video.play = () => { plays++; return fails ? Promise.reject(Error('blocked')) : Promise.resolve(); };
  video.pause = () => {};
  const motion = element(); motion.matches = reduced;
  let callback, observed = false;
  class Observer {
    constructor(fn) { callback = fn; }
    observe() { observed = true; }
    disconnect() { observed = false; }
  }
  vm.runInNewContext(fs.readFileSync(path.join(scripts, 'essay-signoff.js'), 'utf8'), {
    document: { querySelector: () => video }, window: { matchMedia: () => motion, IntersectionObserver: Observer },
    IntersectionObserver: Observer,
  });
  return { video, motion, enter() { if (observed) callback([{ isIntersecting: true }]); }, plays: () => plays };
}

test('sign-off loads only on first intersection and returns to its final still', () => {
  const p = essay();
  assert.equal(p.video.src, undefined);
  p.enter(); p.video.emit('playing');
  assert.equal(p.video.hidden, false);
  p.video.emit('ended'); p.enter();
  assert.equal(p.plays(), 1);
  assert.equal(p.video.hidden, true);
});

test('reduced motion skips the media request; switching preference mid-play restores the still', () => {
  const reduced = essay(true); reduced.enter(); assert.equal(reduced.video.src, undefined);
  const p = essay(); p.enter(); p.video.emit('playing');
  p.motion.matches = true; p.motion.emit('change');
  assert.equal(p.video.hidden, true);
});

test('a failed file or blocked playback leaves the still visible', async () => {
  const p = essay(); p.enter(); p.video.emit('playing'); p.video.emit('error');
  assert.equal(p.video.hidden, true);
  const blocked = essay(false, true); blocked.enter(); await Promise.resolve();
  assert.equal(blocked.video.hidden, true);
});
