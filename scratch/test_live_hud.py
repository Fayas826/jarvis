import urllib.request
import json
import time

def test_endpoint(url, payload=None):
    print(f"\n==================================================")
    print(f"TESTING ENDPOINT: {url}")
    print(f"==================================================")
    try:
        if payload:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        else:
            req = urllib.request.Request(url)
        
        start_t = time.time()
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            content_type = response.headers.get('Content-Type')
            content_length = response.headers.get('Content-Length')
            body = response.read().decode('utf-8', errors='ignore')
            elapsed = (time.time() - start_t) * 1000
            
            print(f"STATUS CODE: {status}")
            print(f"CONTENT TYPE: {content_type}")
            print(f"CONTENT LENGTH: {content_length} bytes")
            print(f"ELAPSED TIME: {elapsed:.2f} ms")
            print(f"RESPONSE BODY SNIPPET (First 300 chars):\n{body[:300]}")
            return True, body
    except Exception as e:
        print(f"ERROR CONNECTING: {e}")
        return False, str(e)

if __name__ == "__main__":
    print("STARTING COMPREHENSIVE LIVE HUD SERVER VERIFICATION...\n")
    
    # Test 1: Fetch Metrics
    test_endpoint("http://localhost:8092/api/v1/metrics")
    
    # Test 2: Fetch Tasks
    test_endpoint("http://localhost:8092/api/v1/tasks")
    
    # Test 3: Post Deep Search Command (YouTube)
    test_endpoint("http://localhost:8092/api/v1/tasks", {"command": "search Iron Man Mark 85 on YouTube"})
    
    # Test 4: Post Deep Search Command (Google)
    test_endpoint("http://localhost:8092/api/v1/tasks", {"command": "search Quantum Computing on Google"})
    
    # Test 5: Post Win32 Desktop Command (Lock Workstation Check)
    test_endpoint("http://localhost:8092/api/v1/tasks", {"command": "status"})
    
    # Test 6: Cloudflare Tunnel Telemetry Check
    test_endpoint("https://throws-anthony-supervision-drive.trycloudflare.com/api/v1/metrics")
    
    # Test 7: Cloudflare Tunnel Deep Command Check
    test_endpoint("https://throws-anthony-supervision-drive.trycloudflare.com/api/v1/tasks", {"command": "search Python on Google"})
