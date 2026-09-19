import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ═══════════════════════════════════════════════════════════════════
// 🌌 O.M.E.G.A. TESSERACT ENGINE — 4D HYPERCUBE PROJECTION
//
//   MATHEMATICS:
//   A Tesseract has 16 vertices: all (±1, ±1, ±1, ±1) combinations
//   32 edges connect vertices that differ in exactly 1 coordinate.
//
//   4D → 3D PROJECTION (Perspective):
//     factor = wDist / (wDist - w)
//     (x3, y3, z3) = (x4, y4, z4) × factor
//
//   5D BREATHING (System Load):
//     CPU  → rotation speed in XW plane (4D spin rate)
//     RAM  → geometry breathe amplitude (scale oscillation)
// ═══════════════════════════════════════════════════════════════════

// Generate all 16 tesseract vertices: (±1, ±1, ±1, ±1)
function buildTesseractTopology() {
  const vertices = [];
  for (let x = -1; x <= 1; x += 2)
    for (let y = -1; y <= 1; y += 2)
      for (let z = -1; z <= 1; z += 2)
        for (let w = -1; w <= 1; w += 2)
          vertices.push([x, y, z, w]);

  // 32 edges: connect vertices differing in exactly one coordinate
  const edges = [];
  for (let i = 0; i < 16; i++)
    for (let j = i + 1; j < 16; j++) {
      let diffs = 0;
      for (let k = 0; k < 4; k++)
        if (vertices[i][k] !== vertices[j][k]) diffs++;
      if (diffs === 1) edges.push([i, j]);
    }

  return { vertices, edges };
}

// Apply 4D rotation matrices (rotations in XW, YW, ZW, and XY planes)
function rotate4D(v, aXW, aYW, aZW, aXY) {
  let [x, y, z, w] = v;

  // XW plane rotation (the "4D spin" — this creates the tesseract's hypnotic morphing)
  let nx = x * Math.cos(aXW) - w * Math.sin(aXW);
  let nw = x * Math.sin(aXW) + w * Math.cos(aXW);
  x = nx; w = nw;

  // YW plane rotation (secondary 4D axis)
  let ny = y * Math.cos(aYW) - w * Math.sin(aYW);
  nw = y * Math.sin(aYW) + w * Math.cos(aYW);
  y = ny; w = nw;

  // ZW plane rotation (tertiary 4D axis)
  let nz = z * Math.cos(aZW) - w * Math.sin(aZW);
  nw = z * Math.sin(aZW) + w * Math.cos(aZW);
  z = nz; w = nw;

  // XY plane (standard 3D orbit)
  nx = x * Math.cos(aXY) - y * Math.sin(aXY);
  ny = x * Math.sin(aXY) + y * Math.cos(aXY);
  x = nx; y = ny;

  return [x, y, z, w];
}

// Perspective projection: 4D → 3D
function project4D(v, wDist = 3.0, scale = 0.62) {
  const [x, y, z, w] = v;
  const p = wDist / (wDist - w); // perspective factor from W axis
  return [x * p * scale, y * p * scale, z * p * scale];
}

// ─── Tesseract Wireframe (the 32 edges) ───
function TesseractWireframe({ themeColor, cpuLoad, ramLoad }) {
  const linesRef = useRef();
  const { vertices, edges } = useMemo(() => buildTesseractTopology(), []);

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    // Pre-allocate: 32 edges × 2 points × 3 coords = 192 floats
    const positions = new Float32Array(edges.length * 2 * 3);
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return geo;
  }, [edges]);

  const material = useMemo(
    () =>
      new THREE.LineBasicMaterial({
        color: new THREE.Color(themeColor),
        transparent: true,
        opacity: 0.85,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      }),
    [themeColor]
  );

  useFrame(() => {
    const t = performance.now() / 1000;

    // 5D SYSTEM LOAD MAPPING ──────────────────────────────
    const cpu = (cpuLoad || 0) / 100; // normalize 0→1
    const ram = (ramLoad || 0) / 100; // normalize 0→1

    // CPU → XW rotation speed (core 4D spin — accelerates under load)
    const aXW = t * (0.25 + cpu * 0.55);
    // YW / ZW rotate at fixed calm speeds
    const aYW = t * 0.18;
    const aZW = t * 0.12;
    // XY = slow 3D orbit
    const aXY = t * 0.07;

    // RAM → breathing amplitude (geometry expansion/contraction)
    const breathe = 1.0 + Math.sin(t * (1.5 + ram * 2.5)) * (0.08 + ram * 0.18);

    // Update edge positions
    const pos = geometry.attributes.position.array;
    let idx = 0;
    for (const [i, j] of edges) {
      const rA = rotate4D(vertices[i], aXW, aYW, aZW, aXY);
      const rB = rotate4D(vertices[j], aXW, aYW, aZW, aXY);
      const pA = project4D(rA);
      const pB = project4D(rB);

      // eslint-disable-next-line react-hooks/immutability
      pos[idx++] = pA[0] * breathe;
      pos[idx++] = pA[1] * breathe;
      pos[idx++] = pA[2] * breathe;
      pos[idx++] = pB[0] * breathe;
      pos[idx++] = pB[1] * breathe;
      pos[idx++] = pB[2] * breathe;
    }
    geometry.attributes.position.needsUpdate = true;

    // CPU load → opacity pulse (core glows brighter under load)
    if (linesRef.current?.material) {
      const loadGlow = 0.55 + cpu * 0.45 + Math.sin(t * 4) * 0.1;
      linesRef.current.material.opacity = Math.min(1, Math.max(0.3, loadGlow));
    }
  });

  return <lineSegments ref={linesRef} geometry={geometry} material={material} />;
}

