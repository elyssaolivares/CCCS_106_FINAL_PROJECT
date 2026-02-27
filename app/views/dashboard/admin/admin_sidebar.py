"""Shared admin sidebar builder for consistent navigation across admin pages."""

import flet as ft
from app.views.dashboard.dashboard_ui import DashboardUI

_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_WHITE = "#FFFFFF"


def create_admin_sidebar(page, user_data, active_key="home"):
    """Create the admin sidebar with navigation items.

    Args:
        page: Flet Page instance
        user_data: User data dict
        active_key: Which nav item is active
                    ("home", "reports", "audit", "activity", "account")

    Returns:
        tuple: (sidebar_container, on_logout_function)
    """
    full_name = user_data.get("name", "Admin") if user_data else "Admin"
    picture = user_data.get("picture") if user_data else None
    first_letter = full_name[0].upper() if full_name else "A"

    def nav_handler(key):
        def handler(e):
            if key == "home":
                from .admin_dashboard import admin_dashboard
                admin_dashboard(page, user_data)
            elif key == "reports":
                from .admin_all_reports import admin_all_reports
                admin_all_reports(page, user_data)
            elif key == "audit":
                from .audit_logs_viewer import audit_logs_page
                audit_logs_page(page, user_data)
            elif key == "activity":
                from .user_activity_monitoring import user_activity_monitoring_page
                user_activity_monitoring_page(page, user_data)
            elif key == "account":
                from app.views.dashboard.account_page import account_page
                account_page(page, user_data)
        return handler

    def on_logout(e):
        page.session.clear()
        page.controls.clear()
        page.overlay.clear()
        page.floating_action_button = None
        page.end_drawer = None
        page.drawer = None
        page.on_resized = None
        from app.views.loginpage import loginpage
        loginpage(page)

    def _nav_item(icon, label, key, on_click):
        is_active = key == active_key
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=18,
                            color=_ACCENT if is_active else _NAVY_MUTED),
                    ft.Text(label, size=13, font_family="Poppins-Medium",
                            color=_NAVY if is_active else _NAVY_MUTED),
                ],
                spacing=12,
            ),
            padding=ft.padding.symmetric(horizontal=14, vertical=11),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.08, _ACCENT) if is_active else ft.Colors.TRANSPARENT,
            on_click=on_click,
            ink=True,
        )

    nav_items = [
        _nav_item(ft.Icons.GRID_VIEW_ROUNDED, "Dashboard", "home", nav_handler("home")),
        _nav_item(ft.Icons.CAMPAIGN_OUTLINED, "Reports", "reports", nav_handler("reports")),
        _nav_item(ft.Icons.SECURITY_OUTLINED, "Audit Logs", "audit", nav_handler("audit")),
        _nav_item(ft.Icons.VISIBILITY_OUTLINED, "User Activity", "activity", nav_handler("activity")),
        _nav_item(ft.Icons.PERSON_OUTLINE_ROUNDED, "Account", "account", nav_handler("account")),
    ]

    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, size=20, color=_WHITE),
                                width=34, height=34, border_radius=10,
                                bgcolor=_ACCENT, alignment=ft.alignment.center,
                            ),
                            ft.Text("FIXIT Admin", size=16, font_family="Poppins-Bold", color=_NAVY),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(left=16, right=16, top=28, bottom=20),
                ),
                ft.Container(height=1, bgcolor=_BORDER, margin=ft.margin.symmetric(horizontal=12)),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column(nav_items, spacing=4),
                    padding=ft.padding.symmetric(horizontal=8),
                ),
                ft.Container(expand=True),
                ft.Container(height=1, bgcolor=_BORDER, margin=ft.margin.symmetric(horizontal=12)),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=18, color=_NAVY_MUTED),
                            ft.Text("Logout", size=13, font_family="Poppins-Medium", color=_NAVY_MUTED),
                        ],
                        spacing=12,
                    ),
                    padding=ft.padding.symmetric(horizontal=14, vertical=11),
                    border_radius=10,
                    on_click=on_logout,
                    ink=True,
                    margin=ft.margin.symmetric(horizontal=8),
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Row(
                        [
                            DashboardUI._build_avatar(picture, first_letter, 34, 10, _NAVY, _WHITE),
                            ft.Column(
                                [
                                    ft.Text(full_name, size=12, font_family="Poppins-SemiBold", color=_NAVY),
                                    ft.Text("Admin", size=10, font_family="Poppins-Light", color=_NAVY_MUTED),
                                ],
                                spacing=0,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.all(12),
                    margin=ft.margin.only(left=8, right=8, bottom=16),
                    border_radius=10,
                    bgcolor=_BORDER_LIGHT,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        width=230,
        bgcolor=_WHITE,
        border=ft.border.only(right=ft.BorderSide(1, _BORDER)),
    )

    return sidebar, on_logout
