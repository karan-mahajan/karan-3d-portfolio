export function worldToSvg(worldX, worldZ, svgWidth, svgHeight, bounds) {
  const nx = (worldX - bounds.minX) / (bounds.maxX - bounds.minX);
  const nz = (worldZ - bounds.minZ) / (bounds.maxZ - bounds.minZ);
  return {
    x: nx * svgWidth,
    y: (1 - nz) * svgHeight,
  };
}

export function svgToWorld(svgX, svgY, svgWidth, svgHeight, bounds) {
  const nx = svgX / svgWidth;
  const nz = 1 - svgY / svgHeight;
  return {
    x: bounds.minX + nx * (bounds.maxX - bounds.minX),
    z: bounds.minZ + nz * (bounds.maxZ - bounds.minZ),
  };
}

export function assertCoordRoundTrip(bounds) {
  const samples = [
    [0, 0],
    [36, 0],
    [0, 42],
    [-28, 0],
    [0, -32],
  ];
  for (const [x, z] of samples) {
    const p = worldToSvg(x, z, 1000, 1000, bounds);
    const w = svgToWorld(p.x, p.y, 1000, 1000, bounds);
    const err = Math.hypot(w.x - x, w.z - z);
    if (err > 1e-6) {
      console.warn('[MapCoords] round-trip drift', { x, z, p, w, err });
      return false;
    }
  }
  return true;
}
