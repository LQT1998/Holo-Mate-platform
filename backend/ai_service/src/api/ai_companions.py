from fastapi import APIRouter, Depends, HTTPException, Query, status, Path, Response
from typing import Optional, Literal
import uuid
from datetime import datetime, timezone

from ai_service.src.security.deps import get_current_user
from ai_service.src.schemas.ai_companion import (
    AICompanionListResponse,
    AICompanionRead,
    AICompanionCreate,
    AICompanionUpdate,
    DeleteResponse,
    VoiceProfile,
    CharacterAsset,
)
from ai_service.src.config import settings
from backend.shared.src.constants import (
    DEV_KNOWN_COMPANION_ID,
    DEV_FORBIDDEN_ID,
    DEV_NONEXISTENT_PREFIX,
    DEV_OWNER_ID,
)

router = APIRouter(tags=["AI Companions"])


def normalize_companion_id(companion_id: str) -> uuid.UUID:
    """
    Normalize companion_id to UUID.

    - DEV: map arbitrary id to stable UUID5 using namespace + id text
    - PROD: require valid UUID; invalid -> 422
    """
    if not companion_id or companion_id.strip() != companion_id or any(
        ch.isspace() for ch in companion_id
    ):
        raise HTTPException(status_code=422, detail="Invalid companion id format")

    if settings.DEV_MODE:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"dev:ai-companion:{companion_id}")

    try:
        return uuid.UUID(companion_id)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid companion id format")


@router.get("/ai-companions", response_model=AICompanionListResponse)
async def list_ai_companions(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(10, gt=0, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name/description"),
    status_filter: Optional[Literal["active", "inactive", "training", "error"]] = Query(
        None, alias="status"
    ),
    sort_by: Optional[Literal["name", "created_at", "updated_at"]] = None,
    sort_order: Optional[Literal["asc", "desc"]] = None,
    current_user: dict = Depends(get_current_user),
):
    """
    List AI companions for the authenticated user with pagination, search, and filtering.
    """
    if settings.DEV_MODE:
        if search == "empty_list_test":
            return AICompanionListResponse(
                companions=[], total=0, page=page, per_page=per_page, total_pages=0
            )

        mock_companions = [
            AICompanionRead(
                id=uuid.uuid4(),
                user_id=uuid.UUID(str(DEV_OWNER_ID)),
                name="Test Assistant",
                description="A helpful AI assistant for testing",
                personality=None,
                voice_profile=VoiceProfile(
                    voice_id="test_voice_1", speed=1.0, pitch=1.0, volume=0.8
                ),
                character_asset=CharacterAsset(
                    model_id="test_asset_1", animations=["idle"], emotions=["happy"]
                ),
                preferences=None,
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
            AICompanionRead(
                id=uuid.uuid4(),
                user_id=uuid.UUID(str(DEV_OWNER_ID)),
                name="Another Companion",
                description="Another test companion",
                personality=None,
                voice_profile=VoiceProfile(
                    voice_id="test_voice_2", speed=1.0, pitch=1.0, volume=0.8
                ),
                character_asset=CharacterAsset(
                    model_id="test_asset_2", animations=["idle"], emotions=["calm"]
                ),
                preferences=None,
                status="inactive",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            ),
        ]

        if search:
            search_lower = search.lower()
            mock_companions = [
                c
                for c in mock_companions
                if search_lower in (c.name or "").lower()
                or search_lower in (c.description or "").lower()
            ]

        if status_filter:
            mock_companions = [c for c in mock_companions if c.status == status_filter]

        if sort_by:
            reverse = sort_order == "desc"
            mock_companions.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)

        total = len(mock_companions)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated = mock_companions[start_idx:end_idx]

        return AICompanionListResponse(
            companions=paginated,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/ai-companions", response_model=AICompanionRead, status_code=status.HTTP_201_CREATED
)
async def create_ai_companion(
    response: Response,
    payload: AICompanionCreate,
    current_user: dict = Depends(get_current_user),
):
    if settings.DEV_MODE:
        now = datetime.now(timezone.utc)

        if payload.name == "ExistingCompanion":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Companion name already exists",
            )

        companion_id = uuid.uuid4()
        companion = AICompanionRead(
            id=companion_id,
            user_id=uuid.UUID(str(current_user["id"])),
            name=payload.name,
            description=payload.description,
            personality=payload.personality,
            voice_profile=payload.voice_profile,
            character_asset=payload.character_asset,
            preferences=payload.preferences,
            status=payload.status or "active",
            created_at=now,
            updated_at=now,
        )

        response.headers["Location"] = f"/ai-companions/{companion_id}"
        return companion

    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/ai-companions/{companion_id}", response_model=AICompanionRead)
