import flet as ft
from app.services.database.database import db
from app.views.dashboard.session_manager import SessionManager
from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
from .dashboard_data_manager import DataManager
from .admin_dashboard_ui import UIComponents


def admin_all_categories(page: ft.Page, user_data=None):
    page.controls.clear()
    page.floating_action_button = None
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    if not user_data:
        from app.views.loginpage import loginpage
        loginpage(page)
        return
    
    is_dark = SessionManager.get_theme_preference(page)
    current_status_filter = {"status": "All"}
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        admin_all_categories(page, user_data)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    
    data_manager = DataManager()
    ui_components = UIComponents()
    
    header = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                    on_click=lambda e: _go_back(),
                ),
                ft.Text(
                    "All Categorized Reports",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                    on_click=nav_drawer.open_drawer,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )
    
    def _go_back():
        from .admin_dashboard import admin_dashboard
        admin_dashboard(page, user_data)
    
    all_reports = db.get_all_reports()
    
    stats_row = ft.Row(spacing=12, wrap=False, scroll=ft.ScrollMode.AUTO)
    
    
    status_filter_buttons = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO, tight=True)
    
    
    category_list_view = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def update_stats():
        
        stats_row.controls.clear()
        filtered = all_reports
        if current_status_filter["status"] != "All":
            target = (current_status_filter["status"] or '').strip().lower()
            filtered = [r for r in all_reports if (r.get('status') or '').strip().lower() == target]
        
        from .dashboard_data_manager import DataManager as DM
        counts = DM.calculate_status_counts(filtered)
        
        stats_row.controls.extend([
            ui_components.create_stat_card("Pending", counts.get("pending", 0), "#FFE5D9", "#FF6B35"),
            ui_components.create_stat_card("In Progress", counts.get("in progress", 0), "#FFF9E6", "#FFC107"),
            ui_components.create_stat_card("Resolved", counts.get("resolved", 0), "#E8F5E9", "#4CAF50"),
            ui_components.create_stat_card("Rejected", counts.get("rejected", 0), "#FFEBEE", "#F44336"),
        ])
    
    def update_status_filters():
        
        status_filter_buttons.controls.clear()
        
        counts = DataManager.calculate_status_counts(all_reports)
        
        status_mapping = {
            "All": len(all_reports),
            "Pending": counts.get("pending", 0),
            "In Progress": counts.get("in progress", 0),
            "Resolved": counts.get("resolved", 0),
            "Rejected": counts.get("rejected", 0)
        }
        
        for label, count in status_mapping.items():
            btn = ft.TextButton(
                content=ui_components.create_tab_button(
                    label, count, current_status_filter["status"] == label
                ),
                on_click=lambda e, s=label: apply_status_filter(s)
            )
            status_filter_buttons.controls.append(btn)
    
    def apply_status_filter(status):
        
        current_status_filter["status"] = status
        update_stats()
        update_category_list()
        page.update()
    
    def update_category_list():
        
        category_list_view.controls.clear()
        
        
        filtered_reports = all_reports
        if current_status_filter["status"] != "All":
            target = (current_status_filter["status"] or '').strip().lower()
            filtered_reports = [r for r in all_reports if (r.get('status') or '').strip().lower() == target]
        
        
        category_counts = DataManager.calculate_category_counts(filtered_reports)
        
        if not category_counts:
            category_list_view.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INBOX_OUTLINED, size=64, color=ft.Colors.GREY_600),
                            ft.Container(height=10),
                            ft.Text("No categories found", size=16, weight=ft.FontWeight.BOLD,
                                   color=ft.Colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            )
        else:
            
            
            sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            
            for category_name, count in sorted_categories:
                item = ui_components.create_category_list_item(
                    category_name,
                    count,
                    lambda e, cat=category_name: navigate_to_category(cat)
                )
                category_list_view.controls.append(item)
    
    def navigate_to_category(category_name):
        
        from .admin_category_reports import admin_category_reports
        admin_category_reports(page, user_data, category=category_name)
    
    
    update_stats()
    update_status_filters()
    update_category_list()
    
    main_content = ft.Column(
        [
            
            ft.Text("Reports Summary", size=16, font_family="Poppins-Bold",
                   color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
            ft.Container(height=12),
            ft.Container(
                content=stats_row,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                padding=ft.padding.all(12),
                border_radius=10,
            ),
            
            
            
            ft.Container(height=20),
            ft.Text("Filter by Status", size=14, font_family="Poppins-SemiBold",
                   color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
            ft.Container(height=10),
            ft.Container(
                content=status_filter_buttons,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                padding=ft.padding.all(8),
                border_radius=8,
            ),
            
            
            
            ft.Container(height=20),
            ft.Text("Categories", size=14, font_family="Poppins-SemiBold",
                   color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
            ft.Container(height=10),
            ft.Container(
                content=category_list_view,
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                padding=ft.padding.all(12),
                border_radius=10,
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
    page.update()
