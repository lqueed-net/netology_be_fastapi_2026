import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import sys
import os
import asyncio

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import schemas
from routers import users


# Fixtures
@pytest.fixture
def mock_db_session():
    """Fixture to provide a mock database session"""
    session = AsyncMock()
    return session


@pytest.fixture
def sample_user_data():
    """Fixture to provide sample user creation data"""
    return schemas.UserCreate(
        email="test@example.com",
        password="password123",
        role=schemas.UserRole.USER
    )


@pytest.fixture
def sample_admin_user():
    """Fixture to provide a sample admin user"""
    user = Mock()
    user.id = 1
    user.email = "admin@example.com"
    user.role = schemas.UserRole.ADMIN
    return user


@pytest.fixture
def sample_regular_user():
    """Fixture to provide a sample regular user"""
    user = Mock()
    user.id = 2
    user.email = "user@example.com"
    user.role = schemas.UserRole.USER
    return user


@pytest.fixture
def sample_user_list():
    """Fixture to provide a list of sample users"""
    return [
        Mock(id=1, email="user1@example.com", role=schemas.UserRole.USER),
        Mock(id=2, email="user2@example.com", role=schemas.UserRole.ADMIN),
        Mock(id=3, email="user3@example.com", role=schemas.UserRole.USER),
    ]


