import pytest
from unittest.mock import Mock
from backend.ai_service.src.services.ai_companion_service import AICompanionService
from backend.shared.src.models.ai_companion import AICompanion

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    return Mock()

def test_create_ai_companion(mock_db_session):
    """Test creating a new AI companion."""
    ai_companion_service = AICompanionService(mock_db_session)
    user_id = "some_user_id"
    companion_data = {"name": "Companion1", "description": "A test companion"}

    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    new_companion = ai_companion_service.create_ai_companion(user_id, companion_data)

    assert new_companion.name == companion_data["name"]
    assert new_companion.user_id == user_id
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_get_ai_companion_by_id(mock_db_session):
    """Test getting an AI companion by its ID."""
    ai_companion_service = AICompanionService(mock_db_session)
    companion_id = "some_companion_id"
    user_id = "some_user_id"

    mock_companion = AICompanion(id=companion_id, user_id=user_id, name="Companion1")
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_companion

    found_companion = ai_companion_service.get_ai_companion_by_id(user_id, companion_id)

    assert found_companion
    assert found_companion.id == companion_id
    assert found_companion.user_id == user_id
