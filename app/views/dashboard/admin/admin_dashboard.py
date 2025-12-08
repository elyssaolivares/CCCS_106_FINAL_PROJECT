import flet as ft
from app.services.database.database import db
from app.views.dashboard.session_manager import SessionManager
from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
from .dashboard_data_manager import DataManager
from .admin_dashboard_ui import UIComponents
from .dashboard_controller import DashboardController, DashboardState
from app.views.components.session_timeout_ui import create_session_timeout_handler


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
    
    # Setup session timeout handler
    def on_logout_callback():
        from app.views.loginpage import loginpage
        page.controls.clear()
        loginpage(page)
    
    session_timeout_handler = create_session_timeout_handler(
        page,
        user_data.get("email"),
        on_logout_callback
    )
    
    header = ui_components.create_header(is_dark, nav_drawer.open_drawer)
    
    def navigate_to_all_categories(e):
        from .admin_all_reports import admin_all_reports
        admin_all_reports(page, user_data)
    
    main_content = ft.Column(
        [
            ft.Text("Reports Summary", size=16, font_family="Poppins-Bold",
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
            ft.Container(height=12),
            ft.Container(
                content=state.stats_row,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                padding=ft.padding.all(12),
                border_radius=10,
            ),
            
            ft.Container(height=8),
            ft.Container(
                content=state.category_filter_buttons,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                padding=ft.padding.all(8),
                border_radius=8,
            ),
            ft.Container(height=12),
            
            ft.Container(
                content=state.category_list_view,
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                padding=ft.padding.all(15),
                border_radius=10,
            ),
            ft.Row(
                [
                    ft.TextButton(
                        "Show All Reports",
                        on_click=navigate_to_all_categories,
                        style=ft.ButtonStyle(
                            color="#062C80",
                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                wrap=True,
                spacing=0,
                expand=True,
            ),
        ],
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
    
    controller.refresh_dashboard()
    page.update()

