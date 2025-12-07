import flet as ft

class NavigationDrawerComponent:
    def __init__(self, page: ft.Page, user_data, on_theme_toggle):
        self.page = page
        self.user_data = user_data
        self.on_theme_toggle = on_theme_toggle
        self.drawer = None
        self.is_admin = user_data.get("type") == "admin" if user_data else False
    
    def create_drawer(self, is_dark):
        
        theme_icon = ft.IconButton(
            icon=ft.Icons.LIGHT_MODE_OUTLINED if is_dark else ft.Icons.DARK_MODE_OUTLINED,
            icon_color=ft.Colors.WHITE,
            icon_size=24,
            on_click=self._toggle_theme,
        )
        
        
        if self.is_admin:
            menu_items = [
                self._create_header(theme_icon),
                ft.Divider(height=1, color=ft.Colors.WHITE, thickness=1),
                self._create_menu_item(ft.Icons.DASHBOARD_OUTLINED, "Dashboard", self._menu_admin_home_clicked),
                self._create_menu_item(ft.Icons.DESCRIPTION_OUTLINED, "Reports", self._menu_admin_reports_clicked),
                self._create_menu_item(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, "Account", self._menu_account_clicked),
                self._create_menu_item(ft.Icons.LOGOUT_OUTLINED, "Logout", self._menu_logout_clicked),
            ]
        else:
            menu_items = [
                self._create_header(theme_icon),
                ft.Divider(height=1, color=ft.Colors.WHITE, thickness=1),
                self._create_menu_item(ft.Icons.HOME_OUTLINED, "Home", self._menu_home_clicked),
                self._create_menu_item(ft.Icons.DESCRIPTION_OUTLINED, "Report", self._menu_reports_clicked),
                self._create_menu_item(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, "Account", self._menu_account_clicked),
                self._create_menu_item(ft.Icons.LOGOUT_OUTLINED, "Logout", self._menu_logout_clicked),
            ]
        
        self.drawer = ft.NavigationDrawer(
            controls=menu_items,
            bgcolor="#062C80",
        )
        return self.drawer
    
    def _create_header(self, theme_icon):
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text("Menu", size=20, font_family="Poppins-SemiBold", color=ft.Colors.WHITE),
                    theme_icon,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=20,
            bgcolor="#062C80",
        )
    
    def _create_menu_item(self, icon, text, on_click):
        
        return ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    [
                        ft.Icon(icon, color=ft.Colors.WHITE, size=20),
                        ft.Text(text, color=ft.Colors.WHITE, size=16, font_family="Poppins-SemiBold"),
                    ],
                    spacing=15,
                    alignment=ft.MainAxisAlignment.START,
                ),
                on_click=on_click,
                style=ft.ButtonStyle(
                    padding=15,
                    shape=ft.RoundedRectangleBorder(radius=0),
                    overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                ),
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=2),
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
        from .report_issue_page import report_issue_page
        report_issue_page(self.page, self.user_data)
    
    def _menu_admin_reports_clicked(self, e):
        
        self._close_drawer()
        from app.views.dashboard.admin.admin_all_reports import admin_all_reports
        admin_all_reports(self.page, self.user_data)
    
    def _menu_account_clicked(self, e):
        
        self._close_drawer()
        # Ensure add/floating action button is removed when viewing account
        self.page.floating_action_button = None
        self.page.update()
        from .account_page import account_page
        account_page(self.page, self.user_data)
    
    def _menu_logout_clicked(self, e):
        
        self._close_drawer()
        self.page.session.clear()
        self.page.controls.clear()
        self.page.floating_action_button = None
        from app.views.loginpage import loginpage
        loginpage(self.page)
    
    def open_drawer(self, e):
        
        if self.drawer:
            self.drawer.open = True
            self.page.update()