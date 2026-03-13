import flet as ft
import asyncio
from .report_issue_page import report_issue_page
from app.services.database.database import db
from .session_manager import SessionManager
from .report_statistics import ReportStatistics
from .navigation_drawer import NavigationDrawerComponent
from .report_card import ReportCard
from .dashboard_ui import DashboardUI
from app.views.components.session_timeout_ui import create_session_timeout_handler

# palette shorthand — resolved dynamically per render
from app.theme import get_colors as _get_colors
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_BORDER = "#E0E6ED"
_WHITE = "#FFFFFF"

_SIDEBAR_BREAKPOINT = 768


def user_dashboard(page: ft.Page, user_data=None, active_section="home"):

    if user_data:
        SessionManager.set_user_data(page, user_data)
    else:
        user_data = SessionManager.validate_session(page)
        if not user_data:
            return

    page.controls.clear()
    page.overlay.clear()
    page.floating_action_button = None
    page.end_drawer = None
    page.drawer = None

    full_name = user_data.get("name", "User")
    first_name = full_name.split()[0] if full_name else "User"
    user_email = user_data.get("email")
    user_type = user_data.get("type", "user")

    # Enrich user_data with profile picture from DB if not already present
    if user_email and not user_data.get("picture"):
        try:
            db_user = db.get_user_by_email(user_email)
            if db_user and db_user.get("picture"):
                user_data["picture"] = db_user["picture"]
        except Exception:
            pass

    if not user_email:
        page.add(ft.Text("Error: No email found in user data", color=ft.Colors.RED))
        page.update()
        return

    # ── Fetch reports ──
    try:
        if user_type == "admin":
            user_reports = db.get_all_reports()
        else:
            user_reports = db.get_reports_by_user(user_email)
    except Exception as e:
        print(f"Error fetching reports: {e}")
        user_reports = []

    if user_reports is None:
        user_reports = []

    stats = ReportStatistics(user_reports)

    is_dark = SessionManager.get_theme_preference(page)
    # Resolve colors for this render
    _t = _get_colors(page)
    _BG = _t["BG"]; _NAVY = _t["NAVY"]; _NAVY_MUTED = _t["NAVY_MUTED"]
    _ACCENT = _t["ACCENT"]; _BORDER = _t["BORDER"]; _WHITE = _t["WHITE"]
    selected_filter = ft.Ref[str]()
    selected_filter.current = "All" if active_section == "reports" else "Pending"

    # ── Callbacks ──
    def report_issue_clicked(e):
        report_issue_page(page, user_data)

    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        user_dashboard(page, user_data)

    def update_dashboard():
        user_dashboard(page, user_data)

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

    # ── Reports list ──
    report_cards_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def update_report_list():
        report_cards_column.controls.clear()
        filtered_reports = stats.get_filtered_reports(selected_filter.current)
        if filtered_reports:
            for report in filtered_reports:
                card = ReportCard(page, report, user_data, update_dashboard)
                report_cards_column.controls.append(card.create())
        else:
            report_cards_column.controls.append(DashboardUI.create_no_reports_message(is_dark=is_dark))
        page.update()

    # ── Filter handler ──
    def filter_changed(filter_name):
        def handler(e):
            selected_filter.current = filter_name
            for btn_name, btn_data in filter_button_refs.items():
                if btn_name == filter_name:
                    btn_data["btn"].bgcolor = _NAVY
                    btn_data["btn"].border = ft.border.all(1, _NAVY)
                    btn_data["text"].color = _WHITE
                else:
                    btn_data["btn"].bgcolor = ft.Colors.TRANSPARENT
                    btn_data["btn"].border = ft.border.all(1, _BORDER)
                    btn_data["text"].color = _NAVY_MUTED
            page.update()
            update_report_list()
        return handler

    filter_buttons, filter_button_refs = DashboardUI.create_filter_buttons(
        filter_changed,
        include_all=active_section == "reports",
        default_filter=selected_filter.current,
        is_dark=is_dark,
    )
    update_report_list()

    # ── Navigation helpers ──
    def nav_handler(key):
        def handler(e):
            if key == "home":
                user_dashboard(page, user_data, active_section="home")
            elif key == "reports":
                user_dashboard(page, user_data, active_section="reports")
            elif key == "account":
                from .account_page import account_page
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

    # ── Build sidebar ──
    sidebar = DashboardUI.create_sidebar(
        first_name, user_data,
        on_nav=nav_handler,
        on_logout=on_logout,
        active=active_section,
        is_dark=is_dark,
        on_toggle_theme=toggle_dark_theme,
    )
    sidebar_ref = ft.Ref[ft.Container]()

    # Wrap sidebar in a ref-able container
    sidebar_wrapper = ft.Container(
        content=sidebar,
        ref=sidebar_ref,
        visible=True,
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # ── Mobile drawer fallback ──
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)

    # ── Top bar ──
    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

    total_issues = stats.get_total_issues()
    resolved = stats.get_resolved_issues()
    pending = len(stats.get_pending_reports())
    ongoing = len(stats.get_ongoing_reports())
    rejected = len(stats.get_rejected_reports())

    # Determine initial sidebar visibility
    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)
    show_sidebar = not is_mobile
    stats_animation_ref = ft.Ref[ft.Container]()
    status_card_refs = []

    top_bar = DashboardUI.create_top_bar(
        first_name, user_type,
        on_report_click=report_issue_clicked,
        on_menu_click=on_menu_click if is_mobile else None,
        is_mobile=is_mobile,
        is_dark=is_dark,
    )
    top_bar_ref = ft.Ref[ft.Container]()

    # ── Main content area ──
    content_pad_h = 12 if is_mobile else 24

    if total_issues > 0:
        if active_section == "reports":
            main_content = ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("My Reports", size=22, font_family="Poppins-Bold", color=_NAVY),
                            ],
                            spacing=2,
                        ),
                        padding=ft.padding.only(bottom=10),
                    ),
                    filter_buttons,
                    ft.Container(height=8),
                    report_cards_column,
                ],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            stats_grid = DashboardUI.create_statistics_grid(
                total_issues,
                resolved,
                pending,
                ongoing,
                rejected,
                is_mobile=is_mobile,
                status_card_refs=status_card_refs,
                is_dark=is_dark,
            )
            main_content = ft.Column(
                [
                    ft.Container(
                        content=stats_grid,
                        opacity=0,
                        ref=stats_animation_ref,
                        animate_opacity=ft.Animation(450, ft.AnimationCurve.EASE_OUT),
                    ),
                    ft.Container(height=8),
                    filter_buttons,
                    ft.Container(height=8),
                    report_cards_column,
                ],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            )
    else:
        if active_section == "reports":
            main_content = ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("My Reports", size=22, font_family="Poppins-Bold", color=_NAVY),
                            ],
                            spacing=2,
                        ),
                        padding=ft.padding.only(bottom=10),
                    ),
                    filter_buttons,
                    ft.Container(height=8),
                    report_cards_column,
                ],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            main_content = DashboardUI.create_empty_state(first_name, is_dark, report_issue_clicked)

    content_padding_ref = ft.Ref[ft.Container]()

    content_area = ft.Container(
        content=ft.Column(
            [
                ft.Container(content=top_bar, ref=top_bar_ref),
                ft.Container(
                    content=main_content,
                    padding=ft.padding.symmetric(horizontal=content_pad_h, vertical=10),
                    expand=True,
                    ref=content_padding_ref,
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
            # rebuild top bar for mobile/desktop
            new_top_bar = DashboardUI.create_top_bar(
                first_name, user_type,
                on_report_click=report_issue_clicked,
                on_menu_click=on_menu_click if is_mobile else None,
                is_mobile=is_mobile,
                is_dark=is_dark,
            )
            if top_bar_ref.current:
                top_bar_ref.current.content = new_top_bar
            # adjust content padding
            if content_padding_ref.current:
                content_padding_ref.current.padding = ft.padding.symmetric(
                    horizontal=12 if is_mobile else 24, vertical=10
                )
            # toggle FAB
            if is_mobile:
                page.floating_action_button = DashboardUI.create_fab(report_issue_clicked, is_dark=is_dark)
            else:
                page.floating_action_button = None
            page.update()

    page.on_resized = on_resize

    # ── Assemble layout ──
    sidebar_wrapper.visible = show_sidebar
    page.end_drawer = drawer  # mobile fallback

    # FAB only on mobile
    if is_mobile:
        page.floating_action_button = DashboardUI.create_fab(report_issue_clicked, is_dark=is_dark)
    else:
        page.floating_action_button = None

    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = _BG

    layout = ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(layout)
    page.update()

    # Subtle page-load reveal for analytics block
    if stats_animation_ref.current:
        stats_animation_ref.current.opacity = 1
        page.update()

    async def stagger_status_cards():
        for idx, card_ref in enumerate(status_card_refs):
            await asyncio.sleep(0.08 if idx else 0.02)
            if card_ref.current:
                card_ref.current.opacity = 1
                page.update()

    if status_card_refs:
        page.run_task(stagger_status_cards)