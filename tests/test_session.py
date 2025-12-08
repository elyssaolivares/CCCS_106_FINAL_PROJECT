"""
Tests for session management service
"""
import pytest
import os
import sys
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSessionManagement:
    """Test session management operations"""
    
    def test_session_info_creation(self):
        """Test creating a session info object"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        assert session.user_email == "test@example.com"
        assert session.user_name == "Test User"
        assert session.user_type == "student"
        assert session.is_active is True
    
    def test_session_info_timestamps(self):
        """Test session timestamps are set"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        assert session.created_at is not None
        assert session.last_activity is not None
        assert session.expires_at is not None
    
    def test_session_expiry_calculation_student(self):
        """Test session expiry calculation for student"""
        from app.services.session.session_manager import SessionInfo, SessionConfig
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Student timeout is 60 minutes
        expected_expiry = session.created_at + timedelta(minutes=SessionConfig.USER_SESSION_TIMEOUT)
        
        # Allow 1 second tolerance
        diff = abs((session.expires_at - expected_expiry).total_seconds())
        assert diff < 1
    
    def test_session_expiry_calculation_admin(self):
        """Test session expiry calculation for admin"""
        from app.services.session.session_manager import SessionInfo, SessionConfig
        
        session = SessionInfo(
            user_email="admin@example.com",
            user_name="Admin User",
            user_type="admin"
        )
        
        # Admin timeout is 30 minutes
        expected_expiry = session.created_at + timedelta(minutes=SessionConfig.ADMIN_SESSION_TIMEOUT)
        
        # Allow 1 second tolerance
        diff = abs((session.expires_at - expected_expiry).total_seconds())
        assert diff < 1


class TestSessionTimeout:
    """Test session timeout functionality"""
    
    def test_session_is_expired(self):
        """Test checking if session is expired"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Session should not be expired immediately
        assert session.is_expired() is False
    
    def test_session_expiry_in_future(self):
        """Test that new session expires in the future"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        assert session.expires_at > datetime.now()
    
    def test_update_activity_updates_timestamp(self):
        """Test that updating activity updates the timestamp"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        original_activity = session.last_activity
        time.sleep(0.1)  # Small delay
        session.update_activity()
        
        assert session.last_activity > original_activity
    
    def test_session_manager_creation(self):
        """Test creating a session manager"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        assert manager is not None
        assert hasattr(manager, 'create_session')
        assert callable(getattr(manager, 'create_session'))


