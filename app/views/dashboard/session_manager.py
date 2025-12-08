import flet as ft

class SessionManager:
    @staticmethod
    def get_user_data(page: ft.Page):
        """Retrieve user data from session"""
        return page.session.get("user_data")
    
    @staticmethod
    def set_user_data(page: ft.Page, user_data):
        """Store user data in session"""
        page.session.set("user_data", user_data)
    
    @staticmethod
    def clear_session(page: ft.Page):
        """Clear all session data"""
        page.session.clear()
    
    @staticmethod
    def get_theme_preference(page: ft.Page):
        """Get dark theme preference"""
        return page.session.get("is_dark_theme") or False
    
    @staticmethod
    def set_theme_preference(page: ft.Page, is_dark: bool):
        """Set dark theme preference"""
        page.session.set("is_dark_theme", is_dark)
    
    @staticmethod
    def validate_session(page: ft.Page):
        """Validate if user session exists, redirect to login if not"""
        user_data = SessionManager.get_user_data(page)
        if not user_data:
            from app.views.loginpage import loginpage
            loginpage(page)
            return None
        return user_data