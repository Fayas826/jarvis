import { createContext, useContext } from "react";

export const UIContext = createContext();
export const BiometricContext = createContext();
export const AIContext = createContext();

export const useUI = () => useContext(UIContext);
export const useBiometrics = () => useContext(BiometricContext);
export const useAI = () => useContext(AIContext);

export const useAppState = () => {
  const ui = useUI();
  const bio = useBiometrics();
  const ai = useAI();
  
  return { 
    ...ui, 
    ...bio, 
    ...ai
  };
};
