'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

const blogSource = fs.readFileSync(
  path.join(__dirname, '..', 'core', 'home', 'assets', 'js', 'blog.js'),
  'utf8',
);
const cubeImport = /import\((['"])\.\/blog-cube\.js\1\)/g;
assert.equal([...blogSource.matchAll(cubeImport)].length, 1);
// Keep the page's real event handlers; replace only its graphics-module boundary.
const source = blogSource.replace(cubeImport, 'loadCubeModule()');
const articles = [
  { title: 'First article', category: 'Systems', read_minutes: 2, dek: 'First introduction.', url: '/blog/first/' },
  { title: 'Second article', category: 'AI & work', read_minutes: 1, dek: 'Second introduction.', url: '/blog/second/' },
];

class Element {
  constructor(ownerDocument, parent = null) {
    this.ownerDocument = ownerDocument;
    this.parent = parent;
    this.listeners = new Map();
    this.attributes = new Map();
    this.dataset = {};
    this.style = {};
    this.hidden = false;
    this.textContent = '';
  }

  addEventListener(type, callback) {
    const listeners = this.listeners.get(type) || [];
    listeners.push(callback);
    this.listeners.set(type, listeners);
  }

  setAttribute(name, value) { this.attributes.set(name, String(value)); }
  getAttribute(name) { return this.attributes.get(name) ?? null; }
  matches(selector) { return selector === '.cube-pin' && this.className === 'cube-pin'; }

  contains(element) {
    for (let current = element; current; current = current.parent) {
      if (current === this) return true;
    }
    return false;
  }

  dispatch(type, properties = {}) {
    const event = {
      type,
      target: this,
      defaultPrevented: false,
      preventDefault() { this.defaultPrevented = true; },
      ...properties,
    };
    for (let current = this; current; current = current.parent) {
      event.currentTarget = current;
      for (const listener of current.listeners.get(type) || []) listener(event);
    }
    return event;
  }

  focus() {
    const previous = this.ownerDocument.activeElement;
    this.ownerDocument.activeElement = this;
    if (previous !== this) previous?.dispatch('focusout', { relatedTarget: this });
  }
}

async function createHarness() {
  const document = new Element();
  document.ownerDocument = document;
  document.activeElement = null;
  const ids = [
    'cubeArticles', 'blogCube', 'cubePoints', 'cubeExplorer', 'articlePreview',
    'cubeConnector', 'cubeStatus', 'growthRange', 'growthToggle', 'growthControls',
    'previewTitle', 'previewMeta', 'previewDek', 'previewLink', 'selectionStatus',
    'growthCount', 'growthExplanation', 'resetCube', 'cubeTools', 'navToggle',
    'articleListLink',
  ];
  const elements = Object.fromEntries(ids.map(id => [id, new Element(document, document)]));
  elements.cubePoints.parent = elements.cubeExplorer;
  elements.articlePreview.parent = elements.cubeExplorer;
  elements.previewLink.parent = elements.articlePreview;
  elements.growthRange.parent = elements.growthControls;
  elements.growthControls.hidden = true;
  elements.growthToggle.setAttribute('aria-expanded', 'false');
  elements.cubeArticles.textContent = JSON.stringify(articles);
  elements.previewTitle.textContent = articles[0].title;
  elements.previewLink.href = articles[0].url;
  const pin = new Element(document, elements.cubePoints);
  pin.className = 'cube-pin';
  pin.dataset.index = '1';
  document.getElementById = id => elements[id] ?? null;
  document.querySelectorAll = () => [];
  const calls = { resets: 0, selections: [] };
  let cubeCallbacks;
  const context = vm.createContext({
    document,
    window: new Element(),
    console,
    async loadCubeModule() {
      return {
        async createBlogCube(callbacks) {
          cubeCallbacks = callbacks;
          callbacks.onReady();
          return {
            reset() { calls.resets += 1; },
            setSelected(index) { calls.selections.push(index); },
            setCount() {},
            dispose() {},
          };
        },
      };
    },
  });
  await vm.runInContext(`(async () => {\n${source}\n})()`, context, { filename: 'blog.js' });
  assert.ok(cubeCallbacks, 'the actual page should initialize its cube module');
  return {
    document, elements, calls, pin,
    selectSecondArticle() { cubeCallbacks.onSelect(1, 'keyboard'); },
    escape(element) { element.focus(); return element.dispatch('keydown', { key: 'Escape' }); },
  };
}

test('Escape in navigation or other page controls preserves the selected article', async () => {
  const harness = await createHarness();
  const { elements, calls } = harness;
  harness.selectSecondArticle();
  const announcement = elements.selectionStatus.textContent;
  for (const id of ['navToggle', 'resetCube', 'articleListLink', 'growthToggle']) {
    const event = harness.escape(elements[id]);
    assert.equal(event.defaultPrevented, false, `${id} keeps its own Escape behavior`);
    assert.equal(calls.resets, 0);
    assert.equal(elements.previewTitle.textContent, articles[1].title);
    assert.equal(elements.previewLink.href, articles[1].url);
    assert.equal(elements.selectionStatus.textContent, announcement);
  }
});

test('Escape closes growth controls and returns focus without resetting the article', async () => {
  const harness = await createHarness();
  const { document, elements, calls } = harness;
  harness.selectSecondArticle();
  for (const target of [elements.growthRange, elements.growthToggle]) {
    elements.growthToggle.dispatch('click');
    assert.equal(elements.growthControls.hidden, false);
    assert.equal(elements.growthToggle.getAttribute('aria-expanded'), 'true');
    const event = harness.escape(target);
    assert.equal(event.defaultPrevented, true);
    assert.equal(elements.growthControls.hidden, true);
    assert.equal(elements.growthToggle.getAttribute('aria-expanded'), 'false');
    assert.equal(document.activeElement, elements.growthToggle);
    assert.equal(calls.resets, 0);
    assert.equal(elements.previewLink.href, articles[1].url);
    assert.equal(elements.previewTitle.textContent, articles[1].title);
  }
});

test('Escape inside the explorer resets the cube and clears the selection announcement', async () => {
  const harness = await createHarness();
  const { elements, calls, pin } = harness;
  for (const target of [pin, elements.previewLink]) {
    harness.selectSecondArticle();
    const priorResets = calls.resets;
    const event = harness.escape(target);
    assert.equal(event.defaultPrevented, true);
    assert.equal(calls.resets, priorResets + 1);
    assert.equal(elements.previewLink.href, articles[0].url);
    assert.equal(elements.previewTitle.textContent, articles[0].title);
    assert.equal(elements.selectionStatus.textContent, '');
  }
});

test('Enter after Escape selects the focused pin before moving to its article link', async () => {
  const harness = await createHarness();
  const { document, elements, calls, pin } = harness;
  harness.selectSecondArticle();
  harness.escape(pin);
  assert.equal(document.activeElement, pin);
  assert.equal(elements.previewLink.href, articles[0].url);
  const event = pin.dispatch('keydown', { key: 'Enter' });
  assert.equal(event.defaultPrevented, true);
  assert.equal(calls.selections.at(-1), 1);
  assert.equal(elements.previewLink.href, articles[1].url);
  assert.equal(elements.previewTitle.textContent, articles[1].title);
  assert.equal(document.activeElement, elements.previewLink);
});
