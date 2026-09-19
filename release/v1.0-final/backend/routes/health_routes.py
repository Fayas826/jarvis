
import time
from fastapi import APIRouter
from perception.vision.vision_loop import vision_loop

router = APIRouter()

@router.get("/")
async def root():
    return {"status": "ONLINE", "core": "O.M.E.G.A. V10", "timestamp": time.time()}

@router.get("/health")
async def health():
    return {
        "status": "NOMINAL",
        "neural_link": "STABLE",
        "vision_sentinel": vision_loop.running,
        "timestamp": time.time()
    }
