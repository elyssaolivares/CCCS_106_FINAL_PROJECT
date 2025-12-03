import flet as ft

def homepage(page, login_func):

    def get_started_clicked(e):
        login_func(page)
   
    get_started_button = ft.Container(
        content=ft.ElevatedButton(
            text="Get Started",
            width=200,
            height=50,
            bgcolor="#062C80",
            color=ft.Colors.WHITE70,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=get_started_clicked,
        ),
        shadow=ft.BoxShadow(
            blur_radius=30,
            color=ft.Colors.with_opacity(0.3, color="#062C80"),
            offset=ft.Offset(0, 4),
        ),
    )

 
    home_content = ft.Container(
        content=ft.Column(
            [
                
                ft.Image(
                    src="cspc_logo.png",
                    width=130,
                    height=130,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Container(height=10),
                ft.Text(
                    "Welcome to",
                    size=12,
                    color=ft.Colors.BLACK,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Text(
                    "FIXIT",
                    size=65,
                    font_family="Poppins",
                    weight=ft.FontWeight.BOLD,
                    color="#062C80",
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Faculty Issue eXchange and\nInformation Tracker",
                    size=12,
                    color=ft.Colors.BLACK,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=20),
                get_started_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )
    
    page.controls.clear()   
    page.add(home_content)
    page.update()