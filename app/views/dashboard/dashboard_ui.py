import flet as ft

# === Color Palette ===
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_LIGHT = "#1A3A6B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_ACCENT_HOVER = "#0D47A1"
_WHITE = "#FFFFFF"
_CARD = "#FFFFFF"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"

# Status palette — blue-toned to stay cohesive
_PENDING_TEXT = "#B45309"
_PENDING_BG = "#FEF3C7"
_ONGOING_TEXT = "#1565C0"
_ONGOING_BG = "#DBEAFE"
_RESOLVED_TEXT = "#15803D"
_RESOLVED_BG = "#DCFCE7"
_REJECTED_TEXT = "#DC2626"
_REJECTED_BG = "#FEE2E2"


class DashboardUI:

    @staticmethod
    def _build_avatar(picture, first_letter, size, border_radius, bg_color, letter_color):
        """Build a circular avatar: user picture if available, else letter fallback."""
        if picture:
            try:
                if picture.startswith("data:image"):
                    b64 = picture.split(",")[1] if "," in picture else picture
                    return ft.Container(
                        content=ft.Image(
                            src_base64=b64,
                            width=size, height=size,
                            fit=ft.ImageFit.COVER,
                            border_radius=border_radius,
                        ),
                        width=size, height=size,
                        border_radius=border_radius,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    )
                elif picture.startswith(("http://", "https://")):
                    return ft.Container(
                        content=ft.Image(
                            src=picture,
                            width=size, height=size,
                            fit=ft.ImageFit.COVER,
                            border_radius=border_radius,
                        ),
                        width=size, height=size,
                        border_radius=border_radius,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    )
            except Exception:
                pass
        # Fallback: letter avatar
        return ft.Container(
            content=ft.Text(first_letter, size=size * 0.42, font_family="Poppins-Bold", color=letter_color),
            width=size, height=size,
            border_radius=border_radius,
            bgcolor=bg_color,
            alignment=ft.alignment.center,
        )

    # ── Sidebar ──────────────────────────────────────
    @staticmethod
    def create_sidebar(first_name, user_data, on_nav, on_logout, active="home"):
        user_name = user_data.get("name", "User") if user_data else "User"
        user_email = user_data.get("email", "") if user_data else ""
        first_letter = user_name[0].upper() if user_name else "U"
        user_type = user_data.get("type", "user") if user_data else "user"
        picture = user_data.get("picture") if user_data else None

        def nav_item(icon, label, key, on_click):
            is_active = key == active
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
            nav_item(ft.Icons.GRID_VIEW_ROUNDED, "Dashboard", "home", on_nav("home")),
            nav_item(ft.Icons.CAMPAIGN_OUTLINED, "Reports", "reports", on_nav("reports")),
            nav_item(ft.Icons.PERSON_OUTLINE_ROUNDED, "Account", "account", on_nav("account")),
        ]

        return ft.Container(
            content=ft.Column(
                [
                    # Logo area
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.BUILD_CIRCLE_OUTLINED, size=20, color=_WHITE),
                                    width=34,
                                    height=34,
                                    border_radius=10,
                                    bgcolor=_ACCENT,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Text("FIXIT", size=18, font_family="Poppins-Bold", color=_NAVY),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(left=16, right=16, top=28, bottom=20),
                    ),
                    ft.Container(height=1, bgcolor=_BORDER, margin=ft.margin.symmetric(horizontal=12)),
                    ft.Container(height=12),
                    # Nav items
                    ft.Container(
                        content=ft.Column(nav_items, spacing=4),
                        padding=ft.padding.symmetric(horizontal=8),
                    ),
                    # Spacer
                    ft.Container(expand=True),
                    # Divider
                    ft.Container(height=1, bgcolor=_BORDER, margin=ft.margin.symmetric(horizontal=12)),
                    ft.Container(height=8),
                    # Logout
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
                    # User card
                    ft.Container(
                        content=ft.Row(
                            [
                                DashboardUI._build_avatar(picture, first_letter, 34, 10, _NAVY, _WHITE),
                                ft.Column(
                                    [
                                        ft.Text(user_name, size=12, font_family="Poppins-SemiBold", color=_NAVY),
                                        ft.Text(user_type.title(), size=10, font_family="Poppins-Light", color=_NAVY_MUTED),
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
            width=220,
            bgcolor=_WHITE,
            border=ft.border.only(right=ft.BorderSide(1, _BORDER)),
        )

    # ── Top Bar ──────────────────────────────────────
    @staticmethod
    def create_top_bar(first_name, user_type, on_report_click, on_menu_click=None, is_mobile=False):
        role_badge = " · Admin" if user_type == "admin" else ""

        menu_btn = ft.Container(
            content=ft.IconButton(
                ft.Icons.MENU_ROUNDED,
                icon_color=_NAVY,
                icon_size=20 if is_mobile else 22,
                on_click=on_menu_click,
            ),
            width=36 if is_mobile else 40,
            height=36 if is_mobile else 40,
            border_radius=10,
            bgcolor=_BORDER_LIGHT,
            alignment=ft.alignment.center,
            visible=on_menu_click is not None,
        )

        title_size = 16 if is_mobile else 20
        sub_size = 11 if is_mobile else 12
        h_pad = 14 if is_mobile else 28
        v_pad = 12 if is_mobile else 18

        # On mobile: no button here (FAB handles it); on desktop: full button
        if is_mobile:
            report_btn = ft.Container()  # hidden — FAB is shown instead
        else:
            report_btn = ft.ElevatedButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.ADD_ROUNDED, size=18, color=_WHITE),
                        ft.Text("New Report", size=13, font_family="Poppins-SemiBold", color=_WHITE),
                    ],
                    spacing=6,
                ),
                bgcolor=_ACCENT,
                on_click=on_report_click,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    padding=ft.padding.symmetric(horizontal=18, vertical=12),
                ),
            )

        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                f"Hi, {first_name}{role_badge}",
                                size=title_size,
                                font_family="Poppins-Bold",
                                color=_NAVY,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                "Here's your report overview",
                                size=sub_size,
                                font_family="Poppins-Light",
                                color=_NAVY_MUTED,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    report_btn,
                    menu_btn,
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10 if is_mobile else 16,
            ),
            padding=ft.padding.symmetric(horizontal=h_pad, vertical=v_pad),
            bgcolor=_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
        )

    # ── Stat Cards 2x2 (responsive) ──────────────────
    @staticmethod
    def create_statistics_grid(total, resolved, pending, ongoing):

        def stat_tile(label, value, icon, accent, bg_tint, trend_text=""):
            tile = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(icon, size=18, color=accent),
                                    width=36,
                                    height=36,
                                    border_radius=10,
                                    bgcolor=bg_tint,
                                    alignment=ft.alignment.center,
                                ),
                                ft.Container(expand=True),
                                ft.Text(
                                    trend_text, size=10,
                                    font_family="Poppins-Medium",
                                    color=accent,
                                ) if trend_text else ft.Container(),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Container(height=8),
                        ft.Text(str(value), size=26, font_family="Poppins-Bold", color=_NAVY),
                        ft.Text(label, size=11, font_family="Poppins-Medium", color=_NAVY_MUTED,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=0,
                ),
                padding=ft.padding.all(16),
                bgcolor=_CARD,
                border_radius=14,
                border=ft.border.all(1, _BORDER),
            )
            # ResponsiveRow col: 6 = half-width on sm+, 6 on xs (2-per-row always)
            tile.col = {"xs": 6, "sm": 6, "md": 6, "lg": 3}
            return tile

        tiles = [
            stat_tile("Total Reports", total, ft.Icons.DESCRIPTION_OUTLINED, _NAVY, _BORDER_LIGHT),
            stat_tile("Pending", pending, ft.Icons.SCHEDULE_OUTLINED, _PENDING_TEXT, _PENDING_BG),
            stat_tile("In Progress", ongoing, ft.Icons.AUTORENEW_ROUNDED, _ONGOING_TEXT, _ONGOING_BG),
            stat_tile("Resolved", resolved, ft.Icons.CHECK_CIRCLE_OUTLINE, _RESOLVED_TEXT, _RESOLVED_BG),
        ]

        return ft.ResponsiveRow(tiles, spacing=10, run_spacing=10)

    # ── Filter Tabs (scrollable on mobile) ────────────
    @staticmethod
    def create_filter_buttons(on_filter_changed):
        filter_button_refs = {}

        def make_filter(label, filter_key, active=False):
            text = ft.Text(
                label, size=11, weight=ft.FontWeight.W_600,
                color=_WHITE if active else _NAVY_MUTED,
                font_family="Poppins-Medium",
            )
            btn = ft.Container(
                content=text,
                bgcolor=_NAVY if active else ft.Colors.TRANSPARENT,
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                border_radius=8,
                alignment=ft.alignment.center,
                on_click=on_filter_changed(filter_key),
                border=ft.border.all(1, _NAVY if active else _BORDER),
            )
            filter_button_refs[filter_key] = {"btn": btn, "text": text}
            return btn

        btns = [
            make_filter("Pending", "Pending", active=True),
            make_filter("Ongoing", "In Progress"),
            make_filter("Resolved", "Resolved"),
            make_filter("Rejected", "Rejected"),
        ]

        return ft.Container(
            content=ft.Row(btns, spacing=6, scroll=ft.ScrollMode.AUTO, tight=True),
        ), filter_button_refs

    # ── Empty State ──────────────────────────────────
    @staticmethod
    def create_empty_state(first_name, is_dark, on_report_click):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.INBOX_OUTLINED, size=40, color=_NAVY_MUTED),
                        width=72,
                        height=72,
                        border_radius=36,
                        bgcolor=_BORDER_LIGHT,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(height=14),
                    ft.Text("No reports yet", size=16, font_family="Poppins-Bold", color=_NAVY),
                    ft.Container(height=4),
                    ft.Text(
                        "Tap the button above to submit your first report.",
                        size=12, font_family="Poppins-Light", color=_NAVY_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.padding.symmetric(vertical=40, horizontal=20),
            alignment=ft.alignment.center,
            expand=True,
        )

    # ── No Filtered Reports ──────────────────────────
    @staticmethod
    def create_no_reports_message():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=36, color=ft.Colors.with_opacity(0.25, _NAVY)),
                    ft.Container(height=8),
                    ft.Text("No reports in this category", size=13, font_family="Poppins-Medium", color=_NAVY_MUTED,
                            text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.padding.symmetric(vertical=40),
            alignment=ft.alignment.center,
        )

    # ── FAB (kept for mobile only) ───────────────────
    @staticmethod
    def create_fab(on_click):
        return ft.FloatingActionButton(
            content=ft.Icon(ft.Icons.ADD_ROUNDED, color=_WHITE, size=24),
            on_click=on_click,
            bgcolor=_ACCENT,
            shape=ft.RoundedRectangleBorder(radius=16),
        )

    # Legacy header kept for compatibility with other pages
    @staticmethod
    def create_header(first_name, user_type, is_dark, on_menu_click):
        return DashboardUI.create_top_bar(first_name, user_type, lambda e: None, on_menu_click, is_mobile=False)