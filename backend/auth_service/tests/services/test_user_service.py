import pytest
from unittest.mock import Mock
from backend.auth_service.src.services.user_service import UserService
from backend.shared.src.models.user import User

# This is a placeholder for unit tests for the UserService.
# These tests will fail until the UserService is implemented.

@pytest.fixture
def mock_db_session():
    """Fixture to create a mock database session."""
    return Mock()

def test_create_user(mock_db_session):
    """Test creating a new user."""
    user_service = UserService(mock_db_session)
    user_data = {"email": "test@example.com", "password": "password123"}
    
    # Mock the return value of the db session
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    new_user = user_service.create_user(user_data)
    
    assert new_user.email == user_data["email"]
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_get_user_by_email(mock_db_session):
    """Test getting a user by email."""
    user_service = UserService(mock_db_session)
    email = "test@example.com"
    
    # Mock the query to return a user
    mock_user = User(email=email, hashed_password="hashed_password")
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    found_user = user_service.get_user_by_email(email)
    
    assert found_user
    assert found_user.email == email

def test_get_user_by_email_not_found(mock_db_session):
    """Test getting a non-existent user by email."""
    user_service = UserService(mock_db_session)
    email = "nonexistent@example.com"
    
    # Mock the query to return None
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    found_user = user_service.get_user_by_email(email)
    
    assert found_user is None
