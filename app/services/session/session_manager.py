import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
import json


class SessionConfig:
    # Session timeout durations (in minutes)
    ADMIN_SESSION_TIMEOUT = 30  # 30 minutes for admins
    USER_SESSION_TIMEOUT = 60   # 60 minutes for regular users
    
    # Inactivity timeout (activity-based expiration) - MUST be longer than SESSION_TIMEOUT
    ADMIN_INACTIVITY_TIMEOUT = 45  # 45 minutes of no activity
    USER_INACTIVITY_TIMEOUT = 90   # 90 minutes of no activity
    
    # Session check interval (how often to check for expired sessions)
    SESSION_CHECK_INTERVAL = 30  # Check every 30 seconds

class SessionInfo:
    """Stores session information for a user"""
    
    def __init__(self, user_email: str, user_name: str, user_type: str):
        self.user_email = user_email
        self.user_name = user_name
        self.user_type = user_type  # 'admin', 'student', 'faculty'
        
        # Session timestamps
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.expires_at = self._calculate_expiry()
        
        # Session state
        self.is_active = True
    
    def _calculate_expiry(self) -> datetime:
        """Calculate session expiry based on user type"""
        if self.user_type == "admin":
            timeout = SessionConfig.ADMIN_SESSION_TIMEOUT
        else:
            timeout = SessionConfig.USER_SESSION_TIMEOUT
        
        return datetime.now() + timedelta(minutes=timeout)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        return datetime.now() > self.expires_at
    
    def is_inactive(self) -> bool:
        """Check if session has exceeded inactivity timeout"""
        if self.user_type == "admin":
            inactivity_timeout = SessionConfig.ADMIN_INACTIVITY_TIMEOUT
        else:
            inactivity_timeout = SessionConfig.USER_INACTIVITY_TIMEOUT
        
        time_since_activity = (datetime.now() - self.last_activity).total_seconds() / 60
        return time_since_activity > inactivity_timeout
    
    def get_time_remaining(self) -> int:
        """Get remaining session time in minutes"""
        remaining = (self.expires_at - datetime.now()).total_seconds() / 60
        return max(0, int(remaining))
    
    def get_inactivity_time(self) -> int:
        """Get inactivity duration in minutes"""
        inactive_time = (datetime.now() - self.last_activity).total_seconds() / 60
        return int(inactive_time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'user_email': self.user_email,
            'user_name': self.user_name,
            'user_type': self.user_type,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'is_active': self.is_active,
            'time_remaining': self.get_time_remaining(),
            'inactivity_minutes': self.get_inactivity_time()
        }