# Test cases
class TestUserRegistration:
    """Test cases for user registration endpoint"""

    @pytest.mark.asyncio
    async def test_register_new_user_success(self, sample_user_data, mock_db_session):
        """Test successful user registration"""
        # Arrange
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None  # No existing user
        mock_db_session.execute.return_value = mock_result

        # Mock the new user object
        mock_new_user = Mock()
        mock_new_user.id = 1
        mock_new_user.email = "test@example.com"
        mock_new_user.role = schemas.UserRole.USER

        # Configure the mock session to return the user when refreshed
        mock_db_session.refresh = AsyncMock(return_value=None)

        # Act
        with patch('auth.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"
            result = await users.register(sample_user_data, mock_db_session)

            # Assert
            assert mock_db_session.execute.await_count == 1
            assert mock_hash.called
            assert mock_db_session.add.called
            assert mock_db_session.commit.await_count == 1
            assert mock_db_session.refresh.await_count == 1

            # Check that the returned user has correct attributes
            assert result.email == "test@example.com"
            assert result.role == schemas.UserRole.USER

    @pytest.mark.asyncio
    async def test_register_existing_email_raises_exception(self, sample_user_data, mock_db_session):
        """Test that registering with existing email raises HTTPException"""
        # Arrange
        mock_existing_user = Mock()
        mock_existing_user.email = "existing@example.com"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_existing_user
        mock_db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await users.register(sample_user_data, mock_db_session)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"


class TestUserLogin:
    """Test cases for user login endpoint"""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_db_session):
        """Test successful user login"""
        # Arrange
        form_data = OAuth2PasswordRequestForm(
            username="test@example.com",
            password="correct_password"
        )

        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_correct_password"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act
        with patch('auth.verify_password') as mock_verify, \
             patch('auth.create_access_token') as mock_token:
            mock_verify.return_value = True
            mock_token.return_value = "fake_access_token"

            result = await users.login(form_data, mock_db_session)

            # Assert
            assert mock_db_session.execute.await_count == 1
            assert mock_verify.called
            assert mock_token.called
            assert result["access_token"] == "fake_access_token"
            assert result["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials_raises_exception(self, mock_db_session):
        """Test that invalid credentials raise HTTPException"""
        # Arrange
        form_data = OAuth2PasswordRequestForm(
            username="test@example.com",
            password="wrong_password"
        )

        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_correct_password"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        # Act & Assert
        with patch('auth.verify_password') as mock_verify:
            mock_verify.return_value = False  # Password verification fails

            with pytest.raises(HTTPException) as exc_info:
                await users.login(form_data, mock_db_session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Incorrect password or email"
        assert exc_info.value.headers == {'WWW-Authenticate': 'Bearer'}

    @pytest.mark.asyncio
    async def test_login_nonexistent_user_raises_exception(self, mock_db_session):
        """Test that login with nonexistent user raises HTTPException"""
        # Arrange
        form_data = OAuth2PasswordRequestForm(
            username="nonexistent@example.com",
            password="any_password"
        )

        # Mock database session with no user found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await users.login(form_data, mock_db_session)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Incorrect password or email"
        assert exc_info.value.headers == {'WWW-Authenticate': 'Bearer'}


class TestUserMeEndpoints:
    """Test cases for /me endpoints"""

    @pytest.mark.asyncio
    async def test_read_user_me_success(self, sample_regular_user):
        """Test successful retrieval of current user"""
        # Act
        result = await users.read_user_me(sample_regular_user)

        # Assert
        assert result == sample_regular_user

    @pytest.mark.asyncio
    async def test_update_user_me_email_success(self, sample_regular_user, mock_db_session):
        """Test successful update of user email"""
        # Arrange
        user_update = schemas.UserUpdate(email="newemail@example.com")
        sample_regular_user.id = 1
        sample_regular_user.email = "oldemail@example.com"

        # Mock database session with no existing user with new email
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None  # No conflict
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await users.update_user_me(user_update, sample_regular_user, mock_db_session)

        # Assert
        assert mock_db_session.execute.await_count == 1
        assert mock_db_session.commit.await_count == 1
        assert mock_db_session.refresh.await_count == 1
        assert result.email == "newemail@example.com"

    @pytest.mark.asyncio
    async def test_update_user_me_password_success(self, sample_regular_user, mock_db_session):
        """Test successful update of user password"""
        # Arrange
        user_update = schemas.UserUpdate(password="newpassword123")
        sample_regular_user.email = "test@example.com"

        # Act
        with patch('auth.get_password_hash') as mock_hash:
            mock_hash.return_value = "new_hashed_password"
            result = await users.update_user_me(user_update, sample_regular_user, mock_db_session)

            # Assert
            assert mock_hash.called
            assert mock_db_session.commit.await_count == 1
            assert mock_db_session.refresh.await_count == 1
            assert sample_regular_user.hashed_password == "new_hashed_password"

    @pytest.mark.asyncio
    async def test_update_user_me_email_conflict_raises_exception(self, sample_regular_user, mock_db_session):
        """Test that updating to existing email raises HTTPException"""
        # Arrange
        user_update = schemas.UserUpdate(email="existing@example.com")
        sample_regular_user.id = 1
        sample_regular_user.email = "current@example.com"

        # Mock database session with existing user having the new email
        mock_existing_user = Mock()
        mock_existing_user.id = 2  # Different user ID
        mock_existing_user.email = "existing@example.com"
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_existing_user
        mock_db_session.execute.return_value = mock_result

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await users.update_user_me(user_update, sample_regular_user, mock_db_session)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Email already registered"

    @pytest.mark.asyncio
    async def test_update_user_me_no_changes(self, sample_regular_user, mock_db_session):
        """Test update with no changes"""
        # Arrange
        user_update = schemas.UserUpdate()  # Empty update
        sample_regular_user.email = "test@example.com"
        sample_regular_user.role = schemas.UserRole.USER

        # Act
        result = await users.update_user_me(user_update, sample_regular_user, mock_db_session)

        # Assert
        assert mock_db_session.commit.await_count == 1
        assert mock_db_session.refresh.await_count == 1
        assert result == sample_regular_user


class TestReadUsers:
    """Test cases for reading all users endpoint"""

    @pytest.mark.asyncio
    async def test_read_users_success_as_admin(self, sample_admin_user, sample_user_list, mock_db_session):
        """Test successful retrieval of users list as admin"""
        # Arrange
        sample_admin_user.role = schemas.UserRole.ADMIN

        # Mock database session with list of users
        mock_result = Mock()
        mock_result.scalars().all.return_value = sample_user_list
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await users.read_users(skip=0, limit=10, current_user=sample_admin_user, session=mock_db_session)

        # Assert
        assert mock_db_session.execute.await_count == 1
        assert len(result) == 3
        assert result == sample_user_list

    @pytest.mark.asyncio
    async def test_read_users_forbidden_for_non_admin(self, sample_regular_user, mock_db_session):
        """Test that non-admin users cannot access users list"""
        # Arrange
        sample_regular_user.role = schemas.UserRole.USER  # Regular user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await users.read_users(skip=0, limit=10, current_user=sample_regular_user, session=mock_db_session)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not enough permissions"

    @pytest.mark.asyncio
    async def test_read_users_with_pagination(self, sample_admin_user, mock_db_session):
        """Test users retrieval with pagination parameters"""
        # Arrange
        sample_admin_user.role = schemas.UserRole.ADMIN

        # Mock database session
        mock_users = [Mock()]
        mock_result = Mock()
        mock_result.scalars().all.return_value = mock_users
        mock_db_session.execute.return_value = mock_result

        # Act
        result = await users.read_users(skip=5, limit=20, current_user=sample_admin_user, session=mock_db_session)

        # Assert
        # Check that the database call includes the pagination parameters
        assert mock_db_session.execute.await_count == 1
        assert result == mock_users