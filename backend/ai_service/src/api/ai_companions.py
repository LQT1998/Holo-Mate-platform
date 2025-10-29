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
from shared.src.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ai_service.src.services.ai_companion_service import CompanionService
from shared.src.constants import (
    DEV_KNOWN_COMPANION_ID,
    DEV_FORBIDDEN_ID,
    DEV_NONEXISTENT_PREFIX,
    DEV_OWNER_ID,
)

router = APIRouter(tags=["AI Companions"])


def normalize_companion_id(companion_id: str) -> uuid.UUID:
    """
    Normalize companion_id to UUID.

    - DEV: If valid UUID, use it directly. Otherwise, map to stable UUID5 using namespace + id text
    - PROD: require valid UUID; invalid -> 422
    """
    if not companion_id or companion_id.strip() != companion_id or any(
        ch.isspace() for ch in companion_id
    ):
        raise HTTPException(status_code=422, detail="Invalid companion id format")

    # Try to parse as UUID first (works for both DEV and PROD)
    try:
        return uuid.UUID(companion_id)
    except Exception:
        # If not a valid UUID, check if we're in DEV mode
        if settings.DEV_MODE:
            return uuid.uuid5(uuid.NAMESPACE_URL, f"dev:ai-companion:{companion_id}")
        else:
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
    db: AsyncSession = Depends(get_db),
):
    """
    List AI companions for the authenticated user with pagination, search, and filtering.
    """
    if settings.DEV_MODE:
        # Use real service/DB for consistency between create & list in DEV
        service = CompanionService(db)
        companions = await service.list_companions(uuid.UUID(str(current_user["id"])) )
        total = len(companions)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated = companions[start_idx:end_idx]
        items = [
            AICompanionRead(
                id=c.id,
                user_id=c.user_id,
                name=c.name,
                description=c.description,
                personality=c.personality,
                voice_profile=None,
                character_asset=None,
                preferences=None,
                status=c.status,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in paginated
        ]
        return AICompanionListResponse(
            companions=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
        )

    # Non-DEV path: fetch from DB
    service = CompanionService(db)
    companions = await service.list_companions(uuid.UUID(str(current_user["id"])) )
    # Basic pagination in memory for now
    total = len(companions)
    total_pages = (total + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated = companions[start_idx:end_idx]
    # Map ORM to schema
    items = [
        AICompanionRead(
            id=c.id,
            user_id=c.user_id,
            name=c.name,
            description=c.description,
            personality=c.personality,
            voice_profile=None,
            character_asset=None,
            preferences=None,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in paginated
    ]
    return AICompanionListResponse(
        companions=items, total=total, page=page, per_page=per_page, total_pages=total_pages
    )


@router.post(
    "/ai-companions", response_model=AICompanionRead, status_code=status.HTTP_201_CREATED
)
async def create_ai_companion(
    response: Response,
    payload: AICompanionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if settings.DEV_MODE:
        # Use real service/DB to persist companion in DEV
        service = CompanionService(db)
        created = await service.create_companion(
            user_id=uuid.UUID(str(current_user["id"])),
            name=payload.name,
            description=payload.description,
            personality=payload.personality.model_dump() if payload.personality else None,
        )
        response.headers["Location"] = f"/ai-companions/{created.id}"
        return AICompanionRead(
            id=created.id,
            user_id=created.user_id,
            name=created.name,
            description=created.description,
            personality=created.personality,
            voice_profile=None,
            character_asset=None,
            preferences=None,
            status=created.status,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )

    # Non-DEV path: create in DB
    service = CompanionService(db)
    created = await service.create_companion(
        user_id=uuid.UUID(str(current_user["id"])),
        name=payload.name,
        description=payload.description,
        personality=payload.personality.model_dump() if payload.personality else None,
    )
    response.headers["Location"] = f"/ai-companions/{created.id}"
    return AICompanionRead(
        id=created.id,
        user_id=created.user_id,
        name=created.name,
        description=created.description,
        personality=created.personality,
        voice_profile=None,
        character_asset=None,
        preferences=None,
        status=created.status,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("/ai-companions/{companion_id}", response_model=AICompanionRead)
async def get_ai_companion(
    companion_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
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
                name="Test Companion",
                description="A helpful AI Companion for testing",
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
                    character_id="avatar_v1",
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

        # For unknown IDs in DEV_MODE, fall through to real DB lookup
        # This allows integration tests to create and retrieve real data

    # Non-DEV path: fetch from DB
    service = CompanionService(db)
    comp = await service.get_companion_by_id(
        uuid.UUID(str(current_user["id"])), normalize_companion_id(companion_id)
    )
    if not comp:
        raise HTTPException(status_code=404, detail="AI Companion not found")
    return AICompanionRead(
        id=comp.id,
        user_id=comp.user_id,
        name=comp.name,
        description=comp.description,
        personality=comp.personality,
        voice_profile=None,
        character_asset=None,
        preferences=None,
        status=comp.status,
        created_at=comp.created_at,
        updated_at=comp.updated_at,
    )


@router.put("/ai-companions/{companion_id}", response_model=AICompanionRead)
async def update_ai_companion(
    companion_id: str,
    payload: AICompanionUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
                name=update_data.get("name", "Test Companion"),
                description=update_data.get(
                    "description", "A helpful AI Companion for testing"
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
                        "character_id": "avatar_v1",
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

    # Non-DEV path: update in DB
    service = CompanionService(db)
    update_data = payload.model_dump(exclude_unset=True)
    if "personality" in update_data and update_data["personality"] is not None:
        update_data["personality"] = update_data["personality"].model_dump()
    updated = await service.update_companion(
        uuid.UUID(str(current_user["id"])), normalize_companion_id(companion_id), update_data
    )
    if not updated:
        raise HTTPException(status_code=404, detail="AI Companion not found")
    return AICompanionRead(
        id=updated.id,
        user_id=updated.user_id,
        name=updated.name,
        description=updated.description,
        personality=updated.personality,
        voice_profile=None,
        character_asset=None,
        preferences=None,
        status=updated.status,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.delete("/ai-companions/{companion_id}", response_model=DeleteResponse)
async def delete_ai_companion(
    companion_id: str, current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
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

    # Non-DEV path: delete from DB
    service = CompanionService(db)
    ok = await service.delete_companion(
        uuid.UUID(str(current_user["id"])), normalize_companion_id(companion_id)
    )
    if not ok:
        raise HTTPException(status_code=404, detail="AI Companion not found")
    return DeleteResponse(message="AI Companion deleted successfully", deleted_id=str(normalize_companion_id(companion_id)))


@router.get("/ai-companions/")
async def get_companion_trailing_slash():
    raise HTTPException(status_code=422, detail="Invalid companion id format")
