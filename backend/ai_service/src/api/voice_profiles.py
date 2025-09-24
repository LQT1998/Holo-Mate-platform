"""Voice Profiles API endpoints for AI Service"""

from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from ai_service.src.config import settings
from ai_service.src.security.deps import get_current_user
from shared.src.constants import DEV_OWNER_ID
from shared.src.schemas.voice_profile_schema import (
    VoiceProfileResponse,
    VoiceProfileListResponse,
)


router = APIRouter(tags=["Voice Profiles"])


@router.get(
    "/voice-profiles",
    response_model=VoiceProfileListResponse,
    status_code=status.HTTP_200_OK,
    summary="List available voice profiles",
)
async def list_voice_profiles(
    current_user: dict = Depends(get_current_user),
) -> VoiceProfileListResponse:
    """Retrieve list of voice profiles in DEV mode."""

    if not settings.DEV_MODE:
        raise HTTPException(status_code=501, detail="Not implemented")

    if str(current_user["id"]) != str(DEV_OWNER_ID):
        raise HTTPException(status_code=403, detail="Forbidden: Access denied")

    now = datetime.now(timezone.utc)

    mock_profiles = [
        VoiceProfileResponse(
            id=uuid.uuid4(),
            name="Aurora",
            language="en-US",
            gender="female",
            sample_url="https://cdn.holomate.dev/voices/aurora.mp3",
            created_at=now,
            updated_at=now,
        ),
        VoiceProfileResponse(
            id=uuid.uuid4(),
            name="Orion",
            language="en-GB",
            gender="male",
            sample_url="https://cdn.holomate.dev/voices/orion.mp3",
            created_at=now,
            updated_at=now,
        ),
        VoiceProfileResponse(
            id=uuid.uuid4(),
            name="Luna",
            language="ja-JP",
            gender="female",
            sample_url="https://cdn.holomate.dev/voices/luna.mp3",
            created_at=now,
            updated_at=now,
        ),
    ]

    return VoiceProfileListResponse(voice_profiles=mock_profiles)

