import flet as ft
from app.services.database.database import db
from app.views.dashboard.session_manager import SessionManager
from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
from .dashboard_data_manager import DataManager, StatusNormalizer
from .admin_dashboard_ui import UIComponents

# ── Palette ──
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_WHITE = "#FFFFFF"


def admin_all_categories(page: ft.Page, user_data=None):
    page.controls.clear()
    page.overlay.clear()
    page.floating_action_button = None
    page.end_drawer = None
    page.drawer = None
    page.scroll = None

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
    all_reports = db.get_all_reports() or []

    stats_row = ft.ResponsiveRow(spacing=10, run_spacing=10)
    status_filter_buttons = ft.Row(spacing=6, scroll=ft.ScrollMode.AUTO, tight=True)
    category_list_view = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def update_stats():
        stats_row.controls.clear()
        filtered = all_reports
        if current_status_filter["status"] != "All":
            target = (current_status_filter["status"] or "").strip().lower()
            filtered = [r for r in all_reports if (r.get("status") or "").strip().lower() == target]

        counts = DataManager.calculate_status_counts(filtered)
        stats_row.controls.extend([
            ui_components.create_stat_card("Pending", counts.get("pending", 0),
                                            ft.Icons.SCHEDULE_OUTLINED, "#B45309", "#FEF3C7"),
            ui_components.create_stat_card("In Progress", counts.get("in progress", 0),
                                            ft.Icons.AUTORENEW_ROUNDED, "#1565C0", "#DBEAFE"),
            ui_components.create_stat_card("Resolved", counts.get("resolved", 0),
                                            ft.Icons.CHECK_CIRCLE_OUTLINE, "#15803D", "#DCFCE7"),
            ui_components.create_stat_card("Rejected", counts.get("rejected", 0),
                                            ft.Icons.CANCEL_OUTLINED, "#DC2626", "#FEE2E2"),
        ])

    def update_status_filters():
        status_filter_buttons.controls.clear()
        counts = DataManager.calculate_status_counts(all_reports)

        status_mapping = {
            "All": len(all_reports),
            "Pending": counts.get("pending", 0),
            "In Progress": counts.get("in progress", 0),
            "Resolved": counts.get("resolved", 0),
            "Rejected": counts.get("rejected", 0),
        }

        for label, count in status_mapping.items():
            btn = ft.Container(
                content=ui_components.create_tab_button(
                    label, count, current_status_filter["status"] == label
                ),
                on_click=lambda e, s=label: apply_status_filter(s),
            )
            status_filter_buttons.controls.append(btn)

    def apply_status_filter(status):
        current_status_filter["status"] = status
        update_stats()
        update_status_filters()
        update_category_list()
        page.update()

    def update_category_list():
        category_list_view.controls.clear()
        filtered_reports = all_reports
        if current_status_filter["status"] != "All":
            target = (current_status_filter["status"] or "").strip().lower()
            filtered_reports = [r for r in all_reports if (r.get("status") or "").strip().lower() == target]

        category_counts = DataManager.calculate_category_counts(filtered_reports)
        if not category_counts:
            category_list_view.controls.append(ui_components.create_empty_category_message())
        else:
            sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            for category_name, count in sorted_categories:
                item = ui_components.create_category_list_item(
                    category_name, count,
                    lambda e, cat=category_name: navigate_to_category(cat),
                )
                category_list_view.controls.append(item)

    def navigate_to_category(category_name):
        from .admin_category_reports import admin_category_reports
        admin_category_reports(page, user_data, category=category_name)

    update_stats()
    update_status_filters()
    update_category_list()

    # ── Top bar ──
    def go_back(e=None):
        from .admin_dashboard import admin_dashboard
        admin_dashboard(page, user_data)

    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

    top_bar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, icon_color=_NAVY, icon_size=20, on_click=go_back),
                ft.Column(
                    [
                        ft.Text("All Categories", size=16, font_family="Poppins-Bold", color=_NAVY),
                        ft.Text("Categorized reports overview", size=11, font_family="Poppins-Light", color=_NAVY_MUTED),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Container(
                    content=ft.IconButton(ft.Icons.MENU_ROUNDED, icon_color=_NAVY, icon_size=20,
                                          on_click=on_menu_click),
                    width=36, height=36, border_radius=10,
                    bgcolor=_BORDER_LIGHT, alignment=ft.alignment.center,
                ),
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=14, vertical=12),
        bgcolor=_WHITE,
        border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
    )

    # ── Main content ──
    main_content = ft.Column(
        [
            stats_row,
            ft.Container(height=12),
            status_filter_buttons,
            ft.Container(height=16),
            ft.Text("Categories", size=14, font_family="Poppins-SemiBold", color=_NAVY),
            ft.Container(height=8),
            category_list_view,
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    content_area = ft.Container(
        content=ft.Column(
            [
                top_bar,
                ft.Container(
                    content=main_content,
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
        bgcolor=_BG,
    )

    # ── Assemble ──
    page.end_drawer = drawer
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = _BG

    page.add(content_area)
    page.update()
