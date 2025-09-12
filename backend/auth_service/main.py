"""
Holo-Mate Auth Service
Authentication and user management service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Assuming your API routers are in app.api
from app.api import auth, users

app = FastAPI(
    title="Holo-Mate Auth Service",
    description="Authentication and user management for Holo-Mate platform",
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

# Include API routers
app.include_router(auth.router, prefix="/auth")
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Holo-Mate Auth Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth_service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


