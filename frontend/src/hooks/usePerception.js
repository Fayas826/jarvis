import { useEffect, useCallback } from 'react';
import { api } from '@/services/api';

export function usePerception({ enabled = true, addLog, setVisionInsight }) {
  const refreshPerception = useCallback(async () => {
    try {
      const res = await api.getVisionAnalysis();
      if (res.data && res.data.insight) {
        if (setVisionInsight) setVisionInsight(res.data.insight);
      }
    } catch (_err) {
      if (addLog) addLog("VISION_ANALYSIS_FAILED");
    }
  }, [addLog, setVisionInsight]);

  useEffect(() => {
    if (!enabled) return undefined;
    
    // Start session on backend
    api.postPerceptionSession("start").catch(console.error);
    
    // Poll perception analysis
    const interval = setInterval(refreshPerception, 15000);
    
    return () => {
      clearInterval(interval);
      api.postPerceptionSession("stop").catch(console.error);
    };
  }, [enabled, refreshPerception]);

  return { refreshPerception };
}
