/** Blend the approved phone and desktop framing without a breakpoint jump. */
export function getCubeCameraSpan(side, aspect, bounds = null) {
  const phone = Math.max(side * 1.48, side * 1.5 / aspect);
  const desktop = Math.max(side * 1.18, side * 1.55 / aspect);
  const progress = Math.max(0, Math.min(1, (aspect - 1.15) / 0.3));
  const blend = progress * progress * (3 - 2 * progress);
  const preferred = phone + (desktop - phone) * blend;

  // The initial 27-post sculpture keeps its approved composition. Larger
  // archives reserve enough room for their panes, selected halo, and tilt.
  return side <= 3 || !bounds
    ? preferred
    : Math.max(preferred, bounds.height, bounds.width / aspect);
}

/** Camera-space envelope of the sculpture throughout its bounded interaction. */
export function getCubeCameraBounds({ side, spacing, rotation, viewMatrix }) {
  const half = (side - 1) * spacing / 2;
  let horizontal = 0;
  let vertical = 0;
  const surfaces = [
    { extent: half, near: -half, far: half + 0.25, padding: 0.216 },
    { extent: half + 0.22, near: -half - 0.01, far: half + 0.24, padding: 0 },
  ];

  // Include intermediate angles so an opened layer never makes the camera
  // zoom while the reader moves. The small margin also covers interpolation.
  for (let pitch = 0; pitch <= 4; pitch += 1) {
    const angleX = rotation.x - 0.1 + pitch * 0.05;
    const cx = Math.cos(angleX);
    const sx = Math.sin(angleX);
    for (let yaw = 0; yaw <= 8; yaw += 1) {
      const angleY = rotation.y - 0.19 + yaw * 0.0475;
      const cy = Math.cos(angleY);
      const sy = Math.sin(angleY);
      for (const { extent, near, far, padding } of surfaces) {
        for (const x of [-extent, extent]) {
          for (const y of [-extent, extent]) {
            for (const z of [near, far]) {
              // Three.js XYZ Euler rotation, followed by the camera view.
              const rx = cy * x + sy * z;
              const ry = sx * sy * x + cx * y - sx * cy * z;
              const rz = -cx * sy * x + sx * y + cx * cy * z;
              const vx = viewMatrix[0] * rx + viewMatrix[4] * ry + viewMatrix[8] * rz + viewMatrix[12];
              const vy = viewMatrix[1] * rx + viewMatrix[5] * ry + viewMatrix[9] * rz + viewMatrix[13];
              horizontal = Math.max(horizontal, Math.abs(vx) + padding);
              vertical = Math.max(vertical, Math.abs(vy) + padding);
            }
          }
        }
      }
    }
  }
  return { width: (horizontal + 0.035) * 2, height: (vertical + 0.035) * 2 };
}
