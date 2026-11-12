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
    classList: { toggle(name, on) { if (on) classes.add(name); else classes.delete(name); }, contains(name) { return classes.has(name); } },
    setAttribute(key, value) { this[key] = value; },
    addEventListener(name, handle) { events.set(name, handle); },
    removeEventListener(name) { events.delete(name); },
    emit(name) { events.get(name)?.(); },
  };
}

function stack(count) {
  const articles = Array.from({ length: count }, (_, i) => ({
    title: 'Essay ' + i, dek: 'Summary ' + i, category: 'Topic ' + i,
    read_minutes: i + 1, url: '/blog/essay-' + i + '/',
  }));
  const elements = Object.fromEntries(['stackArticles', 'olderSheet', 'newerSheet', 'sheetCount',
    'sheetStatus', 'previewTitle', 'previewMeta', 'previewDek', 'previewLink', 'stackNavigation', 'archiveLink', 'allEssays'].map(id => [id, element()]));
  const layers = articles.map(element);
  elements.stackArticles.textContent = JSON.stringify(articles);
  elements.stackNavigation.hidden = true;
  const document = { getElementById: id => elements[id], querySelectorAll: () => layers };
  vm.runInNewContext(fs.readFileSync(path.join(scripts, 'blog.js'), 'utf8'), { document, window: { location: { hash: '' } } });
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

test('a single sheet has a readable article and no unnecessary controls', () => {
  const p = stack(1);
  assert.equal(p.stackNavigation.hidden, true);
  assert.equal(p.previewLink.href, '/blog/essay-0/');
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
