'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(
  path.join(__dirname, '../core/home/assets/js/net-sales.js'), 'utf8',
);

test('all layers describe the same net sales when a refund is applied or removed', () => {
  function element(attributes = {}) {
    const listeners = {};
    return Object.assign({
      dataset: {},
      addEventListener(name, callback) { listeners[name] = callback; },
      fire(name) { listeners[name](); },
    }, attributes);
  }

  const radios = ['source', 'rule', 'check'].map(value => element({ value }));
  const readoutRadios = radios.map(input => element({ value: input.value }));
  const ids = Object.fromEntries(
    ['sales-refund', 'sales-layer-title', 'sales-total', 'sales-formula', 'sales-explanation', 'next-sales-layer']
      .map(name => [name, element()]),
  );
  ids['sales-refund'].checked = true;
  const pin = element();
  const hint = element();
  const figure = element({
    dataset: { layer: 'rule' },
    querySelector(selector) { return selector === '.cs-pin-label' ? pin : hint; },
  });
  const document = {
    querySelector() { return figure; },
    querySelectorAll(selector) {
      if (selector === '.cs-layer-control input') return [...radios, ...readoutRadios];
      return [ids['sales-refund'], ids['next-sales-layer']];
    },
    getElementById(id) { return ids[id]; },
  };
  vm.runInNewContext(source, { document });

  assert.equal(figure.dataset.layer, 'rule');
  assert.equal(ids['sales-total'].textContent, '$560');
  assert.equal(ids['sales-formula'].textContent, '$600 − $40 = $560');
  ids['next-sales-layer'].fire('click');
  assert.equal(pin.textContent, 'Ledger check');
  assert.equal(ids['sales-formula'].textContent, '$560 reported − $560 ledger = $0');

  ids['sales-refund'].checked = false;
  ids['sales-refund'].fire('change');
  assert.equal(ids['sales-total'].textContent, '$600');
  assert.equal(ids['sales-formula'].textContent, '$600 reported − $600 ledger = $0');
  ids['next-sales-layer'].fire('click');
  assert.equal(pin.textContent, 'Source records');
  assert.doesNotMatch(ids['sales-formula'].textContent, /Refund/);
  ids['sales-refund'].checked = true;
  ids['sales-refund'].fire('change');
  assert.match(ids['sales-formula'].textContent, /Refund −\$40/);
  radios[1].checked = true;
  radios[1].fire('change');
  assert.equal(figure.dataset.layer, 'rule');
  assert.equal(readoutRadios[1].checked, true);
  readoutRadios[2].fire('change');
  assert.equal(figure.dataset.layer, 'check');
  assert.deepEqual(radios.map(radio => radio.checked), [false, false, true]);
  assert.equal(ids['sales-total'].textContent, '$560');
});
