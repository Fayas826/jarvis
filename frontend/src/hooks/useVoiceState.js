/**
 * useVoiceState — Voice & Audio Domain
 * Manages: mic, speech recognition, TTS, clap detection, sonic sentry, forge
 * Consumers re-render ONLY when voice state changes (not UI/biometric ticks)
 */
import { useState, useCallback, useRef, useEffect } from "react";
import { api } from "@/services/api";

export function useVoiceState({ addLog, status, setStatus, setMessages, setIsVisionActive, setAssemblyStep, speak, PROFILES, profile, settings, reportRecovery, processLocalIntent }) {
  // ── Audio state ───────────────────────────────────────────────────────
  const [isVoiceIgnited,   setIsVoiceIgnited]   = useState(false);
  const [interimText,      setInterimText]      = useState("");
  const [activeForgeId,    setActiveForgeId]    = useState(null);
  const [forgeLogs,        setForgeLogs]        = useState([]);
  const [proposedForge,    setProposedForge]    = useState(null);
  const [isProcessingInput,setIsProcessingInput]= useState(false);
  const [isGhostActive,    setIsGhostActive]    = useState(false);
  const [sonicSentryActive,setSonicSentryActive]= useState(false);
  const [globalResonanceUrl,setGlobalResonanceUrl] = useState("");
  const [intelSource,      setIntelSource]      = useState("CLOUD");
  const [omegaState,       setOmegaState]       = useState({ active: false, frequency: "1.21 EHz", vectors: [] });
  const [acousticStats,    setAcousticStats]    = useState({
    voiceAdaptation: 100, clapAdaptation: 100,
    falseTriggers: 0, noiseRejection: 95, intelligenceScore: 98,
  });

  // ── Refs ──────────────────────────────────────────────────────────────
  const recognitionRef  = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef     = useRef(null);
  const lastClapTimeRef = useRef(0);
  const isContinuousRef = useRef(false);
  const hasInteractedRef= useRef(false);
  const noiseFloorRef   = useRef(30);
  const startVoiceRef   = useRef(null);
  const sessionIdRef    = useRef(
    sessionStorage.getItem("jarvis_session_id") || Math.random().toString(36).substring(7)
  );

  if (!sessionStorage.getItem("jarvis_session_id")) {
    sessionStorage.setItem("jarvis_session_id", sessionIdRef.current);
  }

  // ── processInput (central AI dispatch) ───────────────────────────────
  const processInput = useCallback(async (text) => {
    const cleanText = text.trim();
    if (!cleanText) return;

    // 🤝 DOMAIN_9: COLLECTIVE_INTELLIGENCE
    const criticalKeywords = ["deploy", "delete", "format", "shutdown", "ignite", "execute", "combat"];
    if (criticalKeywords.some(k => cleanText.toLowerCase().includes(k))) {
      addLog("🤝 COLLECTIVE: Critical Intent Detected. Initiating Agent Council Debate...");
      try {
        const debateRes = await api.postCollectiveDebate(cleanText, {});
        Object.entries(debateRes.data.debate).forEach(([agent, result]) => {
          addLog(`🤝 [${agent.toUpperCase()}_AGENT]: ${result.vote} - ${result.reason}`);
        });
        if (debateRes.data.decision === "REJECTED") {
          speak("Sir, the Council of Agents has vetoed this action due to safety risks.");
          addLog("🤝 COLLECTIVE: ACTION_VETOED_BY_CONSENSUS");
          return;
        } else if (debateRes.data.decision === "PROCEED_WITH_CAUTION") {
          addLog("🤝 COLLECTIVE: PROCEEDING_WITH_CAUTION_ADVISED");
          speak("Proceeding with caution, Sir.");
        }
      } catch { console.error("Collective Engine offline."); }
    }

    // 🔬 DOMAIN_11: PROJECT_DIAGNOSTIC
    if (cleanText.toLowerCase().includes("diagnostic mode") || cleanText.toLowerCase().includes("audit project")) {
      addLog("🔬 DIAGNOSTIC: Initiating Project-Wide Deep Audit...");
      speak("Initiating project-wide diagnostic mode, Sir.");
      try {
        const res = await api.getProjectDiagnostic();
        const { files_scanned, errors_found, integrity_score, validation_results } = res.data;
        addLog(`🔬 AUDIT_COMPLETE: ${files_scanned} files inspected.`);
        addLog(`🔬 INTEGRITY_SCORE: ${integrity_score}%`);
        if (errors_found.length > 0) {
          errors_found.forEach(err => addLog(`🔬 [${err.agent.toUpperCase()}]: ${err.type} in ${err.file} - ${err.message}`));
          speak(`Audit complete. I've identified ${errors_found.length} potential instabilities.`);
        } else {
          addLog("🔬 STATUS: MOLECULAR_INTEGRITY_VERIFIED.");
          speak("Audit complete, Sir. The system is architecturally sound.");
        }
        addLog(`🔬 VALIDATION: Python [${validation_results.python}], Frontend [${validation_results.frontend}]`);
        return;
      } catch { addLog("🔬 DIAGNOSTIC_FAILURE: Internal Auditor Offline."); }
    }

    // 🤖 DOMAIN_12: AUTONOMOUS_ORCHESTRATION
    if (cleanText.toLowerCase().includes("autonomous mode") || cleanText.toLowerCase().includes("activate ecosystem")) {
      addLog("🤖 ORCHESTRATOR: Activating Autonomous Orchestration Layer...");
      speak("Transitioning to autonomous ecosystem mode, Sir.");
      try {
        await api.postOrchestratorStart();
        addLog("🤖 STATUS: AUTONOMOUS_ECOSYSTEM_ONLINE");
        return;
      } catch { addLog("🤖 ORCHESTRATOR_FAILURE: Autonomous layer failed to initialize."); }
    }

    setMessages(prev => {
      const next = [...prev, { type: "user", text: cleanText }];
      return next.length > 50 ? next.slice(-50) : next;
    });
    setInterimText("");
    if (processLocalIntent(cleanText)) return;

    setIsProcessingInput(true);
    setStatus("thinking");
    try {
      const res  = await api.postJarvis(cleanText, { session_id: sessionIdRef.current });
      const data = res.data;
      setMessages(prev => [...prev, { type: "bot", text: data.response }]);
      speak(data.response);
      setStatus("idle");
    } catch { addLog("NEURAL_LINK_FAILURE"); setStatus("idle"); }
    finally { setIsProcessingInput(false); }
  }, [addLog, speak, setStatus, setMessages, processLocalIntent]);

  // ── startVoice ────────────────────────────────────────────────────────
  const startVoice = useCallback(async () => {
    startVoiceRef.current = startVoice;
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasMic  = devices.some(d => d.kind === "audioinput");
      if (!hasMic) { addLog("CRITICAL: NO_AUDIO_HARDWARE_DETECTED"); return; }
      if (navigator.mediaDevices?.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(t => t.stop());
      }
    } catch (_err) {
      console.warn("Mic warming failed", _err.message);
      reportRecovery("MIC", "WARM_UP_FAILURE", { error: _err.message });
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch { /* ignore */ }
    }

    const rec = new SpeechRecognition();
    recognitionRef.current = rec;
    rec.continuous     = true;
    rec.interimResults = true;
    rec.onstart  = () => { setStatus("listening"); addLog("VOCAL_LINK_ESTABLISHED"); };
    rec.onerror  = (e) => {
      addLog(`VOCAL_ERROR: ${e.error.toUpperCase()}`);
      reportRecovery("VOICE", "RECOGNITION_ERROR", { error: e.error });
    };
    rec.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[r.length - 1].transcript).join("");
      setInterimText(transcript);
      if (status === "speaking" && transcript.trim().length > 2) {
        console.warn("[FULL_DUPLEX] Barge-in detected. Canceling synthesis...");
        window.speechSynthesis.cancel();
        setStatus("listening");
        reportRecovery("VOICE", "BARGE_IN_DETECTED");
      }
      if (e.results[e.results.length - 1].isFinal)
        processInput(e.results[e.results.length - 1][0].transcript);
    };
    rec.start();
  }, [addLog, reportRecovery, processInput, status, setStatus]);

  useEffect(() => { startVoiceRef.current = startVoice; }, [startVoice]);

  // ── Voice Engine Watchdog ─────────────────────────────────────────────
  useEffect(() => {
    if (status === "listening" && isContinuousRef.current) {
      const watchdog = setInterval(() => {
        if (!recognitionRef.current || status !== "listening") {
          console.warn("[SELF_HEAL] Vocal Link Stalled. Restarting engine...");
          addLog("SELF_HEAL: RESTARTING_VOICE_ENGINE");
          reportRecovery("VOICE", "ENGINE_STALL_RECOVERED");
          startVoice();
        }
      }, 5000);
      return () => clearInterval(watchdog);
    }
  }, [status, startVoice, addLog, reportRecovery]);

  // ── Sonic Sentry (clap detection) ─────────────────────────────────────
  const initializeSonicSentry = useCallback(async () => {
    if (audioContextRef.current) return;
    try {
      const stream      = await navigator.mediaDevices.getUserMedia({ audio: true });
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      const audioContext = new AudioContext();
      const analyser    = audioContext.createAnalyser();
      const source      = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize  = 2048;
      analyserRef.current     = analyser;
      audioContextRef.current = audioContext;
      setSonicSentryActive(true);
      addLog("ACOUSTIC_INTELLIGENCE: ONLINE");

      const bufferLength = analyser.frequencyBinCount;
      const dataArray    = new Float32Array(bufferLength);

      const checkAcoustics = async () => {
        if (!analyserRef.current) { requestAnimationFrame(checkAcoustics); return; }
        analyserRef.current.getFloatTimeDomainData(dataArray);

        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) sum += dataArray[i] * dataArray[i];
        const rms = Math.sqrt(sum / dataArray.length) * 100;

        let zcr = 0;
        for (let i = 1; i < dataArray.length; i++) {
          if ((dataArray[i] > 0 && dataArray[i-1] < 0) || (dataArray[i] < 0 && dataArray[i-1] > 0)) zcr++;
        }

        const now = Date.now();
        if (now % 5000 < 50)
          noiseFloorRef.current = (noiseFloorRef.current * 0.9) + (rms * 0.1);

        const echoMultiplier  = status === "speaking" ? 4.5 : 1.2;
        const triggerThreshold = noiseFloorRef.current + (45 * echoMultiplier);

        if (rms > triggerThreshold && zcr > 150 && status === "idle" && now - lastClapTimeRef.current > 1500) {
          if (rms < noiseFloorRef.current * 3) { addLog("ACOUSTIC_REJECTION: AMBIENT_NOISE"); return; }
          lastClapTimeRef.current = now;
          addLog(`ACOUSTIC_TRUTH: CLAP_VERIFIED (RMS: ${rms.toFixed(1)})`);
          setIsVoiceIgnited(true);
          isContinuousRef.current = true;
          if (!sessionStorage.getItem("jarvis_greeted")) {
            speak("Acoustic calibration complete, Sir. Systems unified.");
            sessionStorage.setItem("jarvis_greeted", "true");
          } else { startVoice(); }
          setAssemblyStep(5);
        }
        requestAnimationFrame(checkAcoustics);
      };
      checkAcoustics();
    } catch (_err) {
      addLog("ACOUSTIC_LINK_ERROR");
      reportRecovery("VOICE", "ACOUSTIC_SENTRY_FAILURE", { error: _err.message });
    }
  }, [addLog, speak, startVoice, status, setAssemblyStep, reportRecovery]);

  return {
    // state
    isVoiceIgnited, interimText, activeForgeId, forgeLogs, proposedForge,
    isProcessingInput, isGhostActive, sonicSentryActive, globalResonanceUrl,
    intelSource, omegaState, acousticStats,
    // setters
    setIsVoiceIgnited, setInterimText, setActiveForgeId, setForgeLogs, setProposedForge,
    setIsProcessingInput, setIsGhostActive, setSonicSentryActive, setGlobalResonanceUrl,
    setIntelSource, setOmegaState, setAcousticStats,
    // refs
    recognitionRef, audioContextRef, analyserRef, lastClapTimeRef,
    isContinuousRef, hasInteractedRef, sessionIdRef, noiseFloorRef,
    // actions
    processInput, startVoice, initializeSonicSentry,
  };
}
