import numpy as np

_sklearn_threat_model = None

def analyze_threat_from_vitals(cpu: float, gpu: float, memory: float, processes: int = 0) -> dict:
    global _sklearn_threat_model
    try:
        from sklearn.ensemble import IsolationForest
        if _sklearn_threat_model is None:
            normal_data = np.array([
                [15, 10, 40, 0.3], [20, 15, 50, 0.4], [25, 20, 55, 0.5],
                [30, 25, 60, 0.5], [10, 5, 35, 0.2], [18, 12, 45, 0.35],
                [22, 18, 52, 0.45], [28, 22, 58, 0.55], [12, 8, 38, 0.25],
                [35, 30, 62, 0.6], [40, 35, 65, 0.65], [5, 3, 30, 0.15],
            ])
            _sklearn_threat_model = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
            _sklearn_threat_model.fit(normal_data)
        
        proc_norm = min(processes / 200.0, 1.0) if processes > 0 else 0.5
        sample = np.array([[cpu, gpu, memory, proc_norm]])
        prediction = _sklearn_threat_model.predict(sample)[0]
        anomaly_score = float(_sklearn_threat_model.score_samples(sample)[0])
        
        if prediction == -1:
            if anomaly_score < -0.5:
                threat = "CRITICAL"
                reason = f"Severe anomaly: CPU={cpu:.0f}% GPU={gpu:.0f}% MEM={memory:.0f}%"
            else:
                threat = "ELEVATED"
                reason = f"Elevated signatures: CPU={cpu:.0f}% GPU={gpu:.0f}% MEM={memory:.0f}%"
        else:
            if cpu > 90 or gpu > 90 or memory > 90:
                threat = "ELEVATED"
                reason = f"High load detected — resources near saturation"
            else:
                threat = "NOMINAL"
                reason = "All systems operating within normal parameters"
        
        return {
            "threat_level": threat,
            "anomaly_score": round(anomaly_score, 4),
            "vitals": {"cpu": cpu, "gpu": gpu, "memory": memory},
            "reason": reason
        }
    except ImportError:
        return {"threat_level": "NOMINAL", "anomaly_score": 0.0, "reason": "sklearn unavailable"}
    except Exception as e:
        return {"threat_level": "NOMINAL", "anomaly_score": 0.0, "reason": str(e)}

def get_threat_analyzer_status() -> str:
    return "ONLINE" if _sklearn_threat_model is not None else "STANDBY"
