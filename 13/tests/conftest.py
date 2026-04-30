import pytest
import sys
import os
from unittest.mock import Mock

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import schemas


@pytest.fixture
def mock_db_session():
    """Fixture to provide a mock database session"""
    return Mock()


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