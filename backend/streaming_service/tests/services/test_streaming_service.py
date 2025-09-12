import pytest
from unittest.mock import Mock
from backend.streaming_service.src.services.streaming_service import StreamingService

@pytest.fixture
def mock_redis_client():
    """Fixture to create a mock Redis client."""
    return Mock()

def test_start_streaming_session(mock_redis_client):
    """Test starting a new streaming session."""
    streaming_service = StreamingService(mock_redis_client)
    session_id = "test_session_123"
    user_id = "test_user"

    streaming_service.start_session(session_id, user_id)

    mock_redis_client.set.assert_called_with(f"stream:{session_id}:status", "active")

def test_get_streaming_session_status(mock_redis_client):
    """Test getting the status of a streaming session."""
    streaming_service = StreamingService(mock_redis_client)
    session_id = "test_session_123"
    
    mock_redis_client.get.return_value = b"active"

    status = streaming_service.get_session_status(session_id)
    
    assert status == "active"
    mock_redis_client.get.assert_called_with(f"stream:{session_id}:status")

def test_end_streaming_session(mock_redis_client):
    """Test ending a streaming session."""
    streaming_service = StreamingService(mock_redis_client)
    session_id = "test_session_123"
    
    streaming_service.end_session(session_id)
    
    mock_redis_client.delete.assert_called_with(f"stream:{session_id}:status")
