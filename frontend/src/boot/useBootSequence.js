import { useState, useCallback } from 'react';

export function useBootSequence({ addLog, playSound, initializeSonicSentry, fetchGeo, fetchBio, fetchIot, speak }) {
  const [showStartup, setShowStartup] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [assemblyStep, setAssemblyStep] = useState(0);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isIgniting, setIsIgniting] = useState(false);

  const initializeSystem = useCallback(() => {
    setIsIgniting(true);
    setShowStartup(true);
    if (playSound) playSound('start');
    if (initializeSonicSentry) initializeSonicSentry();
  }, [playSound, initializeSonicSentry]);

  const handleLogoComplete = useCallback(() => {
    setShowStartup(false);
    if (addLog) addLog("IGNITION_HANDSHAKE_COMPLETE");
    setTimeout(() => {
      setIsScanning(true);
    }, 100);
  }, [addLog]);

  const handleVerify = useCallback((data, setBiometricData) => {
    if (setBiometricData) setBiometricData(data);
    setTimeout(() => {
      setIsScanning(false);
      setAssemblyStep(5);
    }, 500); 
    if (fetchGeo) fetchGeo();
    if (fetchBio) fetchBio();
    if (fetchIot) fetchIot();
    if (speak) speak("Welcome back, Sir.");
  }, [fetchGeo, fetchBio, fetchIot, speak]);

  const handleAssemblyComplete = useCallback(() => {
    setIsInitialized(true);
    if (addLog) addLog("MOLECULAR_INTEGRITY_VERIFIED");
  }, [addLog]);

  return {
    showStartup,
    isScanning,
    assemblyStep,
    isInitialized,
    isIgniting,
    setShowStartup,
    setIsScanning,
    setAssemblyStep,
    setIsInitialized,
    setIsIgniting,
    initializeSystem,
    handleLogoComplete,
    handleVerify,
    handleAssemblyComplete
  };
}
