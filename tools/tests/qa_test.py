import httpx
import asyncio
import json

async def test_jarvis(text, image_path=None):
    url = "http://localhost:5001/jarvis"
    payload = {"message": text}
    if image_path:
        payload["image_path"] = image_path
    
    headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiVG9ueSBTdGFyayJ9.TEUqF-1XLe-UQGqwYKo7KE82GpkhUTC7rQ3WJ_MQb90"} 
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # We need to know the actual auth logic.
            # Let's check api.py for verify_token.
            res = await client.post(url, json=payload, headers=headers)
            print(f"STATUS: {res.status_code}")
            print(f"RESPONSE: {json.dumps(res.json(), indent=2)}")
        except Exception as e:
            import traceback
            print(f"ERROR: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else "Jarvis open YouTube"
    asyncio.run(test_jarvis(text))
