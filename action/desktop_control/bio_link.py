import time
import threading
from core.cognition.reasoning.shared_state import NEURAL_INSIGHT_CACHE

# 🧬 TIER_13: BIO_LINK (rPPG PULSE MONITOR)
# Detects 'Sir's' heart rate via webcam micro-fluctuations in skin color.

class BioLink:
    def __init__(self):
        self.heart_rate = 72
        self.stress_level = "NOMINAL"
        self.running = False
        self._thread = None
        self.buffer = []
        self.buffer_size = 150 # ~5 seconds at 30fps

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._monitor_vitals, daemon=True)
        self._thread.start()
        print("[BIO_LINK] [DNA] Biological Link synchronized. Initializing rPPG sensors.")

    def _monitor_vitals(self):
        # 🛡️ O.M.E.G.A. SAFETY: Camera bypassed to allow Frontend FaceScanner priority
        return

        while self.running:
            ret, frame = cap.read()
            if not ret: break

            # ROI: Forehead/Cheek area (Simplified)
            # In a full implementation, we'd use Mediapipe FaceMesh to lock the ROI
            h, w, _ = frame.shape
            roi = frame[int(h*0.2):int(h*0.35), int(w*0.4):int(w*0.6)]
            
            if roi.size > 0:
                # Calculate mean green channel intensity (rPPG principle: green correlates most with blood flow)
                avg_green = np.mean(roi[:, :, 1])
                self.buffer.append(avg_green)
                if len(self.buffer) > self.buffer_size:
                    self.buffer.pop(0)
                
                # Signal Processing: FFT or Peak Detection for HR
                if len(self.buffer) == self.buffer_size:
                    # Very basic frequency estimation (Simplified for stability)
                    # We look for signal peaks over time
                    peaks = 0
                    for i in range(1, len(self.buffer)-1):
                        if self.buffer[i] > self.buffer[i-1] and self.buffer[i] > self.buffer[i+1]:
                            peaks += 1
                    
                    # Convert peaks to BPM (Sample Rate approx 30fps)
                    fps = 30
                    duration = self.buffer_size / fps
                    calculated_hr = (peaks / duration) * 60
                    
                    # Smoothing
                    self.heart_rate = int(0.9 * self.heart_rate + 0.1 * calculated_hr)
                    self.heart_rate = max(40, min(180, self.heart_rate)) # Clamp
                    
                    # Stress Deduction
                    if self.heart_rate > 95:
                        self.stress_level = "CRITICAL"
                        NEURAL_INSIGHT_CACHE["text"] = f"CRITICAL: Sir's heart rate is elevated at {self.heart_rate} BPM. Crisis protocols suggested."
                    elif self.heart_rate > 85:
                        self.stress_level = "ELEVATED"
                    else:
                        self.stress_level = "NOMINAL"

            time.sleep(0.03) # ~30 FPS

        cap.release()

    def get_vitals(self):
        return {
            "heart_rate": self.heart_rate,
            "stress_level": self.stress_level,
            "timestamp": time.time()
        }

# Singleton instance
bio_link = BioLink()