// ─── Inner Singularity (glowing point at tesseract centre) ───
function TesseractCore({ themeColor, cpuLoad }) {
  const coreRef = useRef();
  useFrame(() => {
    if (!coreRef.current) return;
    const t = performance.now() / 1000;
    const cpu = (cpuLoad || 0) / 100;
    const s = 0.18 + Math.sin(t * 6) * 0.03 + cpu * 0.12;
    coreRef.current.scale.setScalar(s);
    coreRef.current.rotation.y -= 0.06;
    coreRef.current.rotation.z += 0.04;
  });
  return (
    <mesh ref={coreRef}>
      <octahedronGeometry args={[1, 0]} />
      <meshBasicMaterial
        color={themeColor}
        transparent
        opacity={0.9}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
      <pointLight intensity={4} color={themeColor} distance={6} />
    </mesh>
  );
}

// ─── Data Dimension Labels (CSS — not 3D text, cheaper) ───
function DimensionOverlay({ cpuLoad, ramLoad }) {
  return (
    <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-4 z-50">
      {/* TOP — 4D label */}
      <div className="self-center flex flex-col items-center gap-0.5">
        <span className="font-mono text-[8px] text-cyan-300/60 tracking-[0.5em] uppercase">
          4D Hypercube Projection
        </span>
        <div className="w-16 h-px bg-cyan-500/20" />
      </div>

      {/* BOTTOM — 5D live metrics */}
      <div className="self-center flex items-center gap-6">
        {/* CPU */}
        <div className="flex flex-col items-center gap-1">
          <span className="font-mono text-[7px] text-cyan-400/50 tracking-widest uppercase">
            5D·CPU
          </span>
          <div className="w-20 h-0.5 bg-white/5 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-500 transition-all duration-1000 shadow-[0_0_6px_cyan]"
              style={{ width: `${cpuLoad}%` }}
            />
          </div>
          <span className="font-mono text-[8px] text-cyan-400 font-bold">
            {cpuLoad?.toFixed(1)}%
          </span>
        </div>

        <div className="w-px h-8 bg-white/10" />

        {/* RAM */}
        <div className="flex flex-col items-center gap-1">
          <span className="font-mono text-[7px] text-purple-400/50 tracking-widest uppercase">
            5D·RAM
          </span>
          <div className="w-20 h-0.5 bg-white/5 rounded-full overflow-hidden">
            <div
              className="h-full bg-purple-500 transition-all duration-1000 shadow-[0_0_6px_purple]"
              style={{ width: `${ramLoad}%` }}
            />
          </div>
          <span className="font-mono text-[8px] text-purple-400 font-bold">
            {ramLoad?.toFixed(1)}%
          </span>
        </div>
      </div>
    </div>
  );
}

// ─── Public Export ───
export default function Tesseract4D({ themeColor = "#00f0ff", cpuLoad = 0, ramLoad = 0 }) {
  return (
    <>
      <TesseractWireframe themeColor={themeColor} cpuLoad={cpuLoad} ramLoad={ramLoad} />
      <TesseractCore themeColor={themeColor} cpuLoad={cpuLoad} />
    </>
  );
}

export { DimensionOverlay };
