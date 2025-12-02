import flet as ft

def homepage(page):

    
    def get_started_clicked(e):
        (page)
   
    get_started_button = ft.ElevatedButton(
        text="Get Started",
        width=300,
        height=50,
        bgcolor="#062C80",
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=get_started_clicked,
    )

 
    home_content = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=10),
                ft.Image(
                    src="cspc_logo.png",
                    width=200,
                    height=200,
                    fit=ft.ImageFit.CONTAIN,
                ),
                ft.Container(height=15),
                ft.Text(
                    "Welcome to",
                    size=16,
                    color=ft.Colors.BLACK,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=10),
                ft.Text(
                    "FIXIT",
                    size=40,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Faculty Issue eXchange and\nInformation Tracker",
                    size=14,
                    color=ft.Colors.BLACK,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=50),
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