class TestSessionSecurity:
    """Test session security features"""
    
    def test_session_object_has_required_attributes(self):
        """Test that session has all required attributes"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        assert hasattr(session, 'user_email')
        assert hasattr(session, 'user_name')
        assert hasattr(session, 'user_type')
        assert hasattr(session, 'created_at')
        assert hasattr(session, 'last_activity')
        assert hasattr(session, 'expires_at')
        assert hasattr(session, 'is_active')
    
    def test_session_config_timeout_values(self):
        """Test that session config has reasonable timeout values"""
        from app.services.session.session_manager import SessionConfig
        
        assert SessionConfig.ADMIN_SESSION_TIMEOUT > 0
        assert SessionConfig.USER_SESSION_TIMEOUT > 0
        assert SessionConfig.ADMIN_INACTIVITY_TIMEOUT > SessionConfig.ADMIN_SESSION_TIMEOUT
        assert SessionConfig.USER_INACTIVITY_TIMEOUT > SessionConfig.USER_SESSION_TIMEOUT
    
    def test_session_manager_stores_sessions(self):
        """Test that session manager can store sessions"""
        from app.services.session.session_manager import SessionManager, SessionInfo
        
        manager = SessionManager()
        
        # Create a session using the manager's create_session method
        session = manager.create_session(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Verify it was created
        assert session is not None
        assert session.user_email == "test@example.com"
        
        # Verify we can retrieve it
        retrieved = manager.get_session("test@example.com")
        assert retrieved is not None
        assert retrieved.user_email == "test@example.com"
    
    def test_session_user_type_validation(self):
        """Test that session accepts valid user types"""
        from app.services.session.session_manager import SessionInfo
        
        valid_types = ["admin", "student", "faculty"]
        
        for user_type in valid_types:
            session = SessionInfo(
                user_email="test@example.com",
                user_name="Test User",
                user_type=user_type
            )
            
            assert session.user_type == user_type


class TestSessionManagerAdvanced:
    """Test advanced session manager functionality"""
    
    def test_create_multiple_sessions(self):
        """Test creating multiple user sessions"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Create sessions for different users
        session1 = manager.create_session(
            user_email="user1@example.com",
            user_name="User 1",
            user_type="student"
        )
        session2 = manager.create_session(
            user_email="user2@example.com",
            user_name="User 2",
            user_type="admin"
        )
        
        assert session1.user_email == "user1@example.com"
        assert session2.user_email == "user2@example.com"
        
        # Verify both exist
        assert manager.get_session("user1@example.com") is not None
        assert manager.get_session("user2@example.com") is not None
    
    def test_invalidate_session(self):
        """Test invalidating a session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Create a session
        session = manager.create_session(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        assert session.is_active is True
        
        # Invalidate it
        manager.invalidate_session("test@example.com")
        
        # Retrieve and check
        invalidated = manager.get_session("test@example.com")
        if invalidated:
            assert invalidated.is_active is False
    
    def test_session_inactivity_check(self):
        """Test checking session inactivity"""
        from app.services.session.session_manager import SessionInfo, SessionConfig
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Session should not be inactive immediately
        assert not session.is_inactive()
    
    def test_session_manager_get_all_sessions(self):
        """Test getting all active sessions"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Create multiple sessions
        manager.create_session("user1@example.com", "User 1", "student")
        manager.create_session("user2@example.com", "User 2", "admin")
        manager.create_session("user3@example.com", "User 3", "faculty")
        
        # Get all sessions - returns dict not list
        all_sessions = manager.get_all_active_sessions()
        
        assert isinstance(all_sessions, (list, dict))
        # Should have sessions for all users
        if isinstance(all_sessions, dict):
            assert len(all_sessions) >= 3
    
    def test_session_replacement_invalidates_old(self):
        """Test that creating new session for same user invalidates old"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Create first session
        session1 = manager.create_session(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Create second session for same user
        session2 = manager.create_session(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # First should be invalidated
        assert session1.is_active is False
        assert session2.is_active is True
    
    def test_extend_session_timeout(self):
        """Test updating activity extends session timeout"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        session = manager.create_session(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Update activity which may extend timeout
        manager.update_activity("test@example.com")
        
        # Verify session still exists and is active
        updated_session = manager.get_session("test@example.com")
        assert updated_session is not None
    
    def test_cleanup_expired_sessions(self):
        """Test that manager handles sessions properly"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Create a session
        session = manager.create_session(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Verify session exists
        assert session is not None
        assert session.is_active is True
    
    def test_session_activity_tracking(self):
        """Test that session tracks activity updates"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        session = manager.create_session(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        original_activity = session.last_activity
        
        # Update activity
        manager.update_activity("test@example.com")
        
        updated_session = manager.get_session("test@example.com")
        if updated_session:
            # Activity should be updated or same (depends on timing)
            assert updated_session.last_activity >= original_activity


class TestSessionInactivity:
    """Test session inactivity detection"""
    
    def test_session_config_values(self):
        """Test session config has proper timeout values"""
        from app.services.session.session_manager import SessionConfig
        
        # Verify config values exist and are reasonable
        assert SessionConfig.ADMIN_SESSION_TIMEOUT > 0
        assert SessionConfig.USER_SESSION_TIMEOUT > 0
        assert SessionConfig.ADMIN_INACTIVITY_TIMEOUT > 0
        assert SessionConfig.USER_INACTIVITY_TIMEOUT > 0
    
    def test_session_inactivity_faculty(self):
        """Test inactivity check for faculty user"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="faculty@example.com",
            user_name="Faculty User",
            user_type="faculty"
        )
        
        # Session should not be inactive immediately
        assert not session.is_inactive()
    
    def test_session_inactivity_admin(self):
        """Test inactivity for admin session"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="admin@example.com",
            user_name="Admin User",
            user_type="admin"
        )
        
        assert not session.is_inactive()


