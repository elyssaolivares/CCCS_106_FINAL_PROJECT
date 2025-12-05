import flet as ft

def account_page(page: ft.Page, user_data=None):
    
    page.controls.clear()
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    full_name = user_data.get("name", "User") if user_data else "User"
    role = user_data.get("role", "Student").title() if user_data else "Student"
    email = user_data.get("email", "user@example.com") if user_data else "user@example.com"
    
    
    is_dark = page.session.get("is_dark_theme") or False
    
    
    def toggle_dark_theme(e):
        new_dark = not page.session.get("is_dark_theme", False)
        page.session.set("is_dark_theme", new_dark)
        page.theme_mode = ft.ThemeMode.DARK if new_dark else ft.ThemeMode.LIGHT
        page.bgcolor = ft.Colors.GREY_900 if new_dark else ft.Colors.WHITE
        
        header_text.color = ft.Colors.WHITE if new_dark else ft.Colors.BLACK
        theme_icon.icon = ft.Icons.LIGHT_MODE_OUTLINED if new_dark else ft.Icons.DARK_MODE_OUTLINED
        page.update()
    
    
    theme_icon = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE_OUTLINED if is_dark else ft.Icons.DARK_MODE_OUTLINED,
        icon_color=ft.Colors.WHITE,
        icon_size=24,
        on_click=toggle_dark_theme,
    )
    
    
    header_text = ft.Text(
        "Account",
        size=18,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
    )
    
    header = ft.Container(
        content=ft.Row(
            [
                header_text,
                theme_icon,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
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
    page.on_resized = update_layout
    page.add(responsive_wrapper)
    
    
    update_layout()
    page.update()
