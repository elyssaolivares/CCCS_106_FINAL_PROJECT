import flet as ft
from .session_manager import SessionManager
from .navigation_drawer import NavigationDrawerComponent

def account_page(page: ft.Page, user_data=None):
    
    page.controls.clear()
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    full_name = user_data.get("name", "User") if user_data else "User"
    role = user_data.get("role", "Student").title() if user_data else "Student"
    email = user_data.get("email", "user@example.com") if user_data else "user@example.com"
    
    
    is_dark = page.session.get("is_dark_theme") or False
    
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        account_page(page, user_data)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "Account",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                ),
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                    on_click=nav_drawer.open_drawer,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )
    
    profile_card = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=30),
                
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.ACCOUNT_CIRCLE,
                        size=80,
                        color=ft.Colors.WHITE,
                    ),
                    alignment=ft.alignment.center,
                ),
                ft.Container(height=20),
                
                ft.Text(
                    full_name,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=5),
                
                ft.Container(
                    width=200,
                    height=2,
                    bgcolor=ft.Colors.WHITE,
                ),
                ft.Container(height=5),
                
                ft.Text(
                    role,
                    size=16,
                    weight=ft.FontWeight.W_500,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                
                ft.Text(
                    email,
                    size=14,
                    color=ft.Colors.WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=30),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        bgcolor="#062C80",
        border_radius=15,
        padding=20,
        width=900,
    )
    
    
    def update_layout(e=None):
        is_mobile = page.width < 768
        main_container.width = None if is_mobile else 1500
        page.update()
    
    main_container = ft.Container(
        content=ft.Column(
            [profile_card],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.symmetric(horizontal=25, vertical=20),
        width=None,
    )
    
    responsive_wrapper = ft.Column(
        [
            header,
            ft.Container(height=20),
            ft.Container(
                content=main_container,
                alignment=ft.alignment.top_center,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
    
    
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_900 if is_dark else ft.Colors.WHITE
    page.overlay_color = ft.Colors.TRANSPARENT
    page.end_drawer = drawer
    page.on_resized = update_layout
    page.add(responsive_wrapper)
    
    
    update_layout()
    page.update()