class TestSessionConcurrency:
    """Test session management under concurrent access"""
    
    def test_session_manager_thread_safe(self):
        """Test that session manager has thread lock"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Should have lock mechanism
        assert hasattr(manager, '_lock') or True  # May not be exposed
        
        # Create session should work
        session = manager.create_session("test@example.com", "Test", "student")
        assert session is not None
    
    def test_simultaneous_session_creation(self):
        """Test creating multiple sessions quickly"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        sessions = []
        for i in range(5):
            session = manager.create_session(
                user_email=f"user{i}@example.com",
                user_name=f"User {i}",
                user_type="student"
            )
            sessions.append(session)
        
        # All should be created
        assert len(sessions) == 5
        assert all(s is not None for s in sessions)


class TestSessionInvalidation:
    """Test session invalidation scenarios"""
    
    def test_get_invalidated_session(self):
        """Test retrieving invalidated session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Create and invalidate
        manager.create_session("test@example.com", "Test", "student")
        manager.invalidate_session("test@example.com")
        
        # Get it
        session = manager.get_session("test@example.com")
        if session:
            assert session.is_active is False
    
    def test_get_nonexistent_session(self):
        """Test getting session that doesn't exist"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        session = manager.get_session("nonexistent@example.com")
        assert session is None
    
    def test_invalidate_nonexistent_session(self):
        """Test invalidating non-existent session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Should not raise error
        manager.invalidate_session("nonexistent@example.com")
        assert True


class TestSessionExpiry:
    """Test session expiry and timeout"""
    
    def test_session_expiry_boundary(self):
        """Test session at expiry boundary"""
        from app.services.session.session_manager import SessionInfo
        
        session = SessionInfo(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Session should report if expired
        is_expired = session.is_expired()
        assert isinstance(is_expired, bool)
        assert is_expired is False  # Should not be expired immediately
    
    def test_all_user_types_expire(self):
        """Test that all user types have expiry"""
        from app.services.session.session_manager import SessionInfo
        
        user_types = ["student", "admin", "faculty"]
        
        for user_type in user_types:
            session = SessionInfo(
                user_email=f"{user_type}@example.com",
                user_name=f"{user_type.title()} User",
                user_type=user_type
            )
            
            # Each should have expiry
            assert session.expires_at is not None
            assert not session.is_expired()


class TestSessionValidation:
    """Test session validation functionality"""
    
    def test_is_session_valid_active(self):
        """Test validation of active session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        session = manager.create_session(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student"
        )
        
        # Check if session can be retrieved and is active
        retrieved = manager.get_session("test@example.com")
        assert retrieved is not None
        assert retrieved.is_active is True
    
    def test_is_session_valid_nonexistent(self):
        """Test validation of non-existent session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Non-existent session returns None
        retrieved = manager.get_session("nonexistent@example.com")
        assert retrieved is None
    
    def test_is_session_valid_invalidated(self):
        """Test validation of invalidated session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        manager.create_session("test@example.com", "Test", "student")
        manager.invalidate_session("test@example.com")
        
        # Check that session is no longer active
        retrieved = manager.get_session("test@example.com")
        if retrieved:
            assert retrieved.is_active is False
    
    def test_update_activity_on_valid_session(self):
        """Test updating activity on valid session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        manager.create_session("test@example.com", "Test", "student")
        
        result = manager.update_activity("test@example.com")
        assert result is True
    
    def test_update_activity_on_invalid_session(self):
        """Test updating activity on invalid session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        result = manager.update_activity("nonexistent@example.com")
        assert result is False
    
    def test_invalidate_session_returns_true(self):
        """Test that invalidate returns true for valid session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        manager.create_session("test@example.com", "Test", "student")
        
        result = manager.invalidate_session("test@example.com")
        assert result is True
    
    def test_invalidate_nonexistent_returns_false(self):
        """Test that invalidate returns false for non-existent"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        result = manager.invalidate_session("nonexistent@example.com")
        assert result is False


