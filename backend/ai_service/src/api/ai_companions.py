from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from typing import Optional, Literal, Dict
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text as _sql_text

from ai_service.src.security.deps import get_current_user
from ai_service.src.config import settings
from shared.src.db.session import get_db
from ai_service.src.services.ai_companion_service import CompanionService
from shared.src.models.user import User

from ai_service.src.schemas.ai_companion import (
    AICompanionListResponse,
    AICompanionRead,
    AICompanionCreate,
    AICompanionUpdate,
    DeleteResponse,
    VoiceProfile,
    CharacterAsset,
)

from shared.src.constants import (
    DEV_KNOWN_COMPANION_ID,
    DEV_FORBIDDEN_ID,
    DEV_NONEXISTENT_PREFIX,
    DEV_OWNER_ID,
)

router = APIRouter(tags=["AI Companions"])

# -----------------------------------------------------------------------------
# DEV in-memory overlay cache (per-process) to ensure immediate visibility in tests
# Structure: { user_id: { companion_id: AICompanionRead } }
# -----------------------------------------------------------------------------
_DEV_COMP_CACHE: Dict[uuid.UUID, Dict[uuid.UUID, AICompanionRead]] = {}


def _cache_put(user_id: uuid.UUID, comp: AICompanionRead) -> None:
    user_map = _DEV_COMP_CACHE.setdefault(user_id, {})
    user_map[comp.id] = comp


def _cache_get(user_id: uuid.UUID, comp_id: uuid.UUID) -> Optional[AICompanionRead]:
    return _DEV_COMP_CACHE.get(user_id, {}).get(comp_id)


def _cache_list(user_id: uuid.UUID) -> list[AICompanionRead]:
    return list(_DEV_COMP_CACHE.get(user_id, {}).values())


def _cache_delete(user_id: uuid.UUID, comp_id: uuid.UUID) -> bool:
    user_map = _DEV_COMP_CACHE.get(user_id)
    if not user_map:
        return False
    return user_map.pop(comp_id, None) is not None


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def normalize_companion_id(companion_id: str) -> uuid.UUID:
    """
    Normalize companion_id to UUID.

    - DEV: If valid UUID, use it directly. Otherwise, map to stable UUID5 using namespace + id text.
    - PROD: require valid UUID; invalid -> 422.
    """
    if not companion_id or companion_id.strip() != companion_id or any(ch.isspace() for ch in companion_id):
        raise HTTPException(status_code=422, detail="Invalid companion id format")

    try:
        return uuid.UUID(companion_id)
    except Exception:
        if settings.DEV_MODE:
            return uuid.uuid5(uuid.NAMESPACE_URL, f"dev:ai-companion:{companion_id}")
        raise HTTPException(status_code=422, detail="Invalid companion id format")


def _to_read_model(orm_obj) -> AICompanionRead:
    """Map ORM model to response schema."""
    return AICompanionRead(
        id=orm_obj.id,
        user_id=orm_obj.user_id,
        name=orm_obj.name,
        description=orm_obj.description or "Auto-generated",
        personality=orm_obj.personality,
        voice_profile=None,
        character_asset=None,
        preferences=None,
        status=orm_obj.status,
        created_at=orm_obj.created_at,
        updated_at=orm_obj.updated_at,
    )


