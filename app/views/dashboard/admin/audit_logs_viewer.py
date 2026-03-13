"""Audit Log Viewer – admin compliance and debugging."""

import flet as ft
from datetime import datetime
from app.services.audit.audit_logger import audit_logger
from .admin_sidebar import create_admin_sidebar

# ── Fallback palette (shadowed by theme-resolved locals at runtime) ──
_BG           = "#F5F7FA"
_NAVY         = "#0F2B5B"
_NAVY_MUTED   = "#64748B"
_ACCENT       = "#1565C0"
_BORDER       = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_WHITE        = "#FFFFFF"

_SIDEBAR_BREAKPOINT = 768

_ACTION_LABELS = {
    "login":                "Logged In",
    "logout":               "Logged Out",
    "report_create":        "Report Created",
    "report_update":        "Report Updated",
    "report_delete":        "Report Deleted",
    "report_status_change": "Status Changed",
    "user_edit":            "Profile Edited",
    "user_create":          "User Created",
    "user_delete":          "User Deleted",
    "password_change":      "Password Changed",
    "admin_view":           "Admin Access",
}


def get_action_description(action_type, resource_type=None, details=None):
    return _ACTION_LABELS.get(action_type, action_type)


def audit_logs_page(page: ft.Page, user_data=None):
    page.controls.clear()
    page.overlay.clear()
    page.floating_action_button = None
    page.end_drawer = None
    page.drawer    = None
    page.scroll    = None

    if not user_data:
        user_data = page.session.get("user_data")

    if not user_data or user_data.get("type", "").lower() != "admin":
        page.snack_bar = ft.SnackBar(ft.Text("Access Denied: Admin only"))
        page.snack_bar.open = True
        page.update()
        return

    is_dark   = page.session.get("is_dark_theme") or False
    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)

    from app.theme import get_colors as _get_theme
    _t            = _get_theme(page)
    _BG           = _t["BG"];           _NAVY         = _t["NAVY"]
    _NAVY_MUTED   = _t["NAVY_MUTED"];   _ACCENT       = _t["ACCENT"]
    _WHITE        = _t["WHITE"];        _BORDER       = _t["BORDER"]
    _BORDER_LIGHT = _t["BORDER_LIGHT"]; _CARD         = _t["CARD"]

    from app.views.dashboard.session_manager   import SessionManager
    from app.views.dashboard.navigation_drawer import NavigationDrawerComponent

    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        audit_logs_page(page, user_data)

    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer     = nav_drawer.create_drawer(is_dark)

    sidebar, _ = create_admin_sidebar(
        page, user_data, active_key="audit", on_toggle_theme=toggle_dark_theme,
    )
    sidebar_wrapper = ft.Container(content=sidebar, visible=not is_mobile)

    def go_back(e=None):
        from .admin_dashboard import admin_dashboard
        admin_dashboard(page, user_data)

    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

    # ── Header ──────────────────────────────────────────────────────
    header = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_ROUNDED,
                            icon_color=_NAVY, icon_size=20,
                            on_click=go_back,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "Audit Logs",
                                    size=18 if is_mobile else 20,
                                    font_family="Poppins-Bold",
                                    color=_NAVY,
                                ),
                                ft.Text(
                                    "Track all admin and user actions",
                                    size=11, color=_NAVY_MUTED,
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=2,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=16 if is_mobile else 28, vertical=14),
        bgcolor=_WHITE,
        border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
    )

    # ── Filter fields ────────────────────────────────────────────────
    _fkw = dict(
        border_color=_BORDER, focused_border_color=_ACCENT,
        color=_NAVY, label_style=ft.TextStyle(color=_NAVY_MUTED),
        hint_style=ft.TextStyle(color=_NAVY_MUTED),
        bgcolor=_CARD, border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
    )
    _dkw = dict(
        border_color=_BORDER, focused_border_color=_ACCENT,
        color=_NAVY, label_style=ft.TextStyle(color=_NAVY_MUTED),
        bgcolor=_CARD, border_radius=8,
    )

    filter_actor_email = ft.TextField(label="Actor Email", width=220, **_fkw)
    filter_action = ft.Dropdown(
        label="Action Type", width=200, **_dkw,
        options=[
            ft.dropdown.Option("login"),
            ft.dropdown.Option("logout"),
            ft.dropdown.Option("report_create"),
            ft.dropdown.Option("report_update"),
            ft.dropdown.Option("report_delete"),
            ft.dropdown.Option("user_edit"),
            ft.dropdown.Option("password_change"),
        ],
    )
    filter_status = ft.Dropdown(
        label="Status", width=150, **_dkw,
        options=[
            ft.dropdown.Option("success"),
            ft.dropdown.Option("failed"),
        ],
    )
    start_date_field = ft.TextField(
        label="Start Date", hint_text="YYYY-MM-DD", width=180,
        prefix_icon=ft.Icons.CALENDAR_TODAY_OUTLINED, **_fkw,
    )
    end_date_field = ft.TextField(
        label="End Date", hint_text="YYYY-MM-DD", width=180,
        prefix_icon=ft.Icons.CALENDAR_TODAY_OUTLINED, **_fkw,
    )

    # ── Logs list & pagination state ────────────────────────────────
    logs_list       = ft.Column(spacing=8)
    pagination_info = ft.Text("", size=12, color=_NAVY_MUTED)
    current_page    = {"page": 0}
    page_size       = 50

    prev_btn = ft.TextButton(
        "← Previous",
        style=ft.ButtonStyle(color=_ACCENT),
        on_click=lambda e: _go_prev(e),
        disabled=True,
    )
    next_btn = ft.TextButton(
        "Next →",
        style=ft.ButtonStyle(color=_ACCENT),
        on_click=lambda e: _go_next(e),
        disabled=True,
    )

    def load_logs():
        logs_list.controls.clear()

        actor_email = filter_actor_email.value.strip() or None
        action_type = filter_action.value or None
        start_date  = start_date_field.value.strip() or None
        end_date    = end_date_field.value.strip() or None

        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").isoformat()
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").isoformat()
        except ValueError:
            logs_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINE, color=_t["RED"], size=16),
                            ft.Text("Invalid date. Use YYYY-MM-DD.", color=_t["RED"], size=13),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(horizontal=14, vertical=10),
                    bgcolor=_t["RED_BG"], border_radius=8,
                    border=ft.border.all(1, _t["RED"]),
                )
            )
            page.update()
            return

        offset      = current_page["page"] * page_size
        logs        = audit_logger.get_audit_logs(
            actor_email=actor_email, action_type=action_type,
            start_date=start_date,   end_date=end_date,
            limit=page_size,         offset=offset,
        )
        total_count = audit_logger.get_audit_logs_count(
            actor_email=actor_email, action_type=action_type,
            start_date=start_date,   end_date=end_date,
        )

        total_pages            = max(1, (total_count + page_size - 1) // page_size)
        prev_btn.disabled      = current_page["page"] == 0
        next_btn.disabled      = current_page["page"] >= total_pages - 1
        pagination_info.value  = (
            f"Page {current_page['page'] + 1} of {total_pages}  ·  {total_count:,} logs"
        )

        if not logs:
            logs_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF_OUTLINED,
                                    color=_NAVY_MUTED, size=40),
                            ft.Text("No logs found", size=14, color=_NAVY_MUTED,
                                    font_family="Poppins-SemiBold"),
                            ft.Text("Try adjusting the filters.", size=12, color=_NAVY_MUTED),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(vertical=48),
                )
            )
        else:
            for log in logs:
                action_desc  = get_action_description(log["action_type"])
                is_success   = log["status"] == "success"
                status_color = _t["GREEN"] if is_success else _t["RED"]
                status_bg    = _t["GREEN_BG"] if is_success else _t["RED_BG"]

                details_row = []
                if log.get("details"):
                    details_row = [
                        ft.Container(
                            content=ft.Text(
                                f"Details: {log['details']}",
                                size=11, color=_NAVY_MUTED, italic=True,
                            ),
                            padding=ft.padding.only(top=6),
                        )
                    ]

                log_card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    # Actor
                                    ft.Column(
                                        [
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                                                            size=14, color=_ACCENT),
                                                    ft.Text(
                                                        log["actor_name"] or log["actor_email"],
                                                        size=13, font_family="Poppins-SemiBold",
                                                        color=_NAVY,
                                                    ),
                                                ],
                                                spacing=4,
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            ft.Text(log["actor_email"], size=11, color=_NAVY_MUTED),
                                        ],
                                        spacing=1, expand=True,
                                    ),
                                    # Action + resource
                                    ft.Column(
                                        [
                                            ft.Container(
                                                content=ft.Text(action_desc, size=11, color=_ACCENT),
                                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                                bgcolor=_BORDER_LIGHT, border_radius=10,
                                            ),
                                            ft.Text(
                                                f"{log['resource_type'] or 'N/A'}  ·  ID {log['resource_id'] or 'N/A'}",
                                                size=11, color=_NAVY_MUTED,
                                            ),
                                        ],
                                        spacing=4, expand=True,
                                    ),
                                    # Timestamp + status badge
                                    ft.Column(
                                        [
                                            ft.Text(log["timestamp"][:19], size=11, color=_NAVY_MUTED),
                                            ft.Container(
                                                content=ft.Text(
                                                    "✓ Success" if is_success else "✗ Failed",
                                                    size=10, color=status_color,
                                                    font_family="Poppins-Medium",
                                                ),
                                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                                bgcolor=status_bg, border_radius=10,
                                            ),
                                        ],
                                        spacing=4,
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12,
                            ),
                            *details_row,
                        ],
                        spacing=0,
                    ),
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    bgcolor=_CARD,
                    border_radius=8,
                    border=ft.border.only(
                        left=ft.BorderSide(3, status_color),
                        top=ft.BorderSide(1, _BORDER),
                        right=ft.BorderSide(1, _BORDER),
                        bottom=ft.BorderSide(1, _BORDER),
                    ),
                )
                logs_list.controls.append(log_card)

        page.update()

    def on_filter_click(e):
        current_page["page"] = 0
        load_logs()

    def on_clear_click(e):
        filter_actor_email.value = ""
        filter_action.value      = None
        filter_status.value      = None
        start_date_field.value   = ""
        end_date_field.value     = ""
        current_page["page"]     = 0
        load_logs()

    def _go_prev(e):
        if current_page["page"] > 0:
            current_page["page"] -= 1
            load_logs()

    def _go_next(e):
        current_page["page"] += 1
        load_logs()

    def on_export_csv(e):
        import csv

        actor_email = filter_actor_email.value.strip() or None
        action_type = filter_action.value or None
        logs        = audit_logger.get_audit_logs(
            actor_email=actor_email, action_type=action_type, limit=10_000,
        )
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename    = f"audit_logs_{timestamp}.csv"

        try:
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=[
                        "id", "actor_email", "actor_name", "action_type",
                        "resource_type", "resource_id", "details", "timestamp", "status",
                    ],
                )
                writer.writeheader()
                writer.writerows(logs)
            page.snack_bar = ft.SnackBar(ft.Text(f"Exported: {filename}"))
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Export failed: {ex}"),
                                         bgcolor=_t["RED"])

        page.snack_bar.open = True
        page.update()

    # ── Filter card ──────────────────────────────────────────────────
    filter_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.FILTER_LIST_ROUNDED, color=_ACCENT, size=18),
                        ft.Text("Filters", size=15, font_family="Poppins-SemiBold",
                                color=_NAVY),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [filter_actor_email, filter_action, filter_status,
                     start_date_field, end_date_field],
                    spacing=10, wrap=True,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Search",
                            icon=ft.Icons.SEARCH_ROUNDED,
                            on_click=on_filter_click,
                            bgcolor=_ACCENT, color="#FFFFFF", elevation=0,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.OutlinedButton(
                            "Clear",
                            icon=ft.Icons.CLEAR_ALL_ROUNDED,
                            on_click=on_clear_click,
                            style=ft.ButtonStyle(
                                color=_NAVY_MUTED,
                                side=ft.BorderSide(1, _BORDER),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.ElevatedButton(
                            "Export CSV",
                            icon=ft.Icons.DOWNLOAD_ROUNDED,
                            on_click=on_export_csv,
                            bgcolor="#16A34A", color="#FFFFFF", elevation=0,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                    ],
                    spacing=10,
                ),
            ],
            spacing=10,
        ),
        padding=ft.padding.all(16),
        bgcolor=_CARD,
        border_radius=10,
        border=ft.border.all(1, _BORDER),
    )

    # ── Main body ────────────────────────────────────────────────────
    main_body = ft.Column(
        [
            filter_card,
            ft.Container(height=16),
            ft.Row(
                [
                    ft.Icon(ft.Icons.LIST_ALT_ROUNDED, color=_ACCENT, size=18),
                    ft.Text("Logs", size=15, font_family="Poppins-SemiBold", color=_NAVY),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=6),
            logs_list,
            ft.Container(height=8),
            ft.Row(
                [prev_btn, ft.Container(expand=True), pagination_info,
                 ft.Container(expand=True), next_btn],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        spacing=0,
    )

    content_area = ft.Container(
        content=ft.Column(
            [
                header,
                ft.Container(
                    content=main_body,
                    padding=ft.padding.symmetric(
                        horizontal=12 if is_mobile else 28, vertical=16,
                    ),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        bgcolor=_BG,
    )

    # ── Resize handler ───────────────────────────────────────────────
    def on_resize(e):
        nonlocal is_mobile
        w = page.width or 0
        was_mobile = is_mobile
        is_mobile  = w < _SIDEBAR_BREAKPOINT
        if was_mobile != is_mobile:
            sidebar_wrapper.visible = not is_mobile
            page.update()

    page.on_resized = on_resize

    # ── Assemble ─────────────────────────────────────────────────────
    page.end_drawer = drawer
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor    = _BG

    page.add(ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    ))

    load_logs()
