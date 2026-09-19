import os
import json

TRAINING_LAB_DIR = r"c:\jarvis AI\jarvis\training_lab"
FILENAME = "advanced_defensive_cybersecurity.jsonl"

def build_defensive_dataset():
    print("Generating advanced defensive cybersecurity dataset...")
    filepath = os.path.join(TRAINING_LAB_DIR, FILENAME)
    
    defensive_data = [
        {"instruction": "Analyze this access log for potential brute-force attacks: [Login failed for user 'admin' from IP 192.168.1.50] x 50 in 1 minute.", "response": "High probability of brute-force attack detected from IP 192.168.1.50 targeting the 'admin' account. Recommended action: Automatically block the IP address at the firewall and alert the system administrator."},
        {"instruction": "Audit the following code snippet for vulnerabilities: `query = 'SELECT * FROM users WHERE username = ' + user_input`", "response": "Critical Vulnerability Detected: SQL Injection. The user input is concatenated directly into the SQL query. Recommended action: Use parameterized queries or prepared statements to sanitize inputs and prevent arbitrary SQL execution."},
        {"instruction": "Review the network traffic for anomalies: High volume of outbound traffic on port 53 to an unknown external IP.", "response": "Anomaly Detected: Potential DNS Tunneling or data exfiltration. Port 53 is typically used for DNS requests, but the high volume suggests it is being abused to bypass firewall restrictions. Recommended action: Isolate the affected endpoint and inspect DNS payload content."},
        {"instruction": "Evaluate the current firewall configuration: ALLOW TCP ANY TO ANY PORT 22.", "response": "Security Risk: Open SSH port to the entire internet. This exposes the system to automated SSH brute-force campaigns. Recommended action: Restrict Port 22 access to specific, trusted IP addresses or require VPN access for administrative connections."},
        {"instruction": "Analyze the file hash against known threat intelligence databases.", "response": "Hash analysis complete. The file matches a known signature for ransomware (CryptoLocker variant). Recommended action: Immediately quarantine the file, terminate associated processes, and initiate an offline backup restoration protocol."}
    ]
    
    with open(filepath, "w", encoding="utf-8") as f:
        for _ in range(1000):
            for sample in defensive_data:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                
    size_kb = round(os.path.getsize(filepath) / 1024, 2)
    print(f"[OK] Generated: {FILENAME} | Size: {size_kb} KB")

if __name__ == "__main__":
    build_defensive_dataset()
