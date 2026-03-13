import flet as ft

# Module-level fallback (light) — overridden per-instance from theme
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_WHITE = "#FFFFFF"
_BG = "#F8FAFC"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_DANGER = "#DC2626"


class NavigationDrawerComponent:
    def __init__(self, page: ft.Page, user_data, on_theme_toggle):
        self.page = page
        self.user_data = user_data
        self.on_theme_toggle = on_theme_toggle
        self.drawer = None
        self.is_admin = user_data.get("type") == "admin" if user_data else False

    def create_drawer(self, is_dark):
        self.is_dark = is_dark
        # Resolve colors for this render
        from app.theme import DARK, LIGHT as _LIGHT
        _col = DARK if is_dark else _LIGHT
        self._NAVY = _col["NAVY"]; self._NAVY_MUTED = _col["NAVY_MUTED"]
        self._ACCENT = _col["ACCENT"]; self._WHITE = _col["WHITE"]
        self._BORDER = _col["BORDER"]; self._BORDER_LIGHT = _col["BORDER_LIGHT"]
        self._DANGER = "#F87171" if is_dark else "#DC2626"

        if self.is_admin:
            nav_section = [
                self._section_label("NAVIGATION"),
                self._create_menu_item(ft.Icons.GRID_VIEW_ROUNDED, "Dashboard", self._menu_admin_home_clicked),
                self._create_menu_item(ft.Icons.CAMPAIGN_OUTLINED, "Reports", self._menu_admin_reports_clicked),
                self._create_menu_item(ft.Icons.SECURITY_OUTLINED, "Audit Logs", self._menu_audit_logs_clicked),
                self._create_menu_item(ft.Icons.VISIBILITY_OUTLINED, "User Activity", self._menu_user_activity_clicked),
            ]
        else:
            nav_section = [
                self._section_label("NAVIGATION"),
                self._create_menu_item(ft.Icons.GRID_VIEW_ROUNDED, "Dashboard", self._menu_home_clicked),
                self._create_menu_item(ft.Icons.CAMPAIGN_OUTLINED, "Reports", self._menu_reports_clicked),
            ]

        menu_items = [
            self._create_header(),
            self._divider(),
            *nav_section,
            ft.Container(height=8),
            self._divider(),
            self._section_label("SETTINGS"),
            self._create_theme_toggle(is_dark),
            ft.Container(height=4),
            self._divider(),
            self._section_label("ACCOUNT"),
            self._create_menu_item(ft.Icons.PERSON_OUTLINE_ROUNDED, "My Account", self._menu_account_clicked),
            self._create_menu_item(ft.Icons.LOGOUT_ROUNDED, "Logout", self._menu_logout_clicked, danger=True),
        ]

        self.drawer = ft.NavigationDrawer(
            controls=menu_items,
            bgcolor=self._WHITE,
        )
        return self.drawer

    def _create_theme_toggle(self, is_dark):
        moon_icon = ft.Icons.DARK_MODE_ROUNDED
        sun_icon = ft.Icons.LIGHT_MODE_ROUNDED
        icon = sun_icon if is_dark else moon_icon
        label = "Switch to Light" if is_dark else "Switch to Dark"
        icon_color = self._ACCENT

        return ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color=icon_color, size=18),
                            width=34,
                            height=34,
                            border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.10, icon_color),
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(label, color=self._NAVY, size=14, font_family="Poppins-Medium", expand=True),
                        ft.Container(
                            content=ft.Text(
                                "ON" if is_dark else "OFF",
                                size=9, font_family="Poppins-SemiBold",
                                color=self._ACCENT if is_dark else self._NAVY_MUTED,
                            ),
                            padding=ft.padding.symmetric(horizontal=6, vertical=3),
                            border_radius=6,
                            bgcolor=ft.Colors.with_opacity(0.12, self._ACCENT) if is_dark else self._BORDER_LIGHT,
                        ),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                on_click=self._toggle_theme,
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=10, vertical=10),
                    shape=ft.RoundedRectangleBorder(radius=12),
                    overlay_color=ft.Colors.with_opacity(0.06, self._ACCENT),
                ),
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=1),
        )

    def _section_label(self, text):
        return ft.Container(
            content=ft.Text(
                text,
                size=10,
                font_family="Poppins-SemiBold",
                color=ft.Colors.with_opacity(0.40, self._NAVY),
            ),
            padding=ft.padding.only(left=24, right=24, top=16, bottom=6),
        )

    def _divider(self):
        return ft.Container(
            content=ft.Divider(height=1, color=self._BORDER, thickness=1),
            padding=ft.padding.symmetric(horizontal=16),
        )

    def _create_header(self):
        user_name = self.user_data.get("name", "User") if self.user_data else "User"
        user_email = self.user_data.get("email", "") if self.user_data else ""
        first_letter = user_name[0].upper() if user_name else "U"
        user_type = self.user_data.get("type", "user") if self.user_data else "user"
        picture = self.user_data.get("picture") if self.user_data else None

        from .dashboard_ui import DashboardUI
        avatar = DashboardUI._build_avatar(picture, first_letter, 46, 14, self._ACCENT, "#FFFFFF")

        return ft.Container(
            content=ft.Column(
                [
                    # App brand
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.BUILD_CIRCLE_OUTLINED, size=18, color="#FFFFFF"),
                                width=30,
                                height=30,
                                border_radius=8,
                                bgcolor=self._ACCENT,
                                alignment=ft.alignment.center,
                            ),
                            ft.Text("FIXIT", size=16, font_family="Poppins-Bold", color=self._NAVY),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=20),
                    # User info card
                    ft.Container(
                        content=ft.Row(
                            [
                                avatar,
                                ft.Column(
                                    [
                                        ft.Text(
                                            user_name,
                                            size=14,
                                            font_family="Poppins-SemiBold",
                                            color=self._NAVY,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                        ft.Text(
                                            user_email,
                                            size=10,
                                            font_family="Poppins-Light",
                                            color=self._NAVY_MUTED,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    spacing=1,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(12),
                        border_radius=12,
                        bgcolor=self._BORDER_LIGHT,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.only(left=20, right=20, top=28, bottom=20),
        )

    def _create_menu_item(self, icon, text, on_click, danger=False):
        if danger:
            text_color = self._DANGER
            icon_color = self._DANGER
            overlay = ft.Colors.with_opacity(0.06, self._DANGER)
        else:
            text_color = self._NAVY
            icon_color = self._NAVY_MUTED
            overlay = ft.Colors.with_opacity(0.06, self._ACCENT)

        return ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(icon, color=icon_color, size=18),
                            width=34,
                            height=34,
                            border_radius=10,
                            bgcolor=ft.Colors.with_opacity(0.06, icon_color),
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(text, color=text_color, size=14, font_family="Poppins-Medium"),
                    ],
                    spacing=12,
                    alignment=ft.MainAxisAlignment.START,
                ),
                on_click=on_click,
                style=ft.ButtonStyle(
                    padding=ft.padding.symmetric(horizontal=10, vertical=10),
                    shape=ft.RoundedRectangleBorder(radius=12),
                    overlay_color=overlay,
                ),
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=1),
        )

    def _close_drawer(self):
        if self.drawer:
            self.drawer.open = False
            self.page.update()

    def _toggle_theme(self, e):
        self._close_drawer()
        self.on_theme_toggle(e)
    
    def _menu_home_clicked(self, e):
        
        self._close_drawer()
        from .user_dashboard import user_dashboard
        user_dashboard(self.page, self.user_data)
    
    def _menu_admin_home_clicked(self, e):
        
        self._close_drawer()
        from app.views.dashboard.admin.admin_dashboard import admin_dashboard
        admin_dashboard(self.page, self.user_data)
    
    def _menu_reports_clicked(self, e):
        
        self._close_drawer()
        from .user_dashboard import user_dashboard
        user_dashboard(self.page, self.user_data, active_section="reports")
    
    def _menu_admin_reports_clicked(self, e):
        
        self._close_drawer()
        from app.views.dashboard.admin.admin_all_reports import admin_all_reports
        admin_all_reports(self.page, self.user_data)
    
    def _menu_audit_logs_clicked(self, e):
        
        self._close_drawer()
        from app.views.dashboard.admin.audit_logs_viewer import audit_logs_page
        audit_logs_page(self.page, self.user_data)
    
    def _menu_user_activity_clicked(self, e):
        
        self._close_drawer()
        from app.views.dashboard.admin.user_activity_monitoring import user_activity_monitoring_page
        user_activity_monitoring_page(self.page, self.user_data)
    
    def _menu_account_clicked(self, e):
        
        self._close_drawer()
        self.page.floating_action_button = None
        self.page.update()
        from .account_page import account_page
        account_page(self.page, self.user_data)
    
    def _menu_logout_clicked(self, e):
        
        self._close_drawer()
        self.page.session.clear()
        self.page.controls.clear()
        self.page.overlay.clear()
        self.page.floating_action_button = None
        self.page.end_drawer = None
        self.page.drawer = None
        self.page.on_resized = None
        from app.views.loginpage import loginpage
        loginpage(self.page)
    
    def open_drawer(self, e):
        
        if self.drawer:
            self.drawer.open = True
            self.page.update()