"""
Holo-Mate AI Service
AI companion management and conversation handling
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Holo-Mate AI Service",
    description="AI companion management and conversation handling for Holo-Mate platform",
    version="1.0.0"
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
    return {"message": "Holo-Mate AI Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai_service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