class SessionManager:
    """
    Manages user sessions with timeout and inactivity handling.
    Provides session creation, validation, activity tracking, and cleanup.
    """
    
    def __init__(self):
        self._sessions: Dict[str, SessionInfo] = {}
        self._timeout_callbacks: list[Callable] = []
        
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = False
        self._lock = threading.Lock()
    
    def create_session(
        self,
        user_email: str,
        user_name: str,
        user_type: str
    ) -> SessionInfo:
        """
        Create a new session for a user.
        
        Args:
            user_email: User's email address
            user_name: User's name
            user_type: 'admin', 'student', or 'faculty'
        
        Returns:
            SessionInfo object for the created session
        """
        with self._lock:
            # Invalidate any existing session for this user
            if user_email in self._sessions:
                self._sessions[user_email].is_active = False
            
            session = SessionInfo(user_email, user_name, user_type)
            self._sessions[user_email] = session
            
            return session
    
    def get_session(self, user_email: str) -> Optional[SessionInfo]:
        """Get session for a user"""
        with self._lock:
            return self._sessions.get(user_email)
    
    def validate_session(self, user_email: str) -> bool:
        """
        Validate if a session is still active and not expired/inactive.
        
        Returns:
            True if session is valid, False otherwise
        """
        session = self.get_session(user_email)
        
        if not session:
            return False
        
        if not session.is_active:
            return False
        
        if session.is_expired():
            return False
        
        if session.is_inactive():
            return False
        
        return True
    
    def update_activity(self, user_email: str) -> bool:
        """
        Update last activity for a user.
        Called on user interactions (clicks, input, etc).
        
        Returns:
            True if activity updated, False if session invalid
        """
        session = self.get_session(user_email)
        
        if not session:
            return False
        
        session.update_activity()
        return True
    
    def invalidate_session(self, user_email: str) -> bool:
        """
        Manually invalidate a session (for logout).
        
        Returns:
            True if session was invalidated, False if no session
        """
        session = self.get_session(user_email)
        
        if not session:
            return False
        
        with self._lock:
            session.is_active = False
        
        return True
    
    def register_timeout_callback(self, callback: Callable[[str, str], None]):
        """
        Register callback for when session times out.
        Callback receives (user_email, reason) where reason is 'timeout' or 'inactivity'
        """
        self._timeout_callbacks.append(callback)
    
    def start_monitoring(self):
        """Start background monitoring of session timeouts"""
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            return
        
        self._stop_monitoring = False
        self._monitor_thread = threading.Thread(
            target=self._monitor_sessions,
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self._stop_monitoring = True
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
    
    def _monitor_sessions(self):
        """Background thread that monitors sessions"""
        while not self._stop_monitoring:
            try:
                self._check_sessions()
                time.sleep(SessionConfig.SESSION_CHECK_INTERVAL)
            except Exception as e:
                print(f"Error monitoring sessions: {e}")
    
    def _check_sessions(self):
        """Check all sessions for timeout/inactivity"""
        with self._lock:
            sessions_to_check = list(self._sessions.items())
        
        for user_email, session in sessions_to_check:
            if not session.is_active:
                continue
            
            # Check for timeout
            if session.is_expired():
                self._handle_timeout(user_email, session, 'timeout')
            
            # Check for inactivity
            elif session.is_inactive():
                self._handle_timeout(user_email, session, 'inactivity')
    
    def _handle_timeout(self, user_email: str, session: SessionInfo, reason: str):
        """Handle session timeout"""
        with self._lock:
            session.is_active = False
        
        # Trigger timeout callbacks
        for callback in self._timeout_callbacks:
            try:
                callback(user_email, reason)
            except Exception as e:
                print(f"Error in timeout callback: {e}")
    
    def get_all_active_sessions(self) -> Dict[str, Dict]:
        """Get all currently active sessions"""
        with self._lock:
            active = {
                email: session.to_dict()
                for email, session in self._sessions.items()
                if session.is_active
            }
        return active
    
    def get_session_stats(self, user_email: str) -> Optional[Dict]:
        """Get session statistics for a user"""
        session = self.get_session(user_email)
        if not session:
            return None
        
        return {
            'user_email': session.user_email,
            'user_name': session.user_name,
            'user_type': session.user_type,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'time_remaining_minutes': session.get_time_remaining(),
            'inactivity_minutes': session.get_inactivity_time(),
            'is_expired': session.is_expired(),
            'is_inactive': session.is_inactive(),
            'is_active': session.is_active,
            'session_duration_minutes': int((datetime.now() - session.created_at).total_seconds() / 60),
            'expiry_reason': self._get_expiry_reason(session)
        }
    
    def _get_expiry_reason(self, session: SessionInfo) -> Optional[str]:
        """Get reason for session expiry"""
        if session.is_expired():
            return 'Maximum session time exceeded'
        if session.is_inactive():
            if session.user_type == "admin":
                return f'Inactive for {SessionConfig.ADMIN_INACTIVITY_TIMEOUT} minutes'
            else:
                return f'Inactive for {SessionConfig.USER_INACTIVITY_TIMEOUT} minutes'
        return None
    
    def extend_session(self, user_email: str) -> bool:
        """
        Manually extend session timeout by another full duration.
        Can be used for "keep me logged in" functionality.
        
        Returns:
            True if extended, False if session invalid
        """
        session = self.get_session(user_email)
        if not session or not session.is_active:
            return False
        
        session.expires_at = session._calculate_expiry()
        session.last_activity = datetime.now()
        session.warned = False
        
        return True
    
    def cleanup_inactive_sessions(self):
        """Remove sessions that have been inactive or expired"""
        with self._lock:
            to_remove = [
                email for email, session in self._sessions.items()
                if session.is_expired() or session.is_inactive()
            ]
            
            for email in to_remove:
                del self._sessions[email]
            
            return len(to_remove)


# Global singleton instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create the singleton session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
