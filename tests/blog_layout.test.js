'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { test } = require('node:test');

const source = fs.readFileSync(path.join(__dirname, '../core/home/assets/js/blog-layout.js'), 'utf8');
const layout = import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);

test('nine articles make a square and the tenth begins a depth layer', async () => {
  const { getCubePositions } = await layout;
  const square = getCubePositions(9);
  assert.equal(new Set(square.map((point) => point.z)).size, 1);
  assert.equal(new Set(square.map((point) => point.x)).size, 3);
  assert.equal(new Set(square.map((point) => point.y)).size, 3);
  assert.deepEqual(getCubePositions(10).at(-1), { x: 0, y: 0, z: 1 });
});

test('growth keeps all existing coordinates and never duplicates a point', async () => {
  const { getCubePositions } = await layout;
  let previous = [];
  for (const count of [0, 1, 9, 10, 27, 28, 36, 64, 65, 125]) {
    const points = getCubePositions(count);
    assert.equal(points.length, count);
    assert.deepEqual(points.slice(0, previous.length), previous);
    assert.equal(new Set(points.map(({ x, y, z }) => `${x},${y},${z}`)).size, count);
    previous = points;
  }
});

test('27 and 64 posts complete full cubes; the next post starts the next shell', async () => {
  const { getCubePositions } = await layout;
  for (const edge of [3, 4]) {
    const points = getCubePositions(edge ** 3);
    for (const axis of ['x', 'y', 'z']) {
      assert.deepEqual([...new Set(points.map((point) => point[axis]))].sort(),
        Array.from({ length: edge }, (_, index) => index));
    }
    assert.equal(Math.max(...Object.values(getCubePositions(edge ** 3 + 1).at(-1))), edge);
  }
});

test('struts only connect existing immediate neighbours once', async () => {
  const { getCubePositions, getCubeConnections } = await layout;
  for (const count of [9, 10, 27, 28, 36, 64]) {
    const points = getCubePositions(count);
    const edges = getCubeConnections(points);
    assert.equal(new Set(edges.map((edge) => [...edge].sort().join(','))).size, edges.length);
    for (const [a, b] of edges) {
      assert.ok(points[a] && points[b]);
      assert.equal(['x', 'y', 'z'].reduce((sum, axis) => sum + Math.abs(points[a][axis] - points[b][axis]), 0), 1);
    }
  }
  assert.equal(getCubeConnections(getCubePositions(9)).length, 12);
  assert.equal(getCubeConnections(getCubePositions(27)).length, 54);
});

test('invalid article counts fail clearly', async () => {
  const { getCubePositions } = await layout;
  for (const count of [-1, 1.5, NaN, Infinity, '9']) {
    assert.throws(() => getCubePositions(count), RangeError);
  }
});
