import flet as ft
from app.services.database.database import db
from app.views.dashboard.session_manager import SessionManager
from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
from app.views.dashboard.dashboard_ui import DashboardUI
from .dashboard_data_manager import DataManager
from .admin_dashboard_ui import UIComponents
from .dashboard_controller import DashboardController, DashboardState
from .analytics_ui import AnalyticsUI
from app.views.components.session_timeout_ui import create_session_timeout_handler

# ── Palette ──
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_WHITE = "#FFFFFF"
_GREEN = "#15803D"
_GREEN_BG = "#DCFCE7"
_AMBER = "#B45309"
_AMBER_BG = "#FEF3C7"

_SIDEBAR_BREAKPOINT = 768


def admin_dashboard(page: ft.Page, user_data=None):
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
    user_email = user_data.get("email", "")
    user_type = user_data.get("type", "admin")

    # Enrich picture from DB
    if user_email and not user_data.get("picture"):
        try:
            db_user = db.get_user_by_email(user_email)
            if db_user and db_user.get("picture"):
                user_data["picture"] = db_user["picture"]
        except Exception:
            pass

    is_dark = SessionManager.get_theme_preference(page)

    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        admin_dashboard(page, user_data)

    # ── Data ──
    state = DashboardState()
    data_manager = DataManager()
    ui_components = UIComponents()
    controller = DashboardController(page, user_data, state, data_manager, ui_components)

    # ── Session timeout ──
    def on_logout_callback():
        from app.views.loginpage import loginpage
        page.controls.clear()
        page.overlay.clear()
        page.floating_action_button = None
        page.end_drawer = None
        page.drawer = None
        page.on_resized = None
        loginpage(page)

    session_timeout_handler = create_session_timeout_handler(
        page, user_email, on_logout_callback
    )

    # ── Nav callbacks ──
    def nav_handler(key):
        def handler(e):
            if key == "home":
                admin_dashboard(page, user_data)
            elif key == "reports":
                from .admin_all_reports import admin_all_reports
                admin_all_reports(page, user_data)
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

    # ── Admin sidebar ──
    def _create_admin_sidebar():
        def nav_item(icon, label, key, on_click):
            is_active = key == "home"
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
            nav_item(ft.Icons.GRID_VIEW_ROUNDED, "Dashboard", "home", nav_handler("home")),
            nav_item(ft.Icons.CAMPAIGN_OUTLINED, "Reports", "reports", nav_handler("reports")),
            nav_item(ft.Icons.SECURITY_OUTLINED, "Audit Logs", "audit", lambda e: _nav_audit()),
            nav_item(ft.Icons.VISIBILITY_OUTLINED, "User Activity", "activity", lambda e: _nav_activity()),
            nav_item(ft.Icons.PERSON_OUTLINE_ROUNDED, "Account", "account", nav_handler("account")),
        ]

        picture = user_data.get("picture")
        first_letter = full_name[0].upper() if full_name else "A"

        return ft.Container(
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

    def _nav_audit():
        from .audit_logs_viewer import audit_logs_page
        audit_logs_page(page, user_data)

    def _nav_activity():
        from .user_activity_monitoring import user_activity_monitoring_page
        user_activity_monitoring_page(page, user_data)

    sidebar = _create_admin_sidebar()
    sidebar_ref = ft.Ref[ft.Container]()
    sidebar_wrapper = ft.Container(
        content=sidebar, ref=sidebar_ref, visible=True,
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # ── Mobile drawer fallback ──
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)

    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)
    show_sidebar = not is_mobile

    def navigate_to_all_categories(e):
        from .admin_all_reports import admin_all_reports
        admin_all_reports(page, user_data)

    # ── Top bar (mobile-aware) ──
    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

    top_bar = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(
                            f"Hi, {first_name}",
                            size=16 if is_mobile else 20,
                            font_family="Poppins-Bold",
                            color=_NAVY,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            "Here's today's overview",
                            size=11 if is_mobile else 12,
                            font_family="Poppins-Light",
                            color=_NAVY_MUTED,
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Container(
                    content=ft.IconButton(
                        ft.Icons.MENU_ROUNDED, icon_color=_NAVY, icon_size=20,
                        on_click=on_menu_click,
                    ),
                    width=36, height=36, border_radius=10,
                    bgcolor=_BORDER_LIGHT, alignment=ft.alignment.center,
                    visible=is_mobile,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=14 if is_mobile else 28, vertical=12 if is_mobile else 18),
        bgcolor=_WHITE,
        border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
    )
    top_bar_ref = ft.Ref[ft.Container]()

    # ── Main content ──
    content_pad_h = 12 if is_mobile else 24

    # ── Analytics data ──
    reports_per_day = db.get_reports_per_day(days=7)
    reports_per_category = db.get_reports_per_category()
    reports_per_location = db.get_reports_per_location()
    resolution_rate = db.get_resolution_rate()
    total_users = db.get_total_users_count()
    top_reporters = db.get_top_reporters(limit=5)
    all_reports_for_stats = db.get_all_reports() or []
    status_counts = DataManager.calculate_status_counts(all_reports_for_stats)
    total_reports = len(all_reports_for_stats)

    # ── Analytics widgets ──
    daily_trend = AnalyticsUI.daily_trend_chart(reports_per_day, days=7)
    category_chart = AnalyticsUI.horizontal_bar_chart(
        reports_per_category, title="Reports by Category",
        max_bars=6, value_key="count", label_key="category",
    )
    location_chart = AnalyticsUI.horizontal_bar_chart(
        reports_per_location, title="Reports by Location",
        max_bars=6, value_key="count", label_key="location",
    )
    resolution_ring = AnalyticsUI.resolution_ring(resolution_rate)
    reporters_card = AnalyticsUI.top_reporters_card(top_reporters)
    status_bar = AnalyticsUI.status_distribution_bar(status_counts, total_reports)

    # Analytics summary row
    analytics_summary = ft.ResponsiveRow(
        [
            ft.Container(
                content=AnalyticsUI.mini_stat(
                    "Total Reports", total_reports,
                    ft.Icons.DESCRIPTION_OUTLINED, _ACCENT, "#DBEAFE",
                ),
                col={"xs": 6, "sm": 6, "md": 3},
            ),
            ft.Container(
                content=AnalyticsUI.mini_stat(
                    "Users", total_users,
                    ft.Icons.PEOPLE_OUTLINE_ROUNDED, "#7C3AED", "#EDE9FE",
                ),
                col={"xs": 6, "sm": 6, "md": 3},
            ),
            ft.Container(
                content=AnalyticsUI.mini_stat(
                    "Resolved", resolution_rate.get('resolved', 0),
                    ft.Icons.CHECK_CIRCLE_OUTLINE, _GREEN, _GREEN_BG,
                ),
                col={"xs": 6, "sm": 6, "md": 3},
            ),
            ft.Container(
                content=AnalyticsUI.mini_stat(
                    "Resolution %", f"{resolution_rate.get('rate', 0)}%",
                    ft.Icons.TRENDING_UP_ROUNDED, _AMBER, _AMBER_BG,
                ),
                col={"xs": 6, "sm": 6, "md": 3},
            ),
        ],
        spacing=10, run_spacing=10,
    )

    # Analytics charts row (responsive)
    analytics_charts_row = ft.ResponsiveRow(
        [
            ft.Container(content=daily_trend, col={"xs": 12, "md": 6}),
            ft.Container(content=resolution_ring, col={"xs": 12, "md": 6}),
        ],
        spacing=10, run_spacing=10,
    )

    analytics_detail_row = ft.ResponsiveRow(
        [
            ft.Container(content=category_chart, col={"xs": 12, "md": 4}),
            ft.Container(content=location_chart, col={"xs": 12, "md": 4}),
            ft.Container(content=reporters_card, col={"xs": 12, "md": 4}),
        ],
        spacing=10, run_spacing=10,
    )

    main_content = ft.Column(
        [
            # Stats grid
            ft.ResponsiveRow(state.stats_row.controls, spacing=10, run_spacing=10),
            ft.Container(height=12),
            # Filter buttons
            ft.Container(
                content=ft.Row(state.category_filter_buttons.controls, spacing=6,
                               scroll=ft.ScrollMode.AUTO, tight=True),
            ),
            ft.Container(height=12),
            # Section header
            ft.Row(
                [
                    ft.Text("Top Categories", size=14, font_family="Poppins-SemiBold", color=_NAVY),
                    ft.Container(expand=True),
                    ft.TextButton(
                        content=ft.Text("View All", size=12, font_family="Poppins-Medium", color=_ACCENT),
                        on_click=navigate_to_all_categories,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=4),
            # Category list
            ft.Container(
                content=state.category_list_view,
                expand=True,
            ),
            # ── Data Analytics ──
            ft.Container(height=20),
            AnalyticsUI.section_header("Data Analytics", ft.Icons.ANALYTICS_OUTLINED),
            ft.Container(height=10),
            analytics_summary,
            ft.Container(height=12),
            status_bar,
            ft.Container(height=12),
            analytics_charts_row,
            ft.Container(height=12),
            analytics_detail_row,
            ft.Container(height=20),
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    content_area = ft.Container(
        content=ft.Column(
            [
                ft.Container(content=top_bar, ref=top_bar_ref),
                ft.Container(
                    content=main_content,
                    padding=ft.padding.symmetric(horizontal=content_pad_h, vertical=10),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
        bgcolor=_BG,
    )

    # ── Responsive handler ──
    def on_resize(e):
        nonlocal show_sidebar, is_mobile
        w = page.width or 0
        was_mobile = is_mobile
        is_mobile = w < _SIDEBAR_BREAKPOINT
        show_sidebar = not is_mobile

        if was_mobile != is_mobile:
            sidebar_wrapper.visible = show_sidebar
            page.update()

    page.on_resized = on_resize

    # ── Assemble ──
    sidebar_wrapper.visible = show_sidebar
    page.end_drawer = drawer
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = _BG

    layout = ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(layout)
    controller.refresh_dashboard()
    page.update()

