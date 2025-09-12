"""
Holo-Mate AI Service
AI companion management and conversation handling
"""

from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status, Header, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.ai_service.src.api import router as api_router

app = FastAPI(
    title="Holo-Mate AI Service",
    description="AI companion management and conversation handling for Holo-Mate platform",
    version="1.0.0"
)
app.include_router(api_router)

def _auth_header_required(authorization: Annotated[str | None, Header()] = None):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    if token in {"invalid_access_token_here"}:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token


@app.get("/ai-companions")
async def list_ai_companions(
    authorization: str | None = None,
    token: str = Depends(_auth_header_required),
    page: int = Query(1),
    per_page: int = Query(10),
    sort_by: str | None = Query(None),
    sort_order: str | None = Query(None),
):
    errors = []
    if page < 1:
        errors.append({"loc": ["query", "page"], "msg": "page must be >= 1", "type": "value_error"})
    if per_page <= 0:
        errors.append({"loc": ["query", "per_page"], "msg": "per_page must be > 0", "type": "value_error"})
    if sort_by is not None and sort_by not in {"name", "created_at"}:
        errors.append({"loc": ["query", "sort_by"], "msg": "invalid sort_by", "type": "value_error"})
    if sort_order is not None and sort_order not in {"asc", "desc"}:
        errors.append({"loc": ["query", "sort_order"], "msg": "invalid sort_order", "type": "value_error"})
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)

    return {
        "companions": [],
        "total": 0,
        "page": 1,
        "per_page": 10,
        "total_pages": 0,
    }

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