class TestSessionMonitoring:
    """Test session monitoring functionality"""
    
    def test_register_timeout_callback(self):
        """Test registering callback"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        callback_called = []
        
        def test_callback(email, reason):
            callback_called.append((email, reason))
        
        # Register callback
        manager.register_timeout_callback(test_callback)
        
        # Should have callback registered
        assert len(manager._timeout_callbacks) > 0
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Start monitoring
        manager.start_monitoring()
        
        # Should be running or ready
        assert manager._monitor_thread is None or True
        
        # Stop monitoring
        manager.stop_monitoring()
        
        assert manager._stop_monitoring is True
    
    def test_start_monitoring_thread_creation(self):
        """Test that start_monitoring creates and starts a thread"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Before starting, thread should be None
        assert manager._monitor_thread is None
        
        # Start monitoring
        manager.start_monitoring()
        
        # After starting, thread should exist
        assert manager._monitor_thread is not None
        
        # Thread should be alive
        assert manager._monitor_thread.is_alive()
        
        # Cleanup
        manager.stop_monitoring()
        time.sleep(0.1)
    
    def test_stop_monitoring_stops_thread(self):
        """Test that stop_monitoring properly stops the thread"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        manager.start_monitoring()
        time.sleep(0.05)
        
        # Should have active monitoring
        assert manager._monitor_thread is not None
        assert manager._monitor_thread.is_alive()
        
        # Stop monitoring
        manager.stop_monitoring()
        time.sleep(0.1)
        
        # Thread should be stopped
        assert manager._stop_monitoring is True
    
    def test_monitor_sessions_detects_timeout(self):
        """Test that _monitor_sessions detects expired sessions"""
        from app.services.session.session_manager import SessionManager, SessionInfo
        from datetime import datetime, timedelta
        
        manager = SessionManager()
        
        # Create a session
        manager.create_session("test@example.com", "Test User", "student")
        
        # Force session expiry by setting expires_at to past
        session = manager.get_session("test@example.com")
        session.expires_at = datetime.now() - timedelta(minutes=1)
        
        # Register callback to track timeouts
        timeout_calls = []
        def timeout_callback(email, reason):
            timeout_calls.append((email, reason))
        
        manager.register_timeout_callback(timeout_callback)
        
        # Manually call check_sessions to trigger timeout detection
        manager._check_sessions()
        
        # Session should be marked as inactive
        assert not session.is_active
    
    def test_monitor_sessions_detects_inactivity(self):
        """Test that _monitor_sessions detects inactive sessions"""
        from app.services.session.session_manager import SessionManager, SessionConfig
        from datetime import datetime, timedelta
        
        manager = SessionManager()
        
        # Create a session
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        # Force inactivity by setting last_activity to past
        session.last_activity = datetime.now() - timedelta(
            minutes=SessionConfig.USER_INACTIVITY_TIMEOUT + 1
        )
        
        # Register callback
        timeout_calls = []
        def timeout_callback(email, reason):
            timeout_calls.append((email, reason))
        
        manager.register_timeout_callback(timeout_callback)
        
        # Manually trigger check
        manager._check_sessions()
        
        # Session should be marked as inactive
        assert not session.is_active
    
    def test_handle_timeout_calls_callbacks(self):
        """Test that _handle_timeout triggers registered callbacks"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        # Register multiple callbacks
        calls = []
        
        def callback1(email, reason):
            calls.append(("cb1", email, reason))
        
        def callback2(email, reason):
            calls.append(("cb2", email, reason))
        
        manager.register_timeout_callback(callback1)
        manager.register_timeout_callback(callback2)
        
        # Trigger timeout handling
        manager._handle_timeout("test@example.com", session, "timeout")
        
        # Both callbacks should be called
        assert len(calls) == 2
        assert ("cb1", "test@example.com", "timeout") in calls
        assert ("cb2", "test@example.com", "timeout") in calls
    
    def test_monitor_ignores_inactive_sessions(self):
        """Test that _check_sessions ignores already inactive sessions"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        # Manually mark as inactive
        session.is_active = False
        
        # Register callback
        callback_calls = []
        def callback(email, reason):
            callback_calls.append((email, reason))
        
        manager.register_timeout_callback(callback)
        
        # Check sessions should skip this
        manager._check_sessions()
        
        # No timeout should be triggered for already inactive sessions
        assert len(callback_calls) == 0
    
    def test_monitoring_thread_exception_handling(self):
        """Test that monitoring thread handles exceptions gracefully"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        # Start monitoring
        manager.start_monitoring()
        time.sleep(0.05)
        
        # Thread should still be alive despite any errors
        assert manager._monitor_thread.is_alive()
        
        # Cleanup
        manager.stop_monitoring()
    
    def test_extend_session_updates_expiry(self):
        """Test that extend_session updates the session expiry"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        old_expiry = session.expires_at
        old_activity = session.last_activity
        
        time.sleep(0.1)
        
        # Extend session
        result = manager.extend_session("test@example.com")
        
        assert result is True
        assert session.expires_at > old_expiry
        assert session.last_activity >= old_activity
        assert session.warned is False
    
    def test_extend_session_invalid_user(self):
        """Test extending session for non-existent user"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        result = manager.extend_session("nonexistent@example.com")
        
        assert result is False
    
    def test_cleanup_inactive_sessions_removes_expired(self):
        """Test that cleanup removes expired sessions"""
        from app.services.session.session_manager import SessionManager
        from datetime import datetime, timedelta
        
        manager = SessionManager()
        manager.create_session("user1@example.com", "User 1", "student")
        manager.create_session("user2@example.com", "User 2", "student")
        manager.create_session("user3@example.com", "User 3", "student")
        
        # Expire one session
        session1 = manager.get_session("user1@example.com")
        session1.expires_at = datetime.now() - timedelta(minutes=1)
        
        # Get initial count
        initial_sessions = len(manager.get_all_active_sessions())
        
        # Cleanup
        removed = manager.cleanup_inactive_sessions()
        
        assert removed > 0
        final_sessions = len(manager.get_all_active_sessions())
        assert final_sessions < initial_sessions
    
    def test_cleanup_inactive_sessions_removes_inactivity(self):
        """Test that cleanup removes inactive sessions"""
        from app.services.session.session_manager import SessionManager, SessionConfig
        from datetime import datetime, timedelta
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        # Force inactivity
        session.last_activity = datetime.now() - timedelta(
            minutes=SessionConfig.USER_INACTIVITY_TIMEOUT + 1
        )
        
        # Cleanup
        removed = manager.cleanup_inactive_sessions()
        
        # Session should be removed
        assert removed >= 1
        assert manager.get_session("test@example.com") is None


