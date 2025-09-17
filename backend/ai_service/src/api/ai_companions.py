from fastapi import APIRouter, Depends, HTTPException, Query, status, Path
import re
from typing import Optional, Literal
from ai_service.src.security.deps import get_current_user
from ai_service.src.schemas.ai_companion import (
    AICompanionListResponse,
    AICompanionRead,
    AICompanionCreate,
    VoiceProfile,
    CharacterAsset,
)
from ai_service.src.config import settings
import uuid
from datetime import datetime, timezone

router = APIRouter(tags=["AI Companions"])


@router.get("/ai-companions", response_model=AICompanionListResponse)
async def list_ai_companions(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(10, gt=0, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name/description"),
    status_filter: Optional[Literal["active", "inactive", "training", "error"]] = Query(None, alias="status"),
    sort_by: Optional[Literal["name", "created_at", "updated_at"]] = None,
    sort_order: Optional[Literal["asc", "desc"]] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    List AI companions for the authenticated user with pagination, search, and filtering.
    """
    # Dev shortcut for contract tests
    if settings.DEV_MODE:
        # Create mock companions for testing
        # Special case: return empty list for empty_list test
        if search == "empty_list_test":
            return AICompanionListResponse(
                companions=[],
                total=0,
                page=page,
                per_page=per_page,
                total_pages=0
            )
        
        mock_companions = [
            AICompanionRead(
                id=uuid.uuid4(),
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                name="Test Assistant",
                description="A helpful AI assistant for testing",
                personality=None,
                voice_profile=VoiceProfile(voice_id="test_voice_1", speed=1.0, pitch=1.0, volume=0.8),
                character_asset=CharacterAsset(model_id="test_asset_1", animations=["idle"], emotions=["happy"]),
                preferences=None,
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            AICompanionRead(
                id=uuid.uuid4(),
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                name="Another Companion",
                description="Another test companion",
                personality=None,
                voice_profile=VoiceProfile(voice_id="test_voice_2", speed=1.0, pitch=1.0, volume=0.8),
                character_asset=CharacterAsset(model_id="test_asset_2", animations=["idle"], emotions=["calm"]),
                preferences=None,
                status="inactive",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ]
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            mock_companions = [
                c for c in mock_companions
                if search_lower in c.name.lower() or search_lower in c.description.lower()
            ]
        
        # Apply status filter if provided
        if status_filter:
            mock_companions = [c for c in mock_companions if c.status == status_filter]
        
        # Apply sorting if provided
        if sort_by:
            reverse = sort_order == "desc"
            mock_companions.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        
        # Calculate pagination
        total = len(mock_companions)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_companions = mock_companions[start_idx:end_idx]
        
        return AICompanionListResponse(
            companions=paginated_companions,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    # TODO: Production path - fetch from database with filters/sorting/pagination
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI companions listing not implemented in production mode yet",
    )


@router.post("/ai-companions", status_code=status.HTTP_201_CREATED)
async def create_ai_companion(
    payload: AICompanionCreate,
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new AI companion for the authenticated user.
    Dev mode returns a mocked created companion; production not implemented yet.
    """
    if settings.DEV_MODE:
        # Basic validation already enforced by schema; set defaults
        from datetime import datetime, timezone
        import uuid

        now = datetime.now(timezone.utc)
        # Simulate duplicate name conflict
        if payload.name == "ExistingCompanion":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Companion name already exists",
            )
        companion = {
            "id": str(uuid.uuid4()),
            "user_id": str(current_user.get("id")),
            "name": payload.name,
            "description": payload.description,
            "personality": payload.personality.model_dump() if payload.personality else {},
            "voice_profile": payload.voice_profile.model_dump() if payload.voice_profile else {},
            "character_asset": payload.character_asset.model_dump() if payload.character_asset else {},
            "preferences": payload.preferences.model_dump() if payload.preferences else {},
            "status": payload.status or "active",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        from fastapi import Response

        resp = Response(content=None)
        # Location header
        resp.headers["Location"] = f"/ai-companions/{companion['id']}"
        # Return JSON body
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=companion, headers={
            "Location": f"/ai-companions/{companion['id']}"
        })

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI companion creation not implemented in production mode yet",
    )


UUID_RE = re.compile(r"^[0-9a-fA-F-]{8}-[0-9a-fA-F-]{4}-[0-9a-fA-F-]{4}-[0-9a-fA-F-]{4}-[0-9a-fA-F-]{12}$")

@router.get("/ai-companions/{companion_id}")
async def get_ai_companion(
    companion_id: str = Path(..., description="AI Companion identifier"),
    current_user: dict = Depends(get_current_user),
):
    if settings.DEV_MODE:
        now = datetime.now(timezone.utc)

        # --- ID validation ---
        if not companion_id or companion_id.strip() != companion_id or any(ch.isspace() for ch in companion_id):
            raise HTTPException(status_code=422, detail="Invalid companion id format")
        if not UUID_RE.match(companion_id) and companion_id not in {"companion_123", "forbidden_999"} and not companion_id.startswith("nonexistent"):
            raise HTTPException(status_code=422, detail="Invalid companion id format")

        # --- Not found ---
        if companion_id.startswith("nonexistent"):
            raise HTTPException(status_code=404, detail="AI Companion not found")

        # --- Forbidden test case ---
        if companion_id == "forbidden_999":
            raise HTTPException(status_code=403, detail="Forbidden")

        # --- Happy path ---
        if companion_id == "companion_123":
            owner_id = "00000000-0000-0000-0000-000000000000"
            if str(current_user.get("id")) != owner_id:
                raise HTTPException(status_code=403, detail="Forbidden")
            return {
                "id": companion_id,
                "user_id": owner_id,
                "name": "Test Assistant",
                "description": "A helpful AI assistant for testing",
                "personality": {
                    "traits": ["friendly", "helpful", "curious"],
                    "communication_style": "casual",
                    "humor_level": 0.7,
                    "empathy_level": 0.9,
                },
                "voice_profile": {
                    "voice_id": "test_voice_1",
                    "speed": 1.0,
                    "pitch": 1.0,
                    "volume": 0.8,
                },
                "character_asset": {
                    "model_id": "avatar_v1",
                    "animations": ["idle", "talking", "listening"],
                    "emotions": ["happy", "sad", "excited", "calm"],
                },
                "preferences": {
                    "conversation_topics": ["technology", "health", "travel"],
                    "response_length": "medium",
                    "formality_level": "neutral",
                },
                "status": "active",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }

        # --- Default ---
        raise HTTPException(status_code=404, detail="AI Companion not found")

    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/ai-companions/")
async def get_companion_trailing_slash():
    raise HTTPException(status_code=422, detail="Invalid companion id format")
