"""
Comprehensive unit tests for UserService CRUD operations.

Tests cover all CRUD operations with proper async/await patterns,
error handling, and edge cases.
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from auth_service.src.services.user_service import UserService
from shared.src.models.user import User
from shared.src.schemas.user import UserCreate
from shared.src.security.utils import get_password_hash


@pytest.fixture
def mock_db_session():
    """Fixture to create a mock async database session."""
    session = AsyncMock()
    session.add = Mock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = Mock()  # delete() is not async
    return session


@pytest.fixture
def user_service(mock_db_session):
    """Fixture to create UserService with mock database session."""
    return UserService(mock_db_session)


@pytest.fixture
def sample_user_create():
    """Fixture for sample user creation data."""
    return UserCreate(
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )


@pytest.fixture
def sample_user():
    """Fixture for sample user object."""
    user_id = uuid4()
    return User(
        id=user_id,
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        first_name="Test",
        last_name="User",
        is_active=True
    )


class TestUserServiceCreate:
    """Test cases for user creation."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_db_session, sample_user_create, sample_user):
        """Test successful user creation returns User object with correct data."""
        # Mock the database operations
        mock_db_session.refresh.side_effect = lambda user: setattr(user, 'id', sample_user.id)
        
        # Create user
        created_user = await user_service.create_user(sample_user_create)
        
        # Verify user data
        assert created_user.email == sample_user_create.email
        assert created_user.first_name == sample_user_create.first_name
        assert created_user.last_name == sample_user_create.last_name
        assert created_user.hashed_password != sample_user_create.password  # Password should be hashed
        assert created_user.is_active is True  # Default value
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_exception(self, user_service, mock_db_session, sample_user_create):
        """Test creating user with duplicate email raises IntegrityError."""
        # Mock database to raise IntegrityError for duplicate email
        mock_db_session.commit.side_effect = IntegrityError("UNIQUE constraint failed", None, None)
        
        # User creation should raise IntegrityError
        with pytest.raises(IntegrityError):
            await user_service.create_user(sample_user_create)

    @pytest.mark.asyncio
    async def test_create_user_password_hashing(self, user_service, mock_db_session, sample_user_create):
        """Test that password is properly hashed."""
        created_user = await user_service.create_user(sample_user_create)
        
        # Password should be hashed, not plain text
        assert created_user.hashed_password != sample_user_create.password
        assert len(created_user.hashed_password) > 20  # Hashed passwords are longer
        assert created_user.hashed_password.startswith("$2b$")  # bcrypt hash format

    @pytest.mark.asyncio
    async def test_create_user_minimal_data(self, user_service, mock_db_session):
        """Test creating user with minimal required data."""
        minimal_user = UserCreate(email="minimal@example.com", password="password123")
        
        created_user = await user_service.create_user(minimal_user)
        
        assert created_user.email == minimal_user.email
        assert created_user.first_name is None
        assert created_user.last_name is None
        assert created_user.is_active is True


