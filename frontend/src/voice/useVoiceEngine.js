import { useState, useRef, useCallback, useEffect } from 'react';
import { api } from '@/services/api';

export function useVoiceEngine({ 
  addLog, 
  speak, 
  status, 
  setStatus, 
  isInitialized,
  reportRecovery,
  processInput,
  setSystemCoherence,
  setAssemblyStep
}) {
  const [isVoiceIgnited, setIsVoiceIgnited] = useState(false);
  const [interimText, setInterimText] = useState("");
  const [_sonicSentryActive, setSonicSentryActive] = useState(false);
  
  const recognitionRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const lastClapTimeRef = useRef(0);
  const isContinuousRef = useRef(false);
  const startVoiceRef = useRef(null);
  const noiseFloorRef = useRef(30);
  const truthAuditRef = useRef({ lastCheck: 0, failures: 0 });

  const verifyMultimodalTruth = useCallback(async () => {
    const now = Date.now();
    if (now - truthAuditRef.current.lastCheck < 5000) return true;
    truthAuditRef.current.lastCheck = now;

    let truths = { audio: true, ui: true, backend: true, device: true, memory: true };

    try { await api.getHealth(); } catch { truths.backend = false; }
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        truths.device = devices.some(d => d.kind === 'audioinput') && !!audioContextRef.current;
    } catch { truths.device = false; }
    try {
        const mres = await api.getMemoryIntegrity();
        truths.memory = mres.data.status !== "CORRUPTED";
    } catch { truths.memory = false; }

    truths.ui = !!analyserRef.current && isInitialized;

    const score = Object.values(truths).filter(Boolean).length * 20; 
    
    if (setSystemCoherence) {
      setSystemCoherence(prev => ({
          ...prev,
          backendTruth: truths.backend ? 100 : 0,
          deviceTruth: truths.device ? 100 : 0,
          memoryTruth: truths.memory ? 100 : 0,
          uiTruth: truths.ui ? 100 : 0,
          coherenceScore: score
      }));
    }

    if (score < 50) {
        if (addLog) addLog("MULTIMODAL_TRUTH_FAILURE: COHERENCE_LOW");
        if (reportRecovery) reportRecovery("SYSTEM", "COHERENCE_CRITICAL", { score, truths });
        return false;
    }
    return true;
  }, [isInitialized, addLog, reportRecovery, setSystemCoherence]);

  const startVoice = useCallback(async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const hasMic = devices.some(d => d.kind === 'audioinput');
      if (!hasMic) {
        if (addLog) addLog("CRITICAL: NO_AUDIO_HARDWARE_DETECTED");
        if (reportRecovery) reportRecovery("MIC", "HARDWARE_DISCONNECT");
        return;
      }
      
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        stream.getTracks().forEach(t => t.stop());
      }
    } catch (err) { 
      console.warn("Mic warming failed", err); 
      if (reportRecovery) reportRecovery("MIC", "WARM_UP_FAILURE", { error: err.message });
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    
    if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch { /* Ignore stop error */ }
    }

    const rec = new SpeechRecognition();
    recognitionRef.current = rec;
    rec.continuous = true;
    rec.interimResults = true;
    rec.onstart = () => { if (setStatus) setStatus("listening"); if (addLog) addLog("VOCAL_LINK_ESTABLISHED"); };
    rec.onerror = (e) => {
        if (addLog) addLog(`VOCAL_ERROR: ${e.error.toUpperCase()}`);
        if (reportRecovery) reportRecovery("VOICE", "RECOGNITION_ERROR", { error: e.error });
    };
    rec.onresult = (e) => {
      const transcript = Array.from(e.results).map(r => r[r.length-1].transcript).join("");
      setInterimText(transcript);
      
      if (status === "speaking" && transcript.trim().length > 2) {
          console.warn("[FULL_DUPLEX] User interrupted. Canceling synthesis...");
          window.speechSynthesis.cancel();
          if (setStatus) setStatus("listening");
          if (reportRecovery) reportRecovery("VOICE", "BARGE_IN_DETECTED");
      }

      if (e.results[e.results.length - 1].isFinal && processInput) {
        processInput(e.results[e.results.length - 1][0].transcript);
      }
    };
    rec.start();
  }, [addLog, reportRecovery, processInput, setStatus, status]);

  useEffect(() => {
    startVoiceRef.current = startVoice;
  }, [startVoice]);

  const initializeSonicSentry = async () => {
    if (audioContextRef.current) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 2048; 
      analyserRef.current = analyser;
      audioContextRef.current = audioContext;
      setSonicSentryActive(true);
      if (addLog) addLog("ACOUSTIC_INTELLIGENCE: ONLINE");

      // Set up WebSocket for C++ accelerated binary streaming
      const ws = new WebSocket("ws://localhost:8000/stream/audio");
      ws.binaryType = "arraybuffer";
      ws.onopen = () => { if (import.meta.env.DEV) console.log("[AudioStream] Binary WebSocket connected."); };
      ws.onmessage = (msg) => {
          try {
              const data = JSON.parse(msg.data);
              if (data.type === "audio_metrics" && data.is_voice) {
                  // The C++ engine detected voice activity at low latency
                  // Future: Trigger high-speed local processing here
              }
          } catch {
              // Ignore parse errors on binary WS messages
          }
      };
      
      // Capture raw PCM using ScriptProcessor (legacy but reliable for raw stream)
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      source.connect(processor);
      processor.connect(audioContext.destination);
      processor.onaudioprocess = (e) => {
          if (ws.readyState === WebSocket.OPEN) {
              const inputData = e.inputBuffer.getChannelData(0);
              // Convert Float32 to Int16 for C++ engine
              const pcm16 = new Int16Array(inputData.length);
              for (let i = 0; i < inputData.length; i++) {
                  let s = Math.max(-1, Math.min(1, inputData[i]));
                  pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
              }
              ws.send(pcm16.buffer);
          }
      };

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Float32Array(bufferLength);
      
      const checkAcoustics = async () => {
        if (!analyserRef.current) { requestAnimationFrame(checkAcoustics); return; }
        analyserRef.current.getFloatTimeDomainData(dataArray);
        
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i] * dataArray[i];
        }
        const rms = Math.sqrt(sum / dataArray.length) * 100;
        
        let zcr = 0;
        for (let i = 1; i < dataArray.length; i++) {
          if ((dataArray[i] > 0 && dataArray[i-1] < 0) || (dataArray[i] < 0 && dataArray[i-1] > 0)) {
            zcr++;
          }
        }
        
        const now = Date.now();
        
        if (now % 5000 < 50) { 
            const currentFloor = rms;
            noiseFloorRef.current = (noiseFloorRef.current * 0.9) + (currentFloor * 0.1);
        }

        const echoMultiplier = status === "speaking" ? 4.5 : 1.2;
        const triggerThreshold = noiseFloorRef.current + (45 * echoMultiplier);

        if (rms > triggerThreshold && zcr > 150 && status === "idle" && now - lastClapTimeRef.current > 1500) {
          const isTruthValid = await verifyMultimodalTruth();
          if (!isTruthValid) {
              if (addLog) addLog("ACOUSTIC_IGNITION_ABORTED: TRUTH_AUDIT_FAILED");
              return;
          }

          lastClapTimeRef.current = now;
          
          if (rms < noiseFloorRef.current * 3) {
              if (addLog) addLog("ACOUSTIC_REJECTION: AMBIENT_NOISE_DETECTED");
              return;
          }

          if (addLog) addLog(`ACOUSTIC_TRUTH: CLAP_VERIFIED (RMS: ${rms.toFixed(1)})`);
          setIsVoiceIgnited(true);
          isContinuousRef.current = true;
          
          if (!sessionStorage.getItem("jarvis_greeted")) {
            if (speak) speak("Acoustic calibration complete, Sir. Systems unified.");
            sessionStorage.setItem("jarvis_greeted", "true");
          } else { 
            startVoice(); 
          }
          if (setAssemblyStep) setAssemblyStep(5);
        }

        requestAnimationFrame(checkAcoustics);
      };
      
      checkAcoustics();
    } catch (err) { 
      if (addLog) addLog("ACOUSTIC_LINK_ERROR"); 
      if (reportRecovery) reportRecovery("VOICE", "ACOUSTIC_SENTRY_FAILURE", { error: err.message });
    }
  };

  useEffect(() => {
    if (status === "listening" && isContinuousRef.current) {
        const watchdog = setInterval(() => {
            if (!recognitionRef.current || (recognitionRef.current && status !== "listening")) {
                console.warn("[SELF_HEAL] Vocal Link Stalled. Restarting engine...");
                if (addLog) addLog("SELF_HEAL: RESTARTING_VOICE_ENGINE");
                if (reportRecovery) reportRecovery("VOICE", "ENGINE_STALL_RECOVERED");
                startVoice();
            }
        }, 5000);
        return () => clearInterval(watchdog);
    }
  }, [status, startVoice, addLog, reportRecovery]);

  return {
    isVoiceIgnited,
    interimText,
    _sonicSentryActive,
    recognitionRef,
    audioContextRef,
    analyserRef,
    lastClapTimeRef,
    isContinuousRef,
    startVoiceRef,
    startVoice,
    initializeSonicSentry,
    verifyMultimodalTruth,
    setIsVoiceIgnited,
    setInterimText,
    setSonicSentryActive
  };
}
