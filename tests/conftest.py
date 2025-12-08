"""
Shared pytest configuration and fixtures
"""
import pytest
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_user_data():
    """Fixture providing mock user data"""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "role": "student",
        "picture": None,
        "created_at": "2025-12-08 10:00:00",
        "updated_at": "2025-12-08 10:00:00"
    }


@pytest.fixture
def mock_admin_data():
    """Fixture providing mock admin user data"""
    return {
        "email": "admin@example.com",
        "name": "Admin User",
        "role": "admin",
        "picture": None,
        "created_at": "2025-12-08 10:00:00",
        "updated_at": "2025-12-08 10:00:00"
    }


@pytest.fixture
def mock_report_data():
    """Fixture providing mock report data"""
    return {
        "id": 1,
        "user_email": "test@example.com",
        "title": "Test Report",
        "description": "This is a test report",
        "category": "Academic",
        "status": "Open",
        "created_at": "2025-12-08 10:00:00",
        "updated_at": "2025-12-08 10:00:00"
    }


@pytest.fixture
def mock_session_data():
    """Fixture providing mock session data"""
    return {
        "user_email": "test@example.com",
        "session_id": "mock_session_123",
        "created_at": "2025-12-08 10:00:00",
        "last_activity": "2025-12-08 10:30:00"
    }


@pytest.fixture
def mock_audit_log():
    """Fixture providing mock audit log data"""
    return {
        "id": 1,
        "user_email": "test@example.com",
        "action": "login",
        "details": {"ip": "192.168.1.1", "device": "Web Browser"},
        "timestamp": "2025-12-08 10:00:00"
    }


@pytest.fixture
def temp_database(tmp_path):
    """Fixture providing a temporary database for testing"""
    db_path = tmp_path / "test.db"
    return str(db_path)


@pytest.fixture
def mock_file_upload():
    """Fixture providing mock file upload data"""
    return {
        "filename": "test_image.jpg",
        "content_type": "image/jpeg",
        "size": 1024,
        "content": b"fake_image_data"
    }
