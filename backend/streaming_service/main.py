"""
Holo-Mate Streaming Service
Real-time voice processing and WebSocket handling
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from streaming_service.src.api import streaming, devices
from shared.src.db.session import lifespan_manager

app = FastAPI(
    title="Holo-Mate Streaming Service",
    description="Handles device streaming sessions for the Holo-Mate platform",
    version="1.0.0",
    lifespan=lifespan_manager
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Holo-Mate Streaming Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "streaming_service"}

# Routers
app.include_router(streaming.router, prefix="/streaming")
app.include_router(devices.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
