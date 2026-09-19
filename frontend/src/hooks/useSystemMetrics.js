import { useState, useEffect, useRef, useCallback } from "react";

// ═══════════════════════════════════════════════════════════════════
// 🧠 useSystemMetrics — 5D Live Data Pipeline
//
//   Polls the backend /system_metrics endpoint every INTERVAL_MS.
//   Falls back to smooth simulated values if the backend is offline
//   so the tesseract always has something to breathe with.
// ═══════════════════════════════════════════════════════════════════

const INTERVAL_MS = 2000; // poll every 2 seconds
const FALLBACK_INTERVAL_MS = 500; // simulated animation tick

function simulateCPU(prev) {
  // Brownian-motion-style simulation so it looks realistic
  const delta = (Math.random() - 0.5) * 12;
  return Math.min(95, Math.max(5, (prev || 35) + delta));
}

function simulateRAM(prev) {
  const delta = (Math.random() - 0.5) * 4;
  return Math.min(90, Math.max(20, (prev || 55) + delta));
}

export default function useSystemMetrics() {
  const [metrics, setMetrics] = useState({
    cpuLoad: 0,
    ramLoad: 0,
    ramUsedGB: 0,
    ramTotalGB: 0,
    isLive: false,
    error: null,
  });

  const simRef = useRef(null);
  const pollRef = useRef(null);
  const lastCpu = useRef(35);
  const lastRam = useRef(55);

  const startSimulation = useCallback(() => {
    if (simRef.current) return; // already running
    simRef.current = setInterval(() => {
      lastCpu.current = simulateCPU(lastCpu.current);
      lastRam.current = simulateRAM(lastRam.current);
      setMetrics((prev) => ({
        ...prev,
        cpuLoad: lastCpu.current,
        ramLoad: lastRam.current,
        isLive: false,
      }));
    }, FALLBACK_INTERVAL_MS);
  }, []);

  const stopSimulation = useCallback(() => {
    if (simRef.current) {
      clearInterval(simRef.current);
      simRef.current = null;
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await fetch("/system_metrics", { signal: AbortSignal.timeout(1500) });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      stopSimulation(); // stop simulation when backend is live
      setMetrics({
        cpuLoad: data.cpu_percent ?? 0,
        ramLoad: data.ram_percent ?? 0,
        ramUsedGB: data.ram_used_gb ?? 0,
        ramTotalGB: data.ram_total_gb ?? 0,
        isLive: true,
        error: null,
      });
    } catch {
      // Backend offline — fall back to smooth simulation
      startSimulation();
      setMetrics((prev) => ({
        ...prev,
        isLive: false,
        error: "backend_offline",
      }));
    }
  }, [startSimulation, stopSimulation]);

  useEffect(() => {
    fetchMetrics(); // immediate first call
    pollRef.current = setInterval(fetchMetrics, INTERVAL_MS);

    return () => {
      clearInterval(pollRef.current);
      stopSimulation();
    };
  }, [fetchMetrics, stopSimulation]);

  return metrics;
}