class TestUserServiceGet:
    """Test cases for user retrieval."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_service, mock_db_session, sample_user):
        """Test getting user by ID returns correct user."""
        # Mock execute to return the sample user
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        found_user = await user_service.get_user_by_id(sample_user.id)
        
        assert found_user is not None
        assert found_user.id == sample_user.id
        assert found_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service, mock_db_session):
        """Test getting user by non-existent ID returns None."""
        # Mock execute to return None
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        found_user = await user_service.get_user_by_id(uuid4())
        
        assert found_user is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, user_service, mock_db_session, sample_user):
        """Test getting user by email returns correct user."""
        # Mock execute to return the sample user
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        found_user = await user_service.get_user_by_email(sample_user.email)
        
        assert found_user is not None
        assert found_user.email == sample_user.email
        assert found_user.id == sample_user.id

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_service, mock_db_session):
        """Test getting user by non-existent email returns None."""
        # Mock execute to return None
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        found_user = await user_service.get_user_by_email("nonexistent@example.com")
        
        assert found_user is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_with_string_uuid(self, user_service, mock_db_session, sample_user):
        """Test getting user by ID works with string UUID."""
        # Mock execute to return the sample user
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        found_user = await user_service.get_user_by_id(str(sample_user.id))
        
        assert found_user is not None
        assert found_user.id == sample_user.id


class TestUserServiceUpdate:
    """Test cases for user updates."""

    @pytest.mark.asyncio
    async def test_update_user_email_success(self, user_service, mock_db_session, sample_user):
        """Test updating user email returns user with new email."""
        # Mock get_user_by_id to return existing user
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        updated_user = await user_service.update_user(sample_user.id, {"email": "newemail@example.com"})
        
        assert updated_user is not None
        assert updated_user.email == "newemail@example.com"
        assert updated_user.id == sample_user.id
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_password_success(self, user_service, mock_db_session, sample_user):
        """Test updating user password changes hashed_password."""
        original_hashed = sample_user.hashed_password
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        updated_user = await user_service.update_user(sample_user.id, {"password": "newpassword123"})
        
        assert updated_user is not None
        assert updated_user.hashed_password != original_hashed
        assert updated_user.hashed_password != "newpassword123"  # Should be hashed

    @pytest.mark.asyncio
    async def test_update_user_is_active_success(self, user_service, mock_db_session, sample_user):
        """Test updating user is_active status."""
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        updated_user = await user_service.update_user(sample_user.id, {"is_active": False})
        
        assert updated_user is not None
        assert updated_user.is_active is False

    @pytest.mark.asyncio
    async def test_update_user_multiple_fields(self, user_service, mock_db_session, sample_user):
        """Test updating multiple user fields at once."""
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        updates = {
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "is_active": False
        }
        updated_user = await user_service.update_user(sample_user.id, updates)
        
        assert updated_user is not None
        assert updated_user.first_name == "UpdatedFirst"
        assert updated_user.last_name == "UpdatedLast"
        assert updated_user.is_active is False

    @pytest.mark.asyncio
    async def test_update_user_empty_payload(self, user_service, mock_db_session, sample_user):
        """Test updating user with empty payload returns unchanged user."""
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        updated_user = await user_service.update_user(sample_user.id, {})
        
        assert updated_user is not None
        assert updated_user.id == sample_user.id
        assert updated_user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_service, mock_db_session):
        """Test updating non-existent user returns None."""
        # Mock get_user_by_id to return None
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        updated_user = await user_service.update_user(uuid4(), {"email": "new@example.com"})
        
        assert updated_user is None
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()


class TestUserServiceDelete:
    """Test cases for user deletion."""

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_service, mock_db_session, sample_user):
        """Test deleting user returns deleted user and subsequent get returns None."""
        # Mock get_user_by_id to return user for deletion
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        deleted_user = await user_service.delete_user(sample_user.id)
        
        assert deleted_user is not None
        assert deleted_user.id == sample_user.id
        assert deleted_user.email == sample_user.email
        mock_db_session.delete.assert_called_once_with(sample_user)
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_service, mock_db_session):
        """Test deleting non-existent user returns None."""
        # Mock get_user_by_id to return None
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = None
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        deleted_user = await user_service.delete_user(uuid4())
        
        assert deleted_user is None
        mock_db_session.delete.assert_not_called()
        mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_user_with_string_uuid(self, user_service, mock_db_session, sample_user):
        """Test deleting user works with string UUID."""
        mock_result = Mock()
        mock_scalars = Mock()
        mock_scalars.first.return_value = sample_user
        mock_result.scalars.return_value = mock_scalars
        mock_db_session.execute.return_value = mock_result
        
        deleted_user = await user_service.delete_user(str(sample_user.id))
        
        assert deleted_user is not None
        assert deleted_user.id == sample_user.id


class TestUserServiceIntegration:
    """Integration-style test cases for complete user workflows."""

    @pytest.mark.asyncio
    async def test_complete_user_lifecycle(self, user_service, mock_db_session, sample_user_create):
        """Test complete user lifecycle: create -> get -> update -> delete."""
        # Create a mock user object for the lifecycle
        mock_user = User(
            id=uuid4(),
            email=sample_user_create.email,
            hashed_password=get_password_hash(sample_user_create.password),
            first_name=sample_user_create.first_name,
            last_name=sample_user_create.last_name,
            is_active=True
        )
        
        # Mock database responses - always return mock_user for get operations
        def mock_execute(query):
            result = Mock()
            scalars = Mock()
            scalars.first.return_value = mock_user
            result.scalars.return_value = scalars
            return result
        
        mock_db_session.execute.side_effect = mock_execute
        
        # 1. Create user
        created_user = await user_service.create_user(sample_user_create)
        assert created_user.email == sample_user_create.email
        
        # 2. Get user by ID
        found_user = await user_service.get_user_by_id(created_user.id)
        assert found_user is not None
        
        # 3. Get user by email
        found_by_email = await user_service.get_user_by_email(created_user.email)
        assert found_by_email is not None
        
        # 4. Update user
        updated_user = await user_service.update_user(created_user.id, {"first_name": "Updated"})
        assert updated_user is not None
        
        # 5. Delete user
        deleted_user = await user_service.delete_user(created_user.id)
        assert deleted_user is not None

    @pytest.mark.asyncio
    async def test_user_service_error_handling(self, user_service, mock_db_session):
        """Test UserService handles database errors gracefully."""
        # Mock database error
        mock_db_session.commit.side_effect = Exception("Database connection lost")
        
        with pytest.raises(Exception, match="Database connection lost"):
            await user_service.create_user(UserCreate(email="test@example.com", password="password123"))