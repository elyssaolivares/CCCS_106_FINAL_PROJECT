# ============================================
# FILE 1: admin_dashboard.py
# ============================================

import flet as ft
from app.services.database.database import db
from app.views.dashboard.session_manager import SessionManager
from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
from .dashboard_data_manager import DataManager
from .admin_dashboard_ui import UIComponents
from .dashboard_controller import DashboardController, DashboardState


def admin_dashboard(page: ft.Page, user_data=None):
    page.controls.clear()
    page.floating_action_button = None
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    if not user_data:
        from app.views.loginpage import loginpage
        loginpage(page)
        return
    
    is_dark = SessionManager.get_theme_preference(page)
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        admin_dashboard(page, user_data)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    
    state = DashboardState()
    data_manager = DataManager()
    ui_components = UIComponents()
    controller = DashboardController(page, user_data, state, data_manager, ui_components)
    
    header = ui_components.create_header(is_dark, nav_drawer.open_drawer)
    
    main_content = ft.Column(
        [
            ft.Text("Reports Overview", size=18, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
            ft.Container(height=16),
            state.stats_row,
            ft.Container(height=20),
            state.tab_buttons,
            ft.Container(height=16),
            ft.Container(
                content=state.reports_list,
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                border_radius=10,
                padding=ft.padding.all(4),
            ),
        ],
        spacing=0,
        expand=True,
    )
    
    main_container = ft.Container(
        content=main_content,
        padding=ft.padding.all(20),
        expand=True,
    )
    
    page_layout = ft.Column(
        [
            header,
            main_container,
        ],
        spacing=0,
        expand=True,
    )
    
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_900 if is_dark else ft.Colors.GREY_100
    page.end_drawer = drawer
    page.scroll = ft.ScrollMode.AUTO
    
    page.add(page_layout)
    
    controller.refresh_dashboard(state.current_status)
    page.update()