async def get_ai_companion(
    companion_id: str, current_user: dict = Depends(get_current_user)
):
    if settings.DEV_MODE:
        now = datetime.now(timezone.utc)
        normalized_id = normalize_companion_id(companion_id)

        if companion_id.startswith(DEV_NONEXISTENT_PREFIX):
            raise HTTPException(status_code=404, detail="AI Companion not found")

        if companion_id == DEV_FORBIDDEN_ID:
            raise HTTPException(status_code=403, detail="Forbidden")

        if companion_id == DEV_KNOWN_COMPANION_ID:
            owner_uuid = uuid.UUID(str(DEV_OWNER_ID))
            if uuid.UUID(str(current_user["id"])) != owner_uuid:
                raise HTTPException(status_code=403, detail="Forbidden")

            return AICompanionRead(
                id=normalized_id,
                user_id=owner_uuid,
                name="Test Assistant",
                description="A helpful AI assistant for testing",
                personality={
                    "traits": ["friendly", "helpful", "curious"],
                    "communication_style": "casual",
                    "humor_level": 0.7,
                    "empathy_level": 0.9,
                },
                voice_profile=VoiceProfile(
                    voice_id="test_voice_1", speed=1.0, pitch=1.0, volume=0.8
                ),
                character_asset=CharacterAsset(
                    model_id="avatar_v1",
                    animations=["idle", "talking", "listening"],
                    emotions=["happy", "sad", "excited", "calm"],
                ),
                preferences={
                    "conversation_topics": ["technology", "health", "travel"],
                    "response_length": "medium",
                    "formality_level": "neutral",
                },
                status="active",
                created_at=now,
                updated_at=now,
            )

        raise HTTPException(status_code=404, detail="AI Companion not found")

    raise HTTPException(status_code=501, detail="Not implemented")


@router.put("/ai-companions/{companion_id}", response_model=AICompanionRead)
async def update_ai_companion(
    companion_id: str,
    payload: AICompanionUpdate,
    current_user: dict = Depends(get_current_user),
):
    if settings.DEV_MODE:
        now = datetime.now(timezone.utc)
        normalized_id = normalize_companion_id(companion_id)

        if companion_id.startswith(DEV_NONEXISTENT_PREFIX):
            raise HTTPException(status_code=404, detail="AI Companion not found")

        if companion_id == DEV_FORBIDDEN_ID:
            raise HTTPException(status_code=403, detail="Forbidden")

        if companion_id == DEV_KNOWN_COMPANION_ID:
            owner_uuid = uuid.UUID(str(DEV_OWNER_ID))
            if uuid.UUID(str(current_user["id"])) != owner_uuid:
                raise HTTPException(status_code=403, detail="Forbidden")

            update_data = payload.model_dump(exclude_unset=True)

            forbidden = {"id", "user_id", "created_at", "updated_at"}
            if forbidden & update_data.keys():
                raise HTTPException(
                    status_code=400,
                    detail="Updating id, user_id, created_at, or updated_at is not allowed",
                )

            if not update_data:
                raise HTTPException(
                    status_code=422,
                    detail="At least one field must be provided for update",
                )

            return AICompanionRead(
                id=normalized_id,
                user_id=owner_uuid,
                name=update_data.get("name", "Test Assistant"),
                description=update_data.get(
                    "description", "A helpful AI assistant for testing"
                ),
                personality=update_data.get(
                    "personality",
                    {
                        "traits": ["friendly", "helpful", "curious"],
                        "communication_style": "casual",
                        "humor_level": 0.7,
                        "empathy_level": 0.9,
                    },
                ),
                voice_profile=update_data.get(
                    "voice_profile",
                    {"voice_id": "test_voice_1", "speed": 1.0, "pitch": 1.0, "volume": 0.8},
                ),
                character_asset=update_data.get(
                    "character_asset",
                    {
                        "model_id": "avatar_v1",
                        "animations": ["idle", "talking", "listening"],
                        "emotions": ["happy", "sad", "excited", "calm"],
                    },
                ),
                preferences=update_data.get(
                    "preferences",
                    {
                        "conversation_topics": ["technology", "health", "travel"],
                        "response_length": "medium",
                        "formality_level": "neutral",
                    },
                ),
                status=update_data.get("status", "active"),
                created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
                updated_at=now,
            )

        raise HTTPException(status_code=404, detail="AI Companion not found")

    raise HTTPException(status_code=501, detail="Not implemented")


@router.delete("/ai-companions/{companion_id}", response_model=DeleteResponse)
async def delete_ai_companion(
    companion_id: str, current_user: dict = Depends(get_current_user)
):
    if settings.DEV_MODE:
        normalized_id = normalize_companion_id(companion_id)

        if companion_id.startswith(DEV_NONEXISTENT_PREFIX):
            raise HTTPException(status_code=404, detail="AI Companion not found")

        if companion_id == DEV_FORBIDDEN_ID:
            raise HTTPException(status_code=403, detail="Forbidden")

        if companion_id == DEV_KNOWN_COMPANION_ID:
            owner_uuid = uuid.UUID(str(DEV_OWNER_ID))
            if uuid.UUID(str(current_user["id"])) != owner_uuid:
                raise HTTPException(status_code=403, detail="Forbidden")

            return DeleteResponse(
                message="AI Companion deleted successfully", deleted_id=str(normalized_id)
            )

        raise HTTPException(status_code=404, detail="AI Companion not found")

    raise HTTPException(status_code=501, detail="Not implemented")


@router.get("/ai-companions/")
async def get_companion_trailing_slash():
    raise HTTPException(status_code=422, detail="Invalid companion id format")
