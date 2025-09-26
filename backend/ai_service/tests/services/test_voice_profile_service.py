"""
Tests for VoiceProfileService
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException

from ai_service.src.services.voice_profile_service import VoiceProfileService
from shared.src.models.voice_profile import VoiceProfile
from shared.src.models.ai_companion import AICompanion
from shared.src.enums.voice_profile_enums import VoiceProfileStatus


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock async database session."""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def voice_profile_service(mock_db_session):
    """Fixture to create VoiceProfileService with mock database session."""
    return VoiceProfileService(mock_db_session)


@pytest.fixture
def sample_voice_profile_data():
    """Fixture for sample voice profile data."""
    return {
        "provider_name": "elevenlabs",
        "provider_voice_id": "voice_123",
        "settings": {"stability": 0.5, "clarity": 0.75}
    }


class TestVoiceProfileServiceCreate:
    """Test cases for voice profile creation"""

    @pytest.mark.asyncio
    async def test_create_voice_profile_success(self, voice_profile_service, mock_db_session, sample_voice_profile_data):
        """Test successful voice profile creation"""
        user_id = uuid4()
        companion_id = uuid4()
        
        # Mock companion exists
        mock_companion = AICompanion(id=companion_id, user_id=user_id, name="Test Companion")
        mock_companion_result = Mock()
        mock_companion_result.scalars.return_value.first.return_value = mock_companion
        
        # Mock no existing active voice profile
        mock_existing_result = Mock()
        mock_existing_result.scalars.return_value.first.return_value = None
        
        mock_db_session.execute.side_effect = [mock_companion_result, mock_existing_result]
        
        # Mock voice profile creation
        mock_voice_profile = VoiceProfile(
            id=uuid4(),
            ai_companion_id=companion_id,
            provider_name=sample_voice_profile_data["provider_name"],
            provider_voice_id=sample_voice_profile_data["provider_voice_id"],
            status=VoiceProfileStatus.active
        )
        mock_db_session.refresh.side_effect = lambda obj: setattr(obj, 'id', mock_voice_profile.id)
        
        result = await voice_profile_service.create_voice_profile(
            user_id=user_id,
            companion_id=companion_id,
            provider_name=sample_voice_profile_data["provider_name"],
            provider_voice_id=sample_voice_profile_data["provider_voice_id"],
            settings=sample_voice_profile_data["settings"]
        )
        
        assert result is not None
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_voice_profile_companion_not_found(self, voice_profile_service, mock_db_session, sample_voice_profile_data):
        """Test voice profile creation when companion not found"""
        user_id = uuid4()
        companion_id = uuid4()
        
        # Mock companion not found
        mock_companion_result = Mock()
        mock_companion_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_companion_result
        
        with pytest.raises(HTTPException) as exc_info:
            await voice_profile_service.create_voice_profile(
                user_id=user_id,
                companion_id=companion_id,
                provider_name=sample_voice_profile_data["provider_name"],
                provider_voice_id=sample_voice_profile_data["provider_voice_id"]
            )
        
        assert exc_info.value.status_code == 404
        assert "Companion not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_voice_profile_existing_active(self, voice_profile_service, mock_db_session, sample_voice_profile_data):
        """Test voice profile creation when companion already has active profile"""
        user_id = uuid4()
        companion_id = uuid4()
        
        # Mock companion exists
        mock_companion = AICompanion(id=companion_id, user_id=user_id, name="Test Companion")
        mock_companion_result = Mock()
        mock_companion_result.scalars.return_value.first.return_value = mock_companion
        
        # Mock existing active voice profile
        mock_existing_result = Mock()
        mock_existing_result.scalars.return_value.first.return_value = VoiceProfile()
        
        mock_db_session.execute.side_effect = [mock_companion_result, mock_existing_result]
        
        with pytest.raises(HTTPException) as exc_info:
            await voice_profile_service.create_voice_profile(
                user_id=user_id,
                companion_id=companion_id,
                provider_name=sample_voice_profile_data["provider_name"],
                provider_voice_id=sample_voice_profile_data["provider_voice_id"]
            )
        
        assert exc_info.value.status_code == 400
        assert "already has an active voice profile" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_create_voice_profile_missing_fields(self, voice_profile_service, mock_db_session):
        """Test voice profile creation with missing required fields"""
        user_id = uuid4()
        companion_id = uuid4()
        
        with pytest.raises(HTTPException) as exc_info:
            await voice_profile_service.create_voice_profile(
                user_id=user_id,
                companion_id=companion_id,
                provider_name="",
                provider_voice_id="voice_123"
            )
        
        assert exc_info.value.status_code == 422
        assert "Provider name and voice ID are required" in exc_info.value.detail


