import time
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# 5-Tier SaaS Billing Ledger
# In a true enterprise setup, this will hit Redis for token buckets and MongoDB for Stripe data.
TIER_LIMITS = {
    "L0_FREE": {"daily_tokens": 50000, "requests_per_min": 10},
    "L1_PRO": {"daily_tokens": 1000000, "requests_per_min": 60},
    "L2_BUSINESS": {"daily_tokens": 5000000, "requests_per_min": 300},
    "L3_ADMIN": {"daily_tokens": float('inf'), "requests_per_min": float('inf')},
    "L4_SUPERADMIN": {"daily_tokens": float('inf'), "requests_per_min": float('inf')}
}

# Temporary In-Memory store for demonstration. Will be swapped with Redis.
usage_store = {}

async def saas_rate_limiter_middleware(request: Request, call_next):
    # Extract API Key or Client ID from headers
    client_id = request.headers.get("X-Client-ID", "anonymous")
    client_tier = request.headers.get("X-Client-Tier", "L0_FREE")

    if client_tier not in TIER_LIMITS:
        client_tier = "L0_FREE"
    
    limits = TIER_LIMITS[client_tier]
    
    # SuperAdmin Bypass
    if client_tier in ["L3_ADMIN", "L4_SUPERADMIN"]:
        response = await call_next(request)
        return response

    current_time = time.time()
    
    # Initialize store for client
    if client_id not in usage_store:
        usage_store[client_id] = {
            "tokens_used_today": 0,
            "requests_this_minute": 0,
            "minute_start_time": current_time
        }
        
    client_data = usage_store[client_id]
    
    # Reset minute counter
    if current_time - client_data["minute_start_time"] > 60:
        client_data["requests_this_minute"] = 0
        client_data["minute_start_time"] = current_time

    # Check Rate Limits
    if client_data["requests_this_minute"] >= limits["requests_per_min"]:
        return JSONResponse(
            status_code=429,
            content={"error": "Too Many Requests. Please upgrade your SaaS plan for higher limits."}
        )
        
    # Check Token Limits (Assuming each request costs ~500 tokens on average for this mock)
    if client_data["tokens_used_today"] + 500 > limits["daily_tokens"]:
        return JSONResponse(
            status_code=402,
            content={"error": "Payment Required. Daily token limit exceeded for your tier."}
        )

    # Increment Usage
    client_data["requests_this_minute"] += 1
    client_data["tokens_used_today"] += 500
    
    response = await call_next(request)
    
    # Append remaining tokens to response headers for the Frontend HUD
    response.headers["X-Tokens-Remaining"] = str(limits["daily_tokens"] - client_data["tokens_used_today"])
    return response
