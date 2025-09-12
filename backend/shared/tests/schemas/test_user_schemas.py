import pytest
from pydantic import ValidationError
from backend.shared.src.schemas.user_schema import UserCreate, UserUpdate

def test_user_create_schema_valid():
    """Test that a valid UserCreate schema passes validation."""
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    user = UserCreate(**user_data)
    assert user.email == user_data["email"]

def test_user_create_schema_invalid_email():
    """Test that an invalid email in UserCreate schema raises a validation error."""
    with pytest.raises(ValidationError):
        UserCreate(email="invalid-email", password="password")

def test_user_create_schema_password_too_short():
    """Test that a short password in UserCreate schema raises a validation error."""
    with pytest.raises(ValidationError):
        UserCreate(email="test@example.com", password="123") # Assuming a min length

def test_user_update_schema():
    """Test that the UserUpdate schema correctly handles partial updates."""
    update_data = {"first_name": "Updated"}
    user_update = UserUpdate(**update_data)
    assert user_update.first_name == "Updated"
    assert user_update.last_name is None
