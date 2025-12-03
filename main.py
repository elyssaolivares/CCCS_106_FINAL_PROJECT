import flet as ft
from app.views.homepage import homepage

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
    

ft.app(
    target=main,
    assets_dir="assets",
    view=ft.WEB_BROWSER
)