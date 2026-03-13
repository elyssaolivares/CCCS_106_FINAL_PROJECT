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


def admin_category_reports(page: ft.Page, user_data=None, category=None, status=None):
    """Detailed reports page for a specific category, optionally filtered by status."""
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
    # Resolve palette from theme
    from app.theme import get_colors as _get_theme
    _t = _get_theme(page)
    _BG = _t["BG"]; _NAVY = _t["NAVY"]; _NAVY_MUTED = _t["NAVY_MUTED"]
    _ACCENT = _t["ACCENT"]; _WHITE = _t["WHITE"]
    _BORDER = _t["BORDER"]; _BORDER_LIGHT = _t["BORDER_LIGHT"]

    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        admin_category_reports(page, user_data, category, status)

    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    ui_components = UIComponents()

    # ── Data ──
    all_reports = db.get_all_reports() or []

    if category:
        filtered_reports = [r for r in all_reports if r.get("category", "Uncategorized") == category]
    else:
        filtered_reports = all_reports

    if status:
        sf = (status or "").strip().lower()
        filtered_reports = [r for r in filtered_reports if (r.get("status") or "").strip().lower() == sf]

    reports_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    status_filter_buttons = ft.Row(spacing=6, scroll=ft.ScrollMode.AUTO, tight=True)

    def update_status_filters():
        status_filter_buttons.controls.clear()
        category_reports = (
            [r for r in all_reports if r.get("category", "Uncategorized") == category]
            if category
            else all_reports
        )
        status_counts = {"Pending": 0, "In Progress": 0, "Resolved": 0, "Rejected": 0}
        for report in category_reports:
            canon = StatusNormalizer.canonicalize(report.get("status", "Pending"))
            status_counts[canon] = status_counts.get(canon, 0) + 1

        # "All" button
        all_active = status is None
        all_btn = ft.Container(
            content=ui_components.create_tab_button("All", len(category_reports), all_active, is_dark=is_dark),
            on_click=lambda e: admin_category_reports(page, user_data, category, None),
        )
        status_filter_buttons.controls.append(all_btn)

        for s_label in ["Pending", "In Progress", "Resolved", "Rejected"]:
            count = status_counts.get(s_label, 0)
            is_active = status == s_label
            btn = ft.Container(
                content=ui_components.create_tab_button(s_label, count, is_active, is_dark=is_dark),
                on_click=lambda e, st=s_label: admin_category_reports(page, user_data, category, st),
            )
            status_filter_buttons.controls.append(btn)

    def handle_status_change(report_id, new_status, remarks=""):
        from app.services.audit.audit_logger import audit_logger
        admin_email = user_data.get("email", "unknown@example.com") if user_data else "unknown@example.com"
        admin_name = user_data.get("name", "Unknown Admin") if user_data else "Unknown Admin"

        db.update_report_status(report_id, new_status, remarks=remarks, updated_by=admin_email)

        remark_note = f" | Remarks: {remarks}" if remarks else ""
        audit_logger.log_action(
            actor_email=admin_email,
            actor_name=admin_name,
            action_type="report_status_change",
            resource_type="report",
            resource_id=report_id,
            details=f"Changed report status to {new_status}{remark_note}",
            status="success",
        )

        admin_category_reports(page, user_data, category, status)

    def handle_report_delete(report_id):
        from app.services.audit.audit_logger import audit_logger
        admin_email = user_data.get("email", "unknown@example.com") if user_data else "unknown@example.com"
        admin_name = user_data.get("name", "Unknown Admin") if user_data else "Unknown Admin"

        try:
            report = db.get_report_by_id(report_id)
            report_location = (report or {}).get("location", "Unknown location")

            db.delete_report(report_id)

            audit_logger.log_action(
                actor_email=admin_email,
                actor_name=admin_name,
                action_type="report_delete",
                resource_type="report",
                resource_id=report_id,
                details=f"Deleted report at {report_location}",
                status="success",
            )

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Report deleted successfully."),
                bgcolor=ft.Colors.GREEN_600,
            )
            page.snack_bar.open = True
            page.update()
            admin_category_reports(page, user_data, category, status)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Delete failed: {str(ex)}"),
                bgcolor=ft.Colors.RED_600,
            )
            page.snack_bar.open = True
            page.update()

    if not filtered_reports:
        reports_list.controls.append(ui_components.create_empty_category_message(category, is_dark=is_dark))
    else:
        for report in filtered_reports:
            report_card = ui_components.create_report_card(
                report,
                handle_status_change,
                page=page,
                on_delete=handle_report_delete,
            )
            reports_list.controls.append(report_card)

    if category:
        update_status_filters()

    # ── Top bar ──
    _SIDEBAR_BREAKPOINT = 768
    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)

    def go_back(e=None):
        from .admin_all_reports import admin_all_reports
        admin_all_reports(page, user_data)

    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

    # ── Admin sidebar ──
    sidebar, _ = create_admin_sidebar(page, user_data, active_key="reports", on_toggle_theme=toggle_dark_theme)
    sidebar_wrapper = ft.Container(content=sidebar, visible=not is_mobile)

    title = category or "Reports"
    subtitle = f"Filtered: {status}" if status else "All statuses"

    top_bar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, icon_color=_NAVY, icon_size=20, on_click=go_back),
                ft.Column(
                    [
                        ft.Text(title, size=16, font_family="Poppins-Bold", color=_NAVY,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(subtitle, size=11, font_family="Poppins-Light", color=_NAVY_MUTED),
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
    content_items = []
    if category:
        content_items.extend([status_filter_buttons, ft.Container(height=12)])
    content_items.append(reports_list)

    main_content = ft.Column(
        content_items,
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
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = _BG

    layout = ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(layout)
    page.update()