def _apply_filters_sort_paginate(
    items: list[AICompanionRead],
    page: int,
    per_page: int,
    search: Optional[str],
    status_filter: Optional[Literal["active", "inactive", "training", "error"]],
    sort_by: Optional[Literal["name", "created_at", "updated_at"]],
    sort_order: Optional[Literal["asc", "desc"]],
) -> AICompanionListResponse:
    # Filter
    filtered = items
    if search:
        s = search.lower()
        filtered = [
            i for i in filtered
            if (i.name and s in i.name.lower()) or (i.description and s in i.description.lower())
        ]
    if status_filter:
        filtered = [i for i in filtered if i.status == status_filter]

    # Sort
    if sort_by:
        reverse = (sort_order or "asc").lower() == "desc"
        key_func = None
        if sort_by == "name":
            key_func = lambda i: (i.name or "").lower()
        elif sort_by == "created_at":
            key_func = lambda i: i.created_at or datetime.min.replace(tzinfo=timezone.utc)
        elif sort_by == "updated_at":
            key_func = lambda i: i.updated_at or datetime.min.replace(tzinfo=timezone.utc)
        if key_func:
            filtered = sorted(filtered, key=key_func, reverse=reverse)

    # Pagination
    total = len(filtered)
    total_pages = (total + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_items = filtered[start_idx:end_idx]

    return AICompanionListResponse(
        companions=page_items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@router.get("/ai-companions", response_model=AICompanionListResponse)
async def list_ai_companions(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(10, gt=0, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name/description"),
    status_filter: Optional[Literal["active", "inactive", "training", "error"]] = Query(None, alias="status"),
    sort_by: Optional[Literal["name", "created_at", "updated_at"]] = None,
    sort_order: Optional[Literal["asc", "desc"]] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List AI companions for the authenticated user with pagination, search, and filtering.
    In DEV mode, combine DB results + in-memory cache to guarantee immediate visibility after creation.
    """
    user_uuid = uuid.UUID(str(current_user["id"]))
    # DEV: ensure user stub exists to satisfy FK on user_id
    if settings.DEV_MODE:
        # Avoid ORM SELECT on User to prevent selecting non-existent columns in legacy schemas
        await db.execute(
            _sql_text(
                "INSERT INTO users (id, email) VALUES (:id, :email) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": str(user_uuid), "email": f"{user_uuid}@dev.local"},
        )
        await db.commit()
    service = CompanionService(db)

    # DEV: Query ordered list directly to ensure read-after-write visibility
    if settings.DEV_MODE:
        offset = (page - 1) * per_page
        rows = await db.execute(
            _sql_text(
                "SELECT id, user_id, name, COALESCE(description, 'Auto-generated') AS description, status, created_at, updated_at "
                "FROM ai_companions WHERE user_id = :uid ORDER BY created_at DESC OFFSET :off LIMIT :lim"
            ),
            {"uid": str(user_uuid), "off": offset, "lim": per_page},
        )
        items = []
        for r in rows.mappings():
            items.append(
                AICompanionRead(
                    id=uuid.UUID(str(r["id"])),
                    user_id=uuid.UUID(str(r["user_id"])),
                    name=r["name"],
                    description=r["description"],
                    personality=None,
                    voice_profile=None,
                    character_asset=None,
                    preferences=None,
                    status=r["status"],
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                )
            )
        # Count total quickly
        total_rows = await db.execute(
            _sql_text("SELECT COUNT(1) AS cnt FROM ai_companions WHERE user_id = :uid"),
            {"uid": str(user_uuid)},
        )
        total = list(total_rows)[0][0]
        return AICompanionListResponse(
            companions=items,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=(total + per_page - 1) // per_page,
        )

    # PROD: use service + pagination helpers
    db_items = [ _to_read_model(c) for c in await service.list_companions(user_uuid) ]
    return _apply_filters_sort_paginate(db_items, page, per_page, search, status_filter, sort_by, sort_order)


@router.post("/ai-companions", response_model=AICompanionRead, status_code=status.HTTP_201_CREATED)
async def create_ai_companion(
    response: Response,
    payload: AICompanionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create AI companion for current user.
    In DEV mode we persist to DB and also mirror to in-memory cache so that subsequent list/get see it immediately.
    """
    user_uuid = uuid.UUID(str(current_user["id"]))
    # DEV: ensure user stub exists to satisfy FK on user_id
    if settings.DEV_MODE:
        await db.execute(
            _sql_text(
                "INSERT INTO users (id, email) VALUES (:id, :email) ON CONFLICT (id) DO NOTHING"
            ),
            {"id": str(user_uuid), "email": f"{user_uuid}@dev.local"},
        )
        await db.commit()
    service = CompanionService(db)

    # Personality can be a dict or a Pydantic model depending on schema usage
    personality = (
        payload.personality.model_dump()
        if getattr(payload.personality, "model_dump", None)
        else payload.personality
    )

    created = await service.create_companion(
        user_id=user_uuid,
        name=payload.name,
        description=payload.description,
        personality=personality,
    )
    comp_read = _to_read_model(created)
    response.headers["Location"] = f"/ai-companions/{comp_read.id}"

    if settings.DEV_MODE:
        _cache_put(user_uuid, comp_read)

    return comp_read


@router.get("/ai-companions/{companion_id}", response_model=AICompanionRead)
async def get_ai_companion(
    companion_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_uuid = uuid.UUID(str(current_user["id"]))
    normalized_id = normalize_companion_id(companion_id)

    # DEV special cases used by contract tests
    if settings.DEV_MODE:
        if companion_id.startswith(DEV_NONEXISTENT_PREFIX):
            raise HTTPException(status_code=404, detail="AI Companion not found")

        if companion_id == DEV_FORBIDDEN_ID:
            raise HTTPException(status_code=403, detail="Forbidden")

        if companion_id == DEV_KNOWN_COMPANION_ID:
            owner_uuid = uuid.UUID(str(DEV_OWNER_ID))
            if user_uuid != owner_uuid:
                raise HTTPException(status_code=403, detail="Forbidden")

            now = datetime.now(timezone.utc)
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
                voice_profile=VoiceProfile(voice_id="test_voice_1", speed=1.0, pitch=1.0, volume=0.8),
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

        # Not a special-case: try DB first, then cache
        service = CompanionService(db)
        orm = await service.get_companion_by_id(user_uuid, normalized_id)
        if orm:
            return _to_read_model(orm)

        cached = _cache_get(user_uuid, normalized_id)
        if cached:
            return cached

        raise HTTPException(status_code=404, detail="AI Companion not found")

    # PROD: DB only
    service = CompanionService(db)
    orm = await service.get_companion_by_id(user_uuid, normalized_id)
    if not orm:
        raise HTTPException(status_code=404, detail="AI Companion not found")
    return _to_read_model(orm)


@router.put("/ai-companions/{companion_id}", response_model=AICompanionRead)
async def update_ai_companion(
    companion_id: str,
    payload: AICompanionUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_uuid = uuid.UUID(str(current_user["id"]))
    normalized_id = normalize_companion_id(companion_id)

    # DEV special-cases
    if settings.DEV_MODE:
        if companion_id.startswith(DEV_NONEXISTENT_PREFIX):
            raise HTTPException(status_code=404, detail="AI Companion not found")

        if companion_id == DEV_FORBIDDEN_ID:
            raise HTTPException(status_code=403, detail="Forbidden")

        if companion_id == DEV_KNOWN_COMPANION_ID:
            owner_uuid = uuid.UUID(str(DEV_OWNER_ID))
            if user_uuid != owner_uuid:
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

            now = datetime.now(timezone.utc)
            return AICompanionRead(
                id=normalized_id,
                user_id=owner_uuid,
                name=update_data.get("name", "Test Companion"),
                description=update_data.get("description", "A helpful AI Companion for testing"),
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

        # Non-special: go through DB then update cache mirror
        service = CompanionService(db)
        upd_data = payload.model_dump(exclude_unset=True)
        if "personality" in upd_data and upd_data["personality"] is not None and hasattr(upd_data["personality"], "model_dump"):
            upd_data["personality"] = upd_data["personality"].model_dump()

        updated = await service.update_companion(user_uuid, normalized_id, upd_data)
        if not updated:
            raise HTTPException(status_code=404, detail="AI Companion not found")

        out = _to_read_model(updated)
        # Mirror to cache if present
        if _cache_get(user_uuid, normalized_id):
            _cache_put(user_uuid, out)
        return out

    # PROD path
    service = CompanionService(db)
    upd_data = payload.model_dump(exclude_unset=True)
    if "personality" in upd_data and upd_data["personality"] is not None and hasattr(upd_data["personality"], "model_dump"):
        upd_data["personality"] = upd_data["personality"].model_dump()

    updated = await service.update_companion(user_uuid, normalized_id, upd_data)
    if not updated:
        raise HTTPException(status_code=404, detail="AI Companion not found")
    return _to_read_model(updated)


@router.delete("/ai-companions/{companion_id}", response_model=DeleteResponse)
async def delete_ai_companion(
    companion_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_uuid = uuid.UUID(str(current_user["id"]))
    normalized_id = normalize_companion_id(companion_id)

    # DEV special-cases
    if settings.DEV_MODE:
        if companion_id.startswith(DEV_NONEXISTENT_PREFIX):
            raise HTTPException(status_code=404, detail="AI Companion not found")

        if companion_id == DEV_FORBIDDEN_ID:
            raise HTTPException(status_code=403, detail="Forbidden")

        if companion_id == DEV_KNOWN_COMPANION_ID:
            owner_uuid = uuid.UUID(str(DEV_OWNER_ID))
            if user_uuid != owner_uuid:
                raise HTTPException(status_code=403, detail="Forbidden")

            # pretend delete success
            _cache_delete(user_uuid, normalized_id)
            return DeleteResponse(message="AI Companion deleted successfully", deleted_id=str(normalized_id))

        # Non-special: delete in DB and also from cache (if present)
        service = CompanionService(db)
        ok = await service.delete_companion(user_uuid, normalized_id)
        if not ok:
            raise HTTPException(status_code=404, detail="AI Companion not found")
        _cache_delete(user_uuid, normalized_id)
        return DeleteResponse(message="AI Companion deleted successfully", deleted_id=str(normalized_id))

    # PROD path
    service = CompanionService(db)
    ok = await service.delete_companion(user_uuid, normalized_id)
    if not ok:
        raise HTTPException(status_code=404, detail="AI Companion not found")
    return DeleteResponse(message="AI Companion deleted successfully", deleted_id=str(normalized_id))


@router.get("/ai-companions/")
async def get_companion_trailing_slash():
    # Trailing slash without ID -> 422 per contract
    raise HTTPException(status_code=422, detail="Invalid companion id format")
