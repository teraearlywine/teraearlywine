/**
 * Append-only coordinates for a growing collection of articles.
 * The first nine fill a square; the next eighteen complete a 3 × 3 × 3 cube.
 * Further articles fill the outside shell of the next larger cube.
 */
export function getCubePositions(count) {
  if (!Number.isInteger(count) || count < 0) {
    throw new RangeError('The article count must be a non-negative integer.');
  }

  const positions = [];
  for (let z = 0; z < 3 && positions.length < count; z += 1) {
    for (let y = 0; y < 3 && positions.length < count; y += 1) {
      for (let x = 0; x < 3 && positions.length < count; x += 1) {
        positions.push({ x, y, z });
      }
    }
  }

  for (let edge = 3; positions.length < count; edge += 1) {
    for (let z = 0; z <= edge && positions.length < count; z += 1) {
      for (let y = 0; y <= edge && positions.length < count; y += 1) {
        for (let x = 0; x <= edge && positions.length < count; x += 1) {
          if (Math.max(x, y, z) === edge) positions.push({ x, y, z });
        }
      }
    }
  }
  return positions;
}

/** Only join immediate neighbours, so a new post never changes old topology. */
export function getCubeConnections(positions) {
  const at = new Map(positions.map(({ x, y, z }, index) => [`${x},${y},${z}`, index]));
  const connections = [];
  positions.forEach(({ x, y, z }, index) => {
    [[x + 1, y, z], [x, y + 1, z], [x, y, z + 1]].forEach((next) => {
      const neighbour = at.get(next.join(','));
      if (neighbour !== undefined) connections.push([index, neighbour]);
    });
  });
  return connections;
}
