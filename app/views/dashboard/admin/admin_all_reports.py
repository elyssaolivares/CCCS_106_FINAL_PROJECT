import flet as ft
from app.services.database.database import db
from app.views.dashboard.session_manager import SessionManager
from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
from .dashboard_data_manager import DataManager, StatusNormalizer
from .admin_dashboard_ui import UIComponents
from .admin_sidebar import create_admin_sidebar

# ── Palette ──
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_WHITE = "#FFFFFF"

_SIDEBAR_BREAKPOINT = 768


def admin_all_reports(page: ft.Page, user_data=None):
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

    full_name = user_data.get("name", "Admin")
    first_name = full_name.split()[0] if full_name else "Admin"
    is_dark = SessionManager.get_theme_preference(page)
    current_filters = {"status": "All"}

    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        admin_all_reports(page, user_data)

    # ── Mobile drawer ──
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)

    data_manager = DataManager()
    ui_components = UIComponents()
    all_reports = db.get_all_reports() or []

    status_filter_buttons = ft.Row(spacing=6, scroll=ft.ScrollMode.AUTO, tight=True)
    category_list_view = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

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
                    label, count, current_filters["status"] == label
                ),
                on_click=lambda e, s=label: apply_status_filter(s),
            )
            status_filter_buttons.controls.append(btn)

    def apply_status_filter(status):
        current_filters["status"] = status
        update_status_filters()
        update_category_list()
        page.update()

    def update_category_list():
        category_list_view.controls.clear()
        filtered_reports = all_reports
        if current_filters["status"] != "All":
            target = current_filters["status"].lower()
            filtered_reports = [r for r in all_reports if (r.get("status") or "").lower() == target]

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
        admin_category_reports(
            page, user_data, category=category_name,
            status=current_filters["status"] if current_filters["status"] != "All" else None,
        )

    update_status_filters()
    update_category_list()

    # ── Mobile top bar ──
    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)

    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

    def go_back(e=None):
        from .admin_dashboard import admin_dashboard
        admin_dashboard(page, user_data)

    # ── Admin sidebar ──
    sidebar, _ = create_admin_sidebar(page, user_data, active_key="reports")
    sidebar_wrapper = ft.Container(content=sidebar, visible=not is_mobile)

    mobile_top_bar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, icon_color=_NAVY, icon_size=20, on_click=go_back),
                ft.Column(
                    [
                        ft.Text("All Reports", size=16, font_family="Poppins-Bold", color=_NAVY),
                        ft.Text("Browse by category", size=11, font_family="Poppins-Light", color=_NAVY_MUTED),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Container(
                    content=ft.IconButton(ft.Icons.MENU_ROUNDED, icon_color=_NAVY, icon_size=20,
                                          on_click=on_menu_click),
                    width=36, height=36, border_radius=10,
                    bgcolor=_BORDER_LIGHT, alignment=ft.alignment.center,
                    visible=is_mobile,
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
            ft.Container(
                content=status_filter_buttons,
            ),
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
                mobile_top_bar,
                ft.Container(
                    content=main_content,
                    padding=ft.padding.symmetric(horizontal=12 if is_mobile else 24, vertical=10),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
        bgcolor=_BG,
    )

    # ── Resize handler ──
    def on_resize(e):
        nonlocal is_mobile
        w = page.width or 0
        was_mobile = is_mobile
        is_mobile = w < _SIDEBAR_BREAKPOINT
        if was_mobile != is_mobile:
            sidebar_wrapper.visible = not is_mobile
            page.update()

    page.on_resized = on_resize

    # ── Assemble ──
    page.end_drawer = drawer
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = _BG

    layout = ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(layout)
    page.update()
