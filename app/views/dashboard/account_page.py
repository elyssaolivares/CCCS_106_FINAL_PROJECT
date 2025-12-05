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
    picture = user_data.get("picture") if user_data else None
    
    
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
                    font_family="Poppins-SemiBold",
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
    
    # Profile picture or default icon
    profile_image = ft.Container(
        content=ft.Image(
            src=picture,
            width=100,
            height=100,
            fit=ft.ImageFit.COVER,
        ) if picture else ft.Icon(
            ft.Icons.ACCOUNT_CIRCLE,
            size=100,
            color="#062C80",
        ),
        width=120,
        height=120,
        border_radius=60,
        alignment=ft.alignment.center,
    )
    
    profile_card = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=20),
                profile_image,
                ft.Container(height=25),
                ft.Text(
                    full_name,
                    size=26,
                    font_family="Poppins-SemiBold",
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Text(
                        role,
                        size=14,
                        font_family="Poppins-Medium",
                        color=ft.Colors.WHITE70,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    bgcolor="#062C80" if is_dark else "#093AA5",
                    border_radius=20,
                ),
                ft.Container(height=20),
                ft.Divider(height=2, color=ft.Colors.GREY_600 if is_dark else ft.Colors.GREY_300),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.EMAIL, color=ft.Colors.GREY_500, size=20),
                        ft.Container(width=10),
                        ft.Text(
                            email,
                            size=14,
                            color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=30),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.all(30),
        width=500
        
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