class TestVoiceProfileServiceGet:
    """Test cases for getting voice profiles"""

    @pytest.mark.asyncio
    async def test_get_voice_profile_success(self, voice_profile_service, mock_db_session):
        """Test successful voice profile retrieval by ID"""
        user_id = uuid4()
        profile_id = uuid4()
        
        mock_voice_profile = VoiceProfile(
            id=profile_id,
            ai_companion_id=uuid4(),
            provider_name="elevenlabs",
            provider_voice_id="voice_123",
            status=VoiceProfileStatus.active
        )
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_voice_profile
        mock_db_session.execute.return_value = mock_result
        
        result = await voice_profile_service.get_voice_profile(user_id, profile_id)
        
        assert result == mock_voice_profile

    @pytest.mark.asyncio
    async def test_get_voice_profile_not_found(self, voice_profile_service, mock_db_session):
        """Test voice profile retrieval when profile not found"""
        user_id = uuid4()
        profile_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        with pytest.raises(HTTPException) as exc_info:
            await voice_profile_service.get_voice_profile(user_id, profile_id)
        
        assert exc_info.value.status_code == 404
        assert "Voice profile not found" in exc_info.value.detail


class TestVoiceProfileServiceList:
    """Test cases for listing voice profiles"""

    @pytest.mark.asyncio
    async def test_list_voice_profiles_success(self, voice_profile_service, mock_db_session):
        """Test successful voice profile listing"""
        user_id = uuid4()
        
        mock_voice_profiles = [
            VoiceProfile(id=uuid4(), ai_companion_id=uuid4(), provider_name="elevenlabs", status=VoiceProfileStatus.active),
            VoiceProfile(id=uuid4(), ai_companion_id=uuid4(), provider_name="azure", status=VoiceProfileStatus.inactive)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_voice_profiles
        mock_db_session.execute.return_value = mock_result
        
        result = await voice_profile_service.list_voice_profiles(user_id)
        
        assert len(result) == 2
        assert result == mock_voice_profiles

    @pytest.mark.asyncio
    async def test_list_voice_profiles_with_companion_filter(self, voice_profile_service, mock_db_session):
        """Test voice profile listing with companion filter"""
        user_id = uuid4()
        companion_id = uuid4()
        
        mock_voice_profiles = [
            VoiceProfile(id=uuid4(), ai_companion_id=companion_id, provider_name="elevenlabs", status=VoiceProfileStatus.active)
        ]
        
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = mock_voice_profiles
        mock_db_session.execute.return_value = mock_result
        
        result = await voice_profile_service.list_voice_profiles(user_id, companion_id)
        
        assert len(result) == 1
        assert result == mock_voice_profiles


class TestVoiceProfileServiceUpdate:
    """Test cases for updating voice profiles"""

    @pytest.mark.asyncio
    async def test_update_voice_profile_success(self, voice_profile_service, mock_db_session):
        """Test successful voice profile update"""
        user_id = uuid4()
        profile_id = uuid4()
        
        # Mock update result
        mock_update_result = Mock()
        mock_update_result.rowcount = 1
        mock_db_session.execute.return_value = mock_update_result
        
        # Mock get_voice_profile call
        mock_voice_profile = VoiceProfile(
            id=profile_id,
            ai_companion_id=uuid4(),
            provider_name="elevenlabs",
            provider_voice_id="voice_123",
            status=VoiceProfileStatus.active
        )
        
        # Mock the get_voice_profile call
        mock_get_result = Mock()
        mock_get_result.scalars.return_value.first.return_value = mock_voice_profile
        mock_db_session.execute.side_effect = [mock_update_result, mock_get_result]
        
        update_data = {"provider_name": "azure", "status": "inactive"}
        result = await voice_profile_service.update_voice_profile(user_id, profile_id, update_data)
        
        assert result == mock_voice_profile
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_voice_profile_not_found(self, voice_profile_service, mock_db_session):
        """Test voice profile update when profile not found"""
        user_id = uuid4()
        profile_id = uuid4()
        
        # Mock update result with no rows affected
        mock_update_result = Mock()
        mock_update_result.rowcount = 0
        mock_db_session.execute.return_value = mock_update_result
        
        update_data = {"provider_name": "azure"}
        
        with pytest.raises(HTTPException) as exc_info:
            await voice_profile_service.update_voice_profile(user_id, profile_id, update_data)
        
        assert exc_info.value.status_code == 404
        assert "Voice profile not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_update_voice_profile_empty_payload(self, voice_profile_service, mock_db_session):
        """Test voice profile update with empty payload"""
        user_id = uuid4()
        profile_id = uuid4()
        
        update_data = {}
        
        with pytest.raises(HTTPException) as exc_info:
            await voice_profile_service.update_voice_profile(user_id, profile_id, update_data)
        
        assert exc_info.value.status_code == 422
        assert "No valid fields to update" in exc_info.value.detail


class TestVoiceProfileServiceDelete:
    """Test cases for deleting voice profiles"""

    @pytest.mark.asyncio
    async def test_delete_voice_profile_success(self, voice_profile_service, mock_db_session):
        """Test successful voice profile deletion (soft delete)"""
        user_id = uuid4()
        profile_id = uuid4()
        
        # Mock archive_voice_profile call
        mock_voice_profile = VoiceProfile(
            id=profile_id,
            ai_companion_id=uuid4(),
            provider_name="elevenlabs",
            status=VoiceProfileStatus.archived
        )
        
        mock_update_result = Mock()
        mock_update_result.rowcount = 1
        mock_get_result = Mock()
        mock_get_result.scalars.return_value.first.return_value = mock_voice_profile
        mock_db_session.execute.side_effect = [mock_update_result, mock_get_result]
        
        result = await voice_profile_service.delete_voice_profile(user_id, profile_id)
        
        assert result is True
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_voice_profile_not_found(self, voice_profile_service, mock_db_session):
        """Test voice profile deletion when profile not found"""
        user_id = uuid4()
        profile_id = uuid4()
        
        # Mock archive_voice_profile failure
        mock_update_result = Mock()
        mock_update_result.rowcount = 0
        mock_db_session.execute.return_value = mock_update_result
        
        with pytest.raises(HTTPException) as exc_info:
            await voice_profile_service.delete_voice_profile(user_id, profile_id)
        
        assert exc_info.value.status_code == 404
        assert "Voice profile not found" in exc_info.value.detail


class TestVoiceProfileServiceUtility:
    """Test cases for utility methods"""

    @pytest.mark.asyncio
    async def test_get_active_voice_profile_success(self, voice_profile_service, mock_db_session):
        """Test successful active voice profile retrieval"""
        user_id = uuid4()
        companion_id = uuid4()
        
        mock_voice_profile = VoiceProfile(
            id=uuid4(),
            ai_companion_id=companion_id,
            provider_name="elevenlabs",
            status=VoiceProfileStatus.active
        )
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = mock_voice_profile
        mock_db_session.execute.return_value = mock_result
        
        result = await voice_profile_service.get_active_voice_profile(user_id, companion_id)
        
        assert result == mock_voice_profile

    @pytest.mark.asyncio
    async def test_get_active_voice_profile_none(self, voice_profile_service, mock_db_session):
        """Test active voice profile retrieval when no active profile exists"""
        user_id = uuid4()
        companion_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        result = await voice_profile_service.get_active_voice_profile(user_id, companion_id)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_set_active_voice_profile_success(self, voice_profile_service, mock_db_session):
        """Test successful voice profile activation"""
        user_id = uuid4()
        profile_id = uuid4()
        companion_id = uuid4()
        
        # Mock get_voice_profile call
        mock_voice_profile = VoiceProfile(
            id=profile_id,
            ai_companion_id=companion_id,
            provider_name="elevenlabs",
            status=VoiceProfileStatus.inactive
        )
        
        mock_get_result = Mock()
        mock_get_result.scalars.return_value.first.return_value = mock_voice_profile
        
        # Mock deactivate and activate update results
        mock_deactivate_result = Mock()
        mock_deactivate_result.rowcount = 1
        mock_activate_result = Mock()
        mock_activate_result.rowcount = 1
        
        # Mock final get_voice_profile call
        mock_final_get_result = Mock()
        mock_final_get_result.scalars.return_value.first.return_value = mock_voice_profile
        
        mock_db_session.execute.side_effect = [
            mock_get_result,  # get_voice_profile
            mock_deactivate_result,  # deactivate others
            mock_activate_result,  # activate target
            mock_final_get_result  # final get_voice_profile
        ]
        
        result = await voice_profile_service.set_active_voice_profile(user_id, profile_id)
        
        assert result == mock_voice_profile
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_voice_profiles_success(self, voice_profile_service, mock_db_session):
        """Test successful voice profile counting"""
        user_id = uuid4()
        
        mock_result = Mock()
        mock_result.scalar.return_value = 3
        mock_db_session.execute.return_value = mock_result
        
        result = await voice_profile_service.count_voice_profiles(user_id)
        
        assert result == 3

    @pytest.mark.asyncio
    async def test_get_voice_profile_stats_success(self, voice_profile_service, mock_db_session):
        """Test successful voice profile statistics retrieval"""
        user_id = uuid4()
        
        # Mock status count query (grouped)
        mock_status_result = Mock()
        mock_status_result.fetchall.return_value = [
            (VoiceProfileStatus.active, 2),
            (VoiceProfileStatus.inactive, 1)
        ]
        
        # Mock provider count query
        mock_provider_result = Mock()
        mock_provider_result.fetchall.return_value = [("elevenlabs", 2), ("azure", 1)]
        
        mock_db_session.execute.side_effect = [mock_status_result, mock_provider_result]
        
        result = await voice_profile_service.get_voice_profile_stats(user_id)
        
        assert "total_voice_profiles" in result
        assert "status_counts" in result
        assert "provider_counts" in result
        assert result["status_counts"]["active"] == 2
        assert result["status_counts"]["inactive"] == 1
        assert result["status_counts"]["archived"] == 0  # Missing status initialized to 0

    @pytest.mark.asyncio
    async def test_archive_voice_profile_success(self, voice_profile_service, mock_db_session):
        """Test successful voice profile archiving"""
        user_id = uuid4()
        profile_id = uuid4()
        
        # Mock update result
        mock_update_result = Mock()
        mock_update_result.rowcount = 1
        mock_db_session.execute.return_value = mock_update_result
        
        # Mock get_voice_profile call
        mock_voice_profile = VoiceProfile(
            id=profile_id,
            ai_companion_id=uuid4(),
            provider_name="elevenlabs",
            status=VoiceProfileStatus.archived
        )
        
        mock_get_result = Mock()
        mock_get_result.scalars.return_value.first.return_value = mock_voice_profile
        mock_db_session.execute.side_effect = [mock_update_result, mock_get_result]
        
        result = await voice_profile_service.archive_voice_profile(user_id, profile_id)
        
        assert result == mock_voice_profile
        mock_db_session.commit.assert_called_once()
