import os
import flet as ft
from app.views.homepage import homepage
from app.views.loginpage import loginpage
from app.services.session import get_session_manager

def main(page: ft.Page):    
    page.title = "FIXIT"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0 
    page.bgcolor = ft.Colors.WHITE
    page.assets_dir = "assets"
    
    # set Poppins as default font
    page.fonts = {
        "Poppins": "fonts/Poppins-Regular.ttf",
        "Poppins-Bold": "fonts/Poppins-Bold.ttf",
        "Poppins-SemiBold": "fonts/Poppins-SemiBold.ttf",
        "Poppins-Medium": "fonts/Poppins-Medium.ttf",
        "Poppins-Light": "fonts/Poppins-Light.ttf",
    }
    
    # apply Poppins to theme
    page.theme = ft.Theme(
        font_family="Poppins",
    )

    # Start session monitoring
    session_manager = get_session_manager()
    session_manager.start_monitoring()

    def go_to_login(e):
        page.clean()
        loginpage(page)

    homepage(page, go_to_login)

import secrets as _secrets
os.environ.setdefault("FLET_SECRET_KEY", _secrets.token_hex(16))

ft.app(
    target=main,
    assets_dir="assets",
    upload_dir="storage/temp",
    view=ft.WEB_BROWSER,
)