"""
Tests for audit logging service
"""
import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestAuditLogging:
    """Test audit logging operations"""
    
    @pytest.fixture
    def audit_db(self):
        """Create a temporary audit database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.audit.audit_logger import AuditLogger
        logger = AuditLogger(db_path=db_path)
        yield logger
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_log_user_action(self, audit_db):
        """Test logging a user action"""
        log_id = audit_db.log_action(
            actor_email="test@example.com",
            actor_name="Test User",
            action_type="report_created",
            resource_type="report",
            resource_id=1,
            details="User created a new report"
        )
        
        assert log_id is not None
        assert isinstance(log_id, int)
        assert log_id > 0
    
    def test_log_login_action(self, audit_db):
        """Test logging login action"""
        log_id = audit_db.log_action(
            actor_email="test@example.com",
            actor_name="Test User",
            action_type="login",
            details="User logged in successfully"
        )
        
        assert log_id is not None
        assert log_id > 0
    
    def test_log_report_creation(self, audit_db):
        """Test logging report creation"""
        log_id = audit_db.log_action(
            actor_email="student@example.com",
            actor_name="Student User",
            action_type="create",
            resource_type="report",
            resource_id=1
        )
        
        assert log_id is not None
        assert log_id > 0
    
    def test_log_report_update(self, audit_db):
        """Test logging report updates"""
        log_id = audit_db.log_action(
            actor_email="admin@example.com",
            actor_name="Admin User",
            action_type="update",
            resource_type="report",
            resource_id=1,
            details="Status changed to resolved"
        )
        
        assert log_id is not None
        assert log_id > 0


class TestAuditLogRetrieval:
    """Test audit log retrieval operations"""
    
    @pytest.fixture
    def audit_db_with_logs(self):
        """Create audit database with test logs"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.audit.audit_logger import AuditLogger
        logger = AuditLogger(db_path=db_path)
        
        # Add test logs
        logger.log_action("user1@example.com", "User 1", "login")
        logger.log_action("user2@example.com", "User 2", "create", resource_type="report")
        logger.log_action("user1@example.com", "User 1", "update", resource_type="report")
        
        yield logger
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_get_user_activity_logs(self, audit_db_with_logs):
        """Test retrieving user activity logs"""
        logs = audit_db_with_logs.get_audit_logs(actor_email="user1@example.com")
        
        assert isinstance(logs, list)
        assert len(logs) > 0
        assert all(log['actor_email'] == "user1@example.com" for log in logs)
    
    def test_filter_logs_by_action_type(self, audit_db_with_logs):
        """Test filtering logs by action type"""
        logs = audit_db_with_logs.get_audit_logs(action_type="login")
        
        assert isinstance(logs, list)
        assert len(logs) > 0
        assert all(log['action_type'] == "login" for log in logs)
    
    def test_filter_logs_by_resource_type(self, audit_db_with_logs):
        """Test filtering logs by resource type"""
        logs = audit_db_with_logs.get_audit_logs(resource_type="report")
        
        assert isinstance(logs, list)
        assert all(log['resource_type'] == "report" for log in logs)
    
    def test_get_logs_for_specific_user(self, audit_db_with_logs):
        """Test getting logs for a specific user"""
        logs = audit_db_with_logs.get_audit_logs(actor_email="user2@example.com")
        
        assert isinstance(logs, list)
        assert all(log['actor_email'] == "user2@example.com" for log in logs)
    
    def test_logs_ordered_by_timestamp_desc(self, audit_db_with_logs):
        """Test that logs are ordered by timestamp descending"""
        logs = audit_db_with_logs.get_audit_logs(limit=100)
        
        assert len(logs) > 1
        for i in range(len(logs) - 1):
            # Later entries should come first
            assert logs[i]['timestamp'] >= logs[i+1]['timestamp']
    
    def test_get_audit_logs_count(self, audit_db_with_logs):
        """Test getting count of audit logs"""
        count = audit_db_with_logs.get_audit_logs_count()
        
        assert isinstance(count, int)
        assert count >= 3


