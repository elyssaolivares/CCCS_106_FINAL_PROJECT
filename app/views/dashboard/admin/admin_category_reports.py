import flet as ft
from app.services.database.database import db
from app.views.dashboard.session_manager import SessionManager
from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
from .dashboard_data_manager import DataManager, StatusNormalizer
from .admin_dashboard_ui import UIComponents


def admin_category_reports(page: ft.Page, user_data=None, category=None, status=None):
    """Detailed reports page for a specific category, optionally filtered by status"""
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
        admin_category_reports(page, user_data, category, status)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    
    ui_components = UIComponents()
    
    def _go_back():
        from .admin_dashboard import admin_dashboard
        admin_dashboard(page, user_data)
    
    title = f"{category or 'Reports'} - {status or 'All'}" if category else "Reports"
    header = ui_components.create_page_header(is_dark, title, _go_back, nav_drawer.open_drawer)
    
    
    all_reports = db.get_all_reports()
    
    if category:
        filtered_reports = [r for r in all_reports if r.get('category', 'Uncategorized') == category]
    else:
        filtered_reports = all_reports
    
    if status:
        sf = (status or '').strip().lower()
        filtered_reports = [r for r in filtered_reports if (r.get('status') or '').strip().lower() == sf]
    
    reports_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    status_filter_buttons = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
    
    def update_status_filters():
        status_filter_buttons.controls.clear()
        
        category_reports = [r for r in all_reports if r.get('category', 'Uncategorized') == category] if category else all_reports
        status_counts = {
            'Pending': 0,
            'In Progress': 0,
            'Resolved': 0,
            'Rejected': 0
        }

        for report in category_reports:
            canon = StatusNormalizer.canonicalize(report.get('status', 'Pending'))
            status_counts[canon] = status_counts.get(canon, 0) + 1
        
        all_btn = ft.TextButton(
            content=ft.Row([
                ft.Text("All", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE if status is None else ft.Colors.GREY_500),
                ft.Text(f"({len(category_reports)})", size=11, color=ft.Colors.WHITE if status is None else ft.Colors.GREY_500),
            ], spacing=4),
            on_click=lambda e: admin_category_reports(page, user_data, category, None),
            style=ft.ButtonStyle(
                bgcolor="#062C80" if status is None else ft.Colors.TRANSPARENT,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        status_filter_buttons.controls.append(all_btn)
        
        for s in ["Pending", "In Progress", "Resolved", "Rejected"]:
            count = status_counts.get(s, 0)
            btn = ft.TextButton(
                content=ft.Row([
                    ft.Text(s, size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE if status == s else ft.Colors.GREY_500),
                    ft.Text(f"({count})", size=11, color=ft.Colors.WHITE if status == s else ft.Colors.GREY_500),
                ], spacing=4),
                on_click=lambda e, st=s: admin_category_reports(page, user_data, category, st),
                style=ft.ButtonStyle(
                    bgcolor="#062C80" if status == s else ft.Colors.TRANSPARENT,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    shape=ft.RoundedRectangleBorder(radius=8),
                )
            )
            status_filter_buttons.controls.append(btn)
    
    def handle_status_change(report_id, new_status):
        db.update_report_status(report_id, new_status)
        admin_category_reports(page, user_data, category, status)
    
    if not filtered_reports:
        reports_list.controls.append(ui_components.create_empty_category_message(category))
    else:
        for report in filtered_reports:
            report_card = ui_components.create_report_card(report, handle_status_change)
            reports_list.controls.append(report_card)
    
    # Build status filters
    if category:
        update_status_filters()
    
    main_content = ft.Column(
        [
            ft.Text(
                f"Reports in {category}" if category else "All Reports",
                size=14,
                font_family="Poppins-Bold",
                color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
            ),
            # Show status filter buttons only for category view
            *([
                ft.Container(height=8),
                status_filter_buttons,
                ft.Container(height=12),
            ] if category else [ft.Container(height=12)]),
            reports_list,
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
    page.update()
