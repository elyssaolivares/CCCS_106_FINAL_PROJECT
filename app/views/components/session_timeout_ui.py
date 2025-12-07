"""
Session Timeout UI Components
Provides Flet UI components for session timeout warnings and management.
"""

import flet as ft
from datetime import datetime
from app.services.session import get_session_manager, SessionConfig


class SessionTimeoutDialog(ft.AlertDialog):
    """Dialog warning user about session timeout"""
    
    def __init__(self, page: ft.Page, on_extend=None, on_logout=None):
        super().__init__()
        self.page = page
        self.on_extend = on_extend
        self.on_logout = on_logout
        self.session_manager = get_session_manager()
        
        # Timer countdown
        self.timer_text = ft.Text(
            "Session expiring soon",
            size=24,
            weight="bold",
            color=ft.Colors.WHITE
        )
        
        # Message
        message = ft.Text(
            "Your session will expire soon due to inactivity.\n\n"
            "Click 'Continue Session' to stay logged in.",
            size=14,
            color=ft.Colors.WHITE
        )
        
        # Buttons
        extend_button = ft.ElevatedButton(
            "Continue Session",
            on_click=self._on_extend_click,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            width=200
        )
        
        logout_button = ft.ElevatedButton(
            "Logout",
            on_click=self._on_logout_click,
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
            width=200
        )
        
        # Build dialog with prominent styling
        self.title = ft.Text("⚠️ SESSION TIMEOUT WARNING", weight="bold", size=18, color=ft.Colors.WHITE)
        self.content = ft.Container(
            content=ft.Column(
                [
                    message,
                    ft.Container(height=20),
                    self.timer_text,
                ],
                spacing=15,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=500,
            padding=30,
            bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.RED_800),
            border_radius=15
        )
        self.actions = [extend_button, logout_button]
        self.actions_alignment = ft.MainAxisAlignment.CENTER
        self.modal = True  # Make it modal so it can't be dismissed by clicking outside
    
    def _on_extend_click(self, e):
        """Handle extend session"""
        if self.on_extend:
            try:
                self.on_extend()
            except Exception as ex:
                print(f"Error extending session: {ex}")
        self.open = False
        self.page.update()

    
    def _on_logout_click(self, e):
        """Handle logout"""
        if self.on_logout:
            try:
                self.on_logout()
            except Exception as ex:
                print(f"Error logging out: {ex}")
        self.open = False
        self.page.update()
    
    def update_timer(self, seconds_remaining: int):
        """Update timer display"""
        if seconds_remaining <= 0:
            self.timer_text.value = "Session expired!"
            self.timer_text.color = ft.Colors.RED
        else:
            self.timer_text.value = f"{seconds_remaining} second{'s' if seconds_remaining != 1 else ''} remaining"
            self.timer_text.color = ft.Colors.ORANGE if seconds_remaining <= 5 else ft.Colors.RED
        
        self.page.update()


class SessionStatusIndicator(ft.Container):
    """
    UI component displaying current session status and time remaining.
    Shows in dashboards/pages to provide user feedback.
    """
    
    def __init__(self, page: ft.Page, user_email: str):
        super().__init__()
        self.page = page
        self.user_email = user_email
        self.session_manager = get_session_manager()
        
        # Status icon
        self.status_icon = ft.Icon(
            name=ft.Icons.SCHEDULE,
            color=ft.Colors.GREEN,
            size=20
        )
        
        # Timer text
        self.timer_text = ft.Text(
            "59 min remaining",
            size=11,
            color=ft.Colors.GREY_700
        )
        
        # Inactivity warning
        self.warning_text = ft.Text(
            "",
            size=10,
            color=ft.Colors.ORANGE,
            visible=False
        )
        
        # Build layout
        self.padding = ft.padding.symmetric(horizontal=10, vertical=5)
        self.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.ORANGE)
        self.border_radius = 8
        
        self.content = ft.Column(
            [
                ft.Row(
                    [self.status_icon, self.timer_text],
                    spacing=8,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                self.warning_text,
            ],
            spacing=4
        )
        
        # Start update thread
        self._start_updates()
    
    def _start_updates(self):
        """Start periodic updates"""
        import threading
        
        def update_loop():
            while True:
                try:
                    self._update_display()
                    import time
                    time.sleep(10)  # Update every 10 seconds
                except Exception as e:
                    print(f"Error updating session indicator: {e}")
                    break
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()
    
    def _update_display(self):
        """Update status display"""
        session = self.session_manager.get_session(self.user_email)
        
        if not session or not session.is_active:
            self.visible = False
            self.page.update()
            return
        
        # Update timer
        time_remaining = session.get_time_remaining()
        self.timer_text.value = f"{time_remaining} seconds remaining"
        
        # Update color based on time remaining
        if time_remaining <= 5:
            self.status_icon.color = ft.Colors.RED
            self.timer_text.color = ft.Colors.RED
        elif time_remaining <= 15:
            self.status_icon.color = ft.Colors.ORANGE
            self.timer_text.color = ft.Colors.ORANGE
        else:
            self.status_icon.color = ft.Colors.GREEN
            self.timer_text.color = ft.Colors.GREY_700
        
        # Show inactivity warning if applicable
        inactivity_secs = session.get_inactivity_time()
        if session.user_type == "admin":
            inactivity_threshold = SessionConfig.ADMIN_INACTIVITY_TIMEOUT * 0.8  # Warn at 80%
        else:
            inactivity_threshold = SessionConfig.USER_INACTIVITY_TIMEOUT * 0.8
        
        if inactivity_secs > inactivity_threshold:
            self.warning_text.value = f"No activity for {inactivity_secs} seconds"
            self.warning_text.visible = True
        else:
            self.warning_text.visible = False
        
        self.page.update()


class SessionActivityTracker:
    """
    Tracks user activity to keep sessions alive.
    Integrates with Flet page to monitor interactions.
    """
    
    def __init__(self, page: ft.Page, user_email: str):
        self.page = page
        self.user_email = user_email
        self.session_manager = get_session_manager()
    
    def track_activity(self, e=None):
        """Record user activity"""
        if self.session_manager.update_activity(self.user_email):
            # Session activity updated
            pass
        else:
            # Session invalid - user should be logged out
            pass
    
    def setup_tracking(self):
        """Set up activity tracking on page controls"""
        # Intercept mouse events
        self.page.on_focus = self._on_page_focus
        
        # Note: In Flet, we can't easily intercept all events,
        # so we use on_focus and can add manual tracking calls
    
    def _on_page_focus(self, e):
        """Called when page gains focus"""
        self.track_activity()


def create_session_timeout_handler(page: ft.Page, user_email: str, on_logout_callback=None):
    """
    Create a session timeout handler for a page.
    Automatically logs out user when session expires.
    
    Args:
        page: Flet Page object
        user_email: User's email
        on_logout_callback: Function to call on logout
    
    Returns:
        Dictionary with tracker
    """
    session_manager = get_session_manager()
    
    # Register timeout callback for automatic logout
    def timeout_callback(email, reason):
        if email == user_email:
            if on_logout_callback:
                on_logout_callback()
    
    session_manager.register_timeout_callback(timeout_callback)
    
    # Create activity tracker
    tracker = SessionActivityTracker(page, user_email)
    
    return {
        'tracker': tracker,
    }