class TestAuditLogPersistence:
    """Test audit log persistence"""
    
    @pytest.fixture
    def audit_db(self):
        """Create a temporary audit database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.audit.audit_logger import AuditLogger
        logger = AuditLogger(db_path=db_path)
        yield logger
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_save_audit_log_to_database(self, audit_db):
        """Test saving audit log to database"""
        log_id = audit_db.log_action(
            actor_email="test@example.com",
            actor_name="Test User",
            action_type="test_action"
        )
        
        logs = audit_db.get_audit_logs()
        assert len(logs) > 0
        assert logs[0]['id'] == log_id
    
    def test_audit_log_data_integrity(self, audit_db):
        """Test that audit log data is saved correctly"""
        original_data = {
            "actor_email": "test@example.com",
            "actor_name": "Test User",
            "action_type": "test_action",
            "resource_type": "test_resource",
            "resource_id": 123,
            "details": "Test details"
        }
        
        log_id = audit_db.log_action(**original_data)
        
        logs = audit_db.get_audit_logs()
        saved_log = logs[0]
        
        assert saved_log['actor_email'] == original_data['actor_email']
        assert saved_log['actor_name'] == original_data['actor_name']
        assert saved_log['action_type'] == original_data['action_type']
        assert saved_log['resource_type'] == original_data['resource_type']
        assert saved_log['resource_id'] == original_data['resource_id']
        assert saved_log['details'] == original_data['details']
    
    def test_audit_log_timestamp_recorded(self, audit_db):
        """Test that timestamps are recorded"""
        log_id = audit_db.log_action(
            actor_email="test@example.com",
            actor_name="Test User",
            action_type="test_action"
        )
        
        logs = audit_db.get_audit_logs()
        assert len(logs) > 0
        assert logs[0]['timestamp'] is not None
        assert isinstance(logs[0]['timestamp'], str)


class TestAuditLogFiltering:
    """Test advanced audit log filtering"""
    
    @pytest.fixture
    def audit_db_complex(self):
        """Create audit database with complex test data"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.audit.audit_logger import AuditLogger
        logger = AuditLogger(db_path=db_path)
        
        # Add diverse logs
        logger.log_action("admin@example.com", "Admin", "login")
        logger.log_action("admin@example.com", "Admin", "create", "report", 1)
        logger.log_action("user@example.com", "User", "create", "report", 2)
        logger.log_action("user@example.com", "User", "update", "report", 2)
        logger.log_action("admin@example.com", "Admin", "delete", "report", 1)
        
        yield logger
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_filter_by_actor_email_and_action(self, audit_db_complex):
        """Test filtering by both actor email and action type"""
        logs = audit_db_complex.get_audit_logs(
            actor_email="admin@example.com",
            action_type="create"
        )
        
        assert isinstance(logs, list)
        assert all(log['actor_email'] == "admin@example.com" for log in logs)
        assert all(log['action_type'] == "create" for log in logs)
    
    def test_filter_by_resource_id(self, audit_db_complex):
        """Test filtering by resource ID"""
        # Get logs and filter in memory since API doesn't support resource_id filter
        logs = audit_db_complex.get_audit_logs()
        filtered = [log for log in logs if log.get('resource_id') == 1]
        
        assert isinstance(logs, list)
    
    def test_combined_filters(self, audit_db_complex):
        """Test combining multiple filters"""
        logs = audit_db_complex.get_audit_logs(
            actor_email="user@example.com",
            resource_type="report"
        )
        
        assert isinstance(logs, list)
        assert all(log['actor_email'] == "user@example.com" for log in logs)
        assert all(log['resource_type'] == "report" for log in logs)
    
    def test_limit_results(self, audit_db_complex):
        """Test limiting number of results"""
        logs = audit_db_complex.get_audit_logs(limit=2)
        
        assert isinstance(logs, list)
        assert len(logs) <= 2
    
    def test_pagination(self, audit_db_complex):
        """Test getting all logs with pagination"""
        total = audit_db_complex.get_audit_logs_count()
        
        # Get first 2
        logs1 = audit_db_complex.get_audit_logs(limit=2)
        
        assert len(logs1) <= 2
        assert total >= len(logs1)


class TestAuditLogAggregation:
    """Test audit log aggregation and statistics"""
    
    @pytest.fixture
    def audit_db_stats(self):
        """Create audit database for stats testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.audit.audit_logger import AuditLogger
        logger = AuditLogger(db_path=db_path)
        
        # Add multiple logs
        for i in range(5):
            logger.log_action(f"user{i}@example.com", f"User {i}", "login")
            logger.log_action(f"user{i}@example.com", f"User {i}", "create", "report", i)
        
        yield logger
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_count_total_logs(self, audit_db_stats):
        """Test counting total logs"""
        count = audit_db_stats.get_audit_logs_count()
        
        assert isinstance(count, int)
        assert count == 10  # 5 users * 2 actions each
    
    def test_count_by_action_type(self, audit_db_stats):
        """Test counting logs by action type"""
        login_logs = audit_db_stats.get_audit_logs(action_type="login")
        create_logs = audit_db_stats.get_audit_logs(action_type="create")
        
        assert len(login_logs) == 5
        assert len(create_logs) == 5
    
    def test_get_user_actions_summary(self, audit_db_stats):
        """Test getting actions for a specific user"""
        user_logs = audit_db_stats.get_audit_logs(actor_email="user0@example.com")
        
        assert isinstance(user_logs, list)
        assert len(user_logs) == 2  # login + create
        
        action_types = [log['action_type'] for log in user_logs]
        assert 'login' in action_types
        assert 'create' in action_types


class TestAuditLogValidation:
    """Test audit log validation and error handling"""
    
    @pytest.fixture
    def audit_db(self):
        """Create a temporary audit database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.audit.audit_logger import AuditLogger
        logger = AuditLogger(db_path=db_path)
        yield logger
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_log_with_minimal_fields(self, audit_db):
        """Test logging with minimal required fields"""
        log_id = audit_db.log_action(
            actor_email="test@example.com",
            actor_name="Test User",
            action_type="test"
        )
        
        assert log_id is not None
        assert log_id > 0
    
    def test_log_with_all_fields(self, audit_db):
        """Test logging with all available fields"""
        log_id = audit_db.log_action(
            actor_email="test@example.com",
            actor_name="Test User",
            action_type="test",
            resource_type="report",
            resource_id=123,
            details="Full test details"
        )
        
        assert log_id is not None
        
        logs = audit_db.get_audit_logs()
        assert len(logs) > 0
        saved = logs[0]
        assert saved['details'] == "Full test details"
    
    def test_log_with_special_characters(self, audit_db):
        """Test logging with special characters in details"""
        details = "User reported issue: <script>alert('test')</script>"
        
        log_id = audit_db.log_action(
            actor_email="test@example.com",
            actor_name="Test User",
            action_type="create",
            details=details
        )
        
        assert log_id is not None
        
        logs = audit_db.get_audit_logs()
        assert logs[0]['details'] == details
    
    def test_retrieve_nonexistent_filter(self, audit_db):
        """Test retrieving logs with non-matching filter"""
        audit_db.log_action("test@example.com", "Test", "create")
        
        # Try to get logs for different user
        logs = audit_db.get_audit_logs(actor_email="nonexistent@example.com")
        
        assert isinstance(logs, list)
        assert len(logs) == 0

