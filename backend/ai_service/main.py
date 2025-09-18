"""
Holo-Mate AI Service
AI companion management and conversation handling
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ai_service.src.exceptions import AppError, app_error_handler
import uvicorn

# Local imports (absolute from ai_service package)
from ai_service.src.exceptions import AppError, app_error_handler
from ai_service.src.api import ai_companions, conversations, messages

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

# Exception handlers
app.add_exception_handler(AppError, app_error_handler)

@app.get("/")
async def root():
    return {"message": "Holo-Mate AI Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai_service"}

# Routers
app.include_router(ai_companions.router)
app.include_router(conversations.router)
app.include_router(messages.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