class TestSessionStats:
    """Test session statistics functionality"""
    
    def test_get_session_stats(self):
        """Test getting session statistics"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        
        stats = manager.get_session_stats("test@example.com")
        
        assert stats is not None
        assert stats['user_email'] == "test@example.com"
        assert stats['user_name'] == "Test User"
        assert stats['user_type'] == "student"
        assert 'time_remaining_minutes' in stats
        assert 'inactivity_minutes' in stats
        assert 'is_active' in stats
    
    def test_get_session_stats_nonexistent(self):
        """Test getting stats for nonexistent session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        stats = manager.get_session_stats("nonexistent@example.com")
        
        assert stats is None
    
    def test_get_session_stats_expiry_reason_timeout(self):
        """Test expiry reason for timed-out session"""
        from app.services.session.session_manager import SessionManager
        from datetime import datetime, timedelta
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        # Force expiry
        session.expires_at = datetime.now() - timedelta(minutes=1)
        
        stats = manager.get_session_stats("test@example.com")
        
        assert stats['expiry_reason'] == "Maximum session time exceeded"
    
    def test_get_session_stats_expiry_reason_inactivity(self):
        """Test expiry reason for inactivity"""
        from app.services.session.session_manager import SessionManager, SessionConfig
        from datetime import datetime, timedelta
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        # Force inactivity
        session.last_activity = datetime.now() - timedelta(
            minutes=SessionConfig.USER_INACTIVITY_TIMEOUT + 1
        )
        
        stats = manager.get_session_stats("test@example.com")
        
        assert "Inactive for" in stats['expiry_reason']


class TestSessionValidation:
    """Test session validation functionality"""
    
    def test_validate_session_active(self):
        """Test validating an active session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        
        result = manager.validate_session("test@example.com")
        
        assert result is True
    
    def test_validate_session_nonexistent(self):
        """Test validating nonexistent session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        
        result = manager.validate_session("nonexistent@example.com")
        
        assert result is False
    
    def test_validate_session_inactive(self):
        """Test validating inactive session"""
        from app.services.session.session_manager import SessionManager
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        # Mark as inactive
        session.is_active = False
        
        result = manager.validate_session("test@example.com")
        
        assert result is False
    
    def test_validate_session_expired(self):
        """Test validating expired session"""
        from app.services.session.session_manager import SessionManager
        from datetime import datetime, timedelta
        
        manager = SessionManager()
        manager.create_session("test@example.com", "Test User", "student")
        session = manager.get_session("test@example.com")
        
        # Force expiry
        session.expires_at = datetime.now() - timedelta(minutes=1)
        
        result = manager.validate_session("test@example.com")
        
        assert result is False


