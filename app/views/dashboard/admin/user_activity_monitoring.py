"""User Activity Monitoring Dashboard - displays login history, failed attempts, geo-location."""

import flet as ft
from app.services.activity.activity_monitor import activity_monitor
from .admin_sidebar import create_admin_sidebar

_BG           = "#F5F7FA"
_NAVY         = "#0F2B5B"
_NAVY_MUTED   = "#64748B"
_ACCENT       = "#1565C0"
_BORDER       = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_WHITE        = "#FFFFFF"
_CARD         = "#FFFFFF"

_SIDEBAR_BREAKPOINT = 768


def user_activity_monitoring_page(page: ft.Page, user_data=None):
    page.controls.clear()
    page.overlay.clear()
    page.floating_action_button = None
    page.end_drawer = None
    page.drawer = None
    page.scroll = None

    if not user_data:
        user_data = page.session.get("user_data")

    if not user_data or user_data.get("type", "").lower() != "admin":
        page.snack_bar = ft.SnackBar(ft.Text("Access Denied: Admin only"))
        page.snack_bar.open = True
        page.update()
        return

    is_dark = page.session.get("is_dark_theme") or False
    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)

    from app.theme import get_colors as _get_theme
    _t = _get_theme(page)
    _BG           = _t["BG"]
    _NAVY         = _t["NAVY"]
    _NAVY_MUTED   = _t["NAVY_MUTED"]
    _ACCENT       = _t["ACCENT"]
    _WHITE        = _t["WHITE"]
    _BORDER       = _t["BORDER"]
    _BORDER_LIGHT = _t["BORDER_LIGHT"]
    _CARD         = _t["CARD"]

    from app.views.dashboard.session_manager import SessionManager
    from app.views.dashboard.navigation_drawer import NavigationDrawerComponent

    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        user_activity_monitoring_page(page, user_data)

    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)

    sidebar, _ = create_admin_sidebar(page, user_data, active_key="activity", on_toggle_theme=toggle_dark_theme)
    sidebar_wrapper = ft.Container(content=sidebar, visible=not is_mobile)

    def go_back(e=None):
        from .admin_dashboard import admin_dashboard
        admin_dashboard(page, user_data)

    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

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
                                    "User Activity Monitoring",
                                    size=18 if is_mobile else 20,
                                    font_family="Poppins-Bold",
                                    color=_NAVY,
                                ),
                                ft.Text(
                                    "Login history, failed attempts & geo-location",
                                    size=11,
                                    color=_NAVY_MUTED,
                                ),
                            ],
                            spacing=1,
                        ),
                    ],
                    spacing=4,
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

    # ── Shared helpers ──
    def _field(**kw):
        return ft.TextField(
            border_color=_BORDER,
            focused_border_color=_ACCENT,
            bgcolor=_CARD,
            color=_NAVY,
            label_style=ft.TextStyle(color=_NAVY_MUTED),
            content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
            border_radius=8,
            **kw,
        )

    def _mini_stat(label, value, value_color=None):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=10, color=_NAVY_MUTED),
                    ft.Text(str(value), size=16, font_family="Poppins-Bold",
                            color=value_color or _NAVY),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            bgcolor=_CARD,
            border=ft.border.all(1, _BORDER),
            border_radius=8,
        )

    def _search_btn(on_click):
        return ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH_ROUNDED,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=_ACCENT,
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
            ),
        )

    # ── Tab state ──
    main_view_container = ft.Container()
    tab_buttons = {}

    _tab_defs = [
        ("all_users",       ft.Icons.PEOPLE_ROUNDED,        "All Users"),
        ("user_details",    ft.Icons.PERSON_SEARCH_ROUNDED,  "User Details"),
        ("failed_attempts", ft.Icons.LOCK_PERSON_ROUNDED,    "Failed Attempts"),
    ]

    def switch_tab(key):
        views = {
            "all_users":       all_users_view,
            "user_details":    user_detail_view,
            "failed_attempts": failed_attempts_view,
        }
        main_view_container.content = views[key]
        for k, btn in tab_buttons.items():
            active = k == key
            btn.bgcolor = _BORDER_LIGHT if active else "transparent"
            btn.border = ft.border.only(
                bottom=ft.BorderSide(2, _ACCENT if active else "transparent")
            )
            row = btn.content
            row.controls[0].color = _ACCENT if active else _NAVY_MUTED
            row.controls[1].color = _ACCENT if active else _NAVY_MUTED
        page.update()

    # === TAB 1: All Users Stats ===
    all_users_list = ft.Column(spacing=8)

    def load_all_users_stats():
        all_users_list.controls.clear()
        all_stats = activity_monitor.get_all_user_stats(limit=50)

        if not all_stats:
            all_users_list.controls.append(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.PEOPLE_OUTLINE_ROUNDED, size=40, color=_NAVY_MUTED),
                        ft.Text("No user activity data available", size=13, color=_NAVY_MUTED),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                )
            )
        else:
            for stat in all_stats:
                last_login_str = stat["last_login"] if stat["last_login"] else "Never"
                has_failed = stat["total_failed_attempts"] > 0
                left_color = _t["RED"] if has_failed else _BORDER

                card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Row(
                                                [
                                                    ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED,
                                                            size=14, color=_NAVY_MUTED),
                                                    ft.Text(stat["email"], size=12,
                                                            font_family="Poppins-Bold",
                                                            color=_NAVY),
                                                ],
                                                spacing=4,
                                            ),
                                            ft.Text(
                                                stat["last_login_location"] or "Unknown location",
                                                size=11, color=_NAVY_MUTED,
                                            ),
                                        ],
                                        spacing=3,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                str(stat["total_logins"]) + " logins",
                                                size=11, color=_NAVY,
                                            ),
                                            ft.Text(
                                                str(stat["total_failed_attempts"]) + " failed",
                                                size=11,
                                                color=_t["RED"] if has_failed else _t["GREEN"],
                                            ),
                                        ],
                                        spacing=3,
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                expand=True,
                            ),
                            ft.Container(height=1, bgcolor=_BORDER),
                            ft.Row(
                                [
                                    ft.Text("Last login: " + last_login_str, size=10, color=_NAVY_MUTED),
                                    ft.Text("IP: " + (stat["last_login_ip"] or "N/A"), size=10, color=_NAVY_MUTED),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.all(12),
                    bgcolor=_CARD,
                    border=ft.border.only(
                        left=ft.BorderSide(3, left_color),
                        top=ft.BorderSide(1, _BORDER),
                        right=ft.BorderSide(1, _BORDER),
                        bottom=ft.BorderSide(1, _BORDER),
                    ),
                    border_radius=8,
                )
                all_users_list.controls.append(card)

        page.update()

    all_users_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.PEOPLE_ROUNDED, size=16, color=_ACCENT),
                    ft.Text("All Users", size=14, font_family="Poppins-Bold", color=_NAVY),
                ],
                spacing=6,
            ),
            ft.Text("Login statistics for all registered users", size=11, color=_NAVY_MUTED),
            ft.Container(height=4),
            all_users_list,
        ],
        spacing=6,
    )

    # === TAB 2: User Activity Details ===
    search_email = _field(label="Enter user email...", width=300)
    activity_list = ft.Column(spacing=8)
    stats_display = ft.Column(spacing=10)

    def load_user_activity(email):
        activity_list.controls.clear()
        stats_display.controls.clear()

        stats = activity_monitor.get_user_stats(email)
        if stats:
            last_login = stats["last_login"] if stats["last_login"] else "Never"
            failed_color = _t["RED"] if stats["total_failed_attempts"] > 0 else _t["GREEN"]

            stats_display.controls.extend([
                ft.Row(
                    [
                        _mini_stat("Total Logins", stats["total_logins"]),
                        _mini_stat("Failed Attempts", stats["total_failed_attempts"], failed_color),
                        _mini_stat("Last Login", last_login[:10] if last_login != "Never" else "Never"),
                    ],
                    spacing=10,
                    wrap=True,
                ),
                ft.Container(height=4),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, size=14, color=_NAVY_MUTED),
                                    ft.Text("Location Info", size=12,
                                            font_family="Poppins-Bold", color=_NAVY),
                                ],
                                spacing=4,
                            ),
                            ft.Text("Last IP: " + (stats["last_login_ip"] or "N/A"), size=11, color=_NAVY_MUTED),
                            ft.Text("Last Location: " + (stats["last_login_location"] or "Unknown"), size=11, color=_NAVY_MUTED),
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.all(12),
                    bgcolor=_CARD,
                    border=ft.border.all(1, _BORDER),
                    border_radius=8,
                ),
            ])

        activities = activity_monitor.get_user_activity(email, limit=50)
        if not activities:
            activity_list.controls.append(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.HISTORY_ROUNDED, size=36, color=_NAVY_MUTED),
                        ft.Text("No activity history found", size=12, color=_NAVY_MUTED),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                )
            )
        else:
            for activity in activities:
                is_success = activity["status"] == "success"
                status_color = _t["GREEN"] if is_success else _t["RED"]
                details_row = (
                    [ft.Text("Details: " + activity["details"], size=9, color=_NAVY_MUTED)]
                    if activity["details"] else []
                )
                card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(activity["type"].upper(), size=11,
                                            font_family="Poppins-Bold", color=status_color),
                                    ft.Text(
                                        activity["timestamp"][-8:] if activity["timestamp"] else "",
                                        size=10, color=_NAVY_MUTED,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text("IP: " + (activity["ip"] or "N/A"), size=10, color=_NAVY_MUTED),
                            ft.Text("Location: " + activity["city"] + ", " + activity["country"], size=10, color=_NAVY_MUTED),
                            ft.Text("ISP: " + activity["isp"], size=10, color=_NAVY_MUTED),
                            *details_row,
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.all(10),
                    bgcolor=_CARD,
                    border=ft.border.only(
                        left=ft.BorderSide(3, status_color),
                        top=ft.BorderSide(1, _BORDER),
                        right=ft.BorderSide(1, _BORDER),
                        bottom=ft.BorderSide(1, _BORDER),
                    ),
                    border_radius=8,
                )
                activity_list.controls.append(card)

        page.update()

    def on_search_click(e):
        email = search_email.value.strip()
        if not email:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter an email"))
            page.snack_bar.open = True
            page.update()
            return
        load_user_activity(email)

    user_detail_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.PERSON_SEARCH_ROUNDED, size=16, color=_ACCENT),
                    ft.Text("User Details", size=14, font_family="Poppins-Bold", color=_NAVY),
                ],
                spacing=6,
            ),
            ft.Text("Search a user to view their activity stats and login history", size=11, color=_NAVY_MUTED),
            ft.Container(height=4),
            ft.Row(
                [search_email, _search_btn(on_search_click)],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            ft.Container(height=6),
            stats_display,
            ft.Container(height=4),
            ft.Row(
                [
                    ft.Icon(ft.Icons.HISTORY_ROUNDED, size=14, color=_NAVY_MUTED),
                    ft.Text("Activity History", size=13, font_family="Poppins-Bold", color=_NAVY),
                ],
                spacing=6,
            ),
            activity_list,
        ],
        spacing=8,
    )

    # === TAB 3: Failed Attempts ===
    failed_attempts_list = ft.Column(spacing=8)
    failed_search_email = _field(label="Enter user email for failed attempts...", width=300)

    def load_failed_attempts(email):
        failed_attempts_list.controls.clear()

        attempts = activity_monitor.get_failed_attempts(email, limit=50)

        if not attempts:
            failed_attempts_list.controls.append(
                ft.Column(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=36, color=_t["GREEN"]),
                        ft.Text("No failed attempts recorded", size=12, color=_NAVY_MUTED),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                )
            )
        else:
            for attempt in attempts:
                reason_badge = ft.Container(
                    content=ft.Text(attempt["reason"] or "Unknown", size=10, color=_t["RED"]),
                    bgcolor=_t["RED_BG"],
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    border_radius=12,
                )
                card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.LOCK_OUTLINE_ROUNDED,
                                                    size=13, color=_t["RED"]),
                                            ft.Text("Failed Login", size=11,
                                                    font_family="Poppins-Bold", color=_t["RED"]),
                                        ],
                                        spacing=4,
                                    ),
                                    ft.Text(
                                        attempt["timestamp"][-8:] if attempt["timestamp"] else "",
                                        size=10, color=_NAVY_MUTED,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text("Email: " + attempt["email"], size=10, color=_NAVY_MUTED),
                            ft.Text("IP: " + attempt["ip"], size=10, color=_NAVY_MUTED),
                            ft.Text("Location: " + attempt["location"], size=10, color=_NAVY_MUTED),
                            reason_badge,
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.all(10),
                    bgcolor=_CARD,
                    border=ft.border.only(
                        left=ft.BorderSide(3, _t["RED"]),
                        top=ft.BorderSide(1, _BORDER),
                        right=ft.BorderSide(1, _BORDER),
                        bottom=ft.BorderSide(1, _BORDER),
                    ),
                    border_radius=8,
                )
                failed_attempts_list.controls.append(card)

        page.update()

    def on_failed_search_click(e):
        email = failed_search_email.value.strip()
        if not email:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter an email"))
            page.snack_bar.open = True
            page.update()
            return
        load_failed_attempts(email)

    failed_attempts_view = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.LOCK_PERSON_ROUNDED, size=16, color=_t["RED"]),
                    ft.Text("Failed Attempts", size=14, font_family="Poppins-Bold", color=_NAVY),
                ],
                spacing=6,
            ),
            ft.Text("Search a user to view their failed login attempts", size=11, color=_NAVY_MUTED),
            ft.Container(height=4),
            ft.Row(
                [failed_search_email, _search_btn(on_failed_search_click)],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            ft.Container(height=6),
            failed_attempts_list,
        ],
        spacing=8,
    )

    # ── Build tab buttons (views must be defined before this) ──
    def _make_tab_btn(key, icon, label):
        is_active = key == "all_users"
        btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, size=14,
                            color=_ACCENT if is_active else _NAVY_MUTED),
                    ft.Text(label, size=13, font_family="Poppins-SemiBold",
                            color=_ACCENT if is_active else _NAVY_MUTED),
                ],
                spacing=5,
                tight=True,
            ),
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            border_radius=ft.border_radius.only(top_left=6, top_right=6),
            bgcolor=_BORDER_LIGHT if is_active else "transparent",
            border=ft.border.only(
                bottom=ft.BorderSide(2, _ACCENT if is_active else "transparent")
            ),
            on_click=lambda e, k=key: switch_tab(k),
            ink=True,
        )
        tab_buttons[key] = btn
        return btn

    tab_bar = ft.Container(
        content=ft.Row(
            [_make_tab_btn(k, ico, lbl) for k, ico, lbl in _tab_defs],
            spacing=4,
        ),
        border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
        padding=ft.padding.only(left=4, bottom=0),
    )

    main_view_container.content = all_users_view
    load_all_users_stats()

    content_area = ft.Container(
        content=ft.Column(
            [
                header,
                ft.Container(
                    content=ft.Column(
                        [
                            tab_bar,
                            ft.Container(height=14),
                            main_view_container,
                        ],
                        spacing=0,
                    ),
                    padding=ft.padding.symmetric(
                        horizontal=16 if is_mobile else 28, vertical=14
                    ),
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        bgcolor=_BG,
    )

    def on_resize(e):
        nonlocal is_mobile
        w = page.width or 0
        was_mobile = is_mobile
        is_mobile = w < _SIDEBAR_BREAKPOINT
        if was_mobile != is_mobile:
            sidebar_wrapper.visible = not is_mobile
            page.update()

    page.on_resized = on_resize

    if drawer:
        page.drawer = drawer

    page.controls.append(
        ft.Row(
            [sidebar_wrapper, content_area],
            spacing=0,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
    )
    page.update()
