/**
 * useBiometricState — Biometric & Environment Domain
 * Manages: geo, thermal, IoT, biometrics, weather, news, tasks, diagnostics
 * Consumers re-render ONLY when sensor data changes (not voice/UI ticks)
 */
import { useState, useCallback, useEffect, useRef } from "react";
import { api } from "@/services/api";

export function useBiometricState({ isInitialized, addLog }) {
  const [biometrics,    setBiometrics]    = useState({ heart_rate: 72, temp: 36.6, mood: "Focused" });
  const [iotState,      setIotState]      = useState({});
  const [geoData,       setGeoData]       = useState({ lat: "40.7128° N", lon: "74.0060° W", sector: "NEW_YORK_SECTOR" });
  const [thermalData,   setThermalData]   = useState({ cpu_load: "12%", gpu: 42, ram: "4.2GB" });
  const [weatherData,   setWeatherData]   = useState({ temp: 22, condition: "Partly Cloudy", wind: 8 });
  const [newsData,      setNewsData]      = useState([]);
  const [taskData,      setTaskData]      = useState([]);
  const [diagnosticData,setDiagnosticData] = useState(null);
  const [foresightData, setForesightData] = useState([]);
  const [evolutionData, setEvolutionData] = useState(null);
  const [biometricData, setBiometricData] = useState(null);

  // Store setters that are used externally (resonance sync, task merging)
  const setGlobalResonanceUrl = useCallback(() => {}, []); // placeholder — moved to useVoiceState

  // ── Fetch functions ───────────────────────────────────────────────────
  const fetchBio = useCallback(async () => {
    try {
      const res = await api.getVitals();
      setBiometrics(res.data);
    } catch { console.warn("Vitals desync"); }
  }, []);

  const fetchIot = useCallback(async () => {
    try {
      const res = await api.getIotState();
      setIotState(res.data);
    } catch { console.warn("IoT desync"); }
  }, []);

  const fetchGeo = useCallback(async () => {
    try {
      const res = await fetch("http://ip-api.com/json/").then(r => r.json());
      setGeoData({
        lat: `${res.lat}° N`,
        lon: `${res.lon}° W`,
        sector: `${res.city.toUpperCase()}_${res.regionName.toUpperCase()}`,
      });
      addLog(`SATELLITE_SYNC_CONFIRMED: ${res.city}`);
    } catch { console.warn("Geo desync"); }
  }, [addLog]);

  // ── Resonance + mission spire sync ───────────────────────────────────
  const syncResonance = useCallback(async (setShowMissionSpire) => {
    try {
      const res = await api.getGhostSync();
      let mergedTasks = res.data.tasks || [];

      // 🏢 SYNC_ENTERPRISE_CORE
      try {
        const enterpriseRes = await api.getEnterpriseTasks();
        if (enterpriseRes.data) {
          const enterpriseTasks = enterpriseRes.data.map(t => ({
            id:          t._id,
            label:       t.type,
            description: `Repository: ${t.githubRepo || "Local"}`,
            status:      t.status.toUpperCase(),
            progress:    t.progress || 0,
            isEnterprise: true,
            timestamp:   t.createdAt,
          }));
          mergedTasks = [...mergedTasks, ...enterpriseTasks];
        }
      } catch (e) { console.warn("Enterprise desync", e); }

      setTaskData(mergedTasks);
      if (res.data.status === "ACTIVE" || mergedTasks.length > 0) setShowMissionSpire(true);
    } catch { console.warn("Resonance desync"); }
  }, []);

  // ── Polling effects ────────────────────────────────────────────────────
  useEffect(() => {
    if (!isInitialized) return;
    const interval = setInterval(() => { fetchBio(); fetchIot(); }, 5000);
    return () => clearInterval(interval);
  }, [isInitialized, fetchBio, fetchIot]);

  useEffect(() => {
    if (!isInitialized) return;
    const interval = setInterval(async () => {
      try {
        const res = await api.getResonanceVitals();
        setThermalData(res.data);
        if (res.data.insight) addLog(res.data.insight);
      } catch { console.warn("Thermal desync"); }
    }, 5000);
    return () => clearInterval(interval);
  }, [isInitialized, addLog]);

  return {
    // state
    biometrics, iotState, geoData, thermalData, weatherData,
    newsData, taskData, diagnosticData, foresightData, evolutionData, biometricData,
    // setters
    setBiometrics, setIotState, setGeoData, setThermalData, setWeatherData,
    setNewsData, setTaskData, setDiagnosticData, setForesightData, setEvolutionData, setBiometricData,
    // actions
    fetchBio, fetchIot, fetchGeo, syncResonance,
  };
}
