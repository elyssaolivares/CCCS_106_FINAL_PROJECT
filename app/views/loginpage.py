import flet as ft

def loginpage(page: ft.Page):
    page.controls.clear()
    page.floating_action_button = None 
    page.end_drawer = None 
    page.drawer = None 

    role_dropdown = ft.Dropdown(
        hint_text="Select Role",
        width=300,
        options=[
            ft.dropdown.Option("Admin"),
            ft.dropdown.Option("Student"),
            ft.dropdown.Option("Faculty")
        ],
        bgcolor=ft.Colors.WHITE,
        hover_color="#062C80",
        border_color=ft.Colors.BLUE_900,
        border_radius=10,
        content_padding=15,
    )

    email_field = ft.TextField(
        hint_text="Email",
        text_size=13,
        width=300,
        bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
        border_color="#062C80",
        border_radius=10,
        content_padding=15,
        visible=True
    )

    password_field = ft.TextField(
        hint_text="Password",
        text_size=13,
        password=True,
        can_reveal_password=True,
        width=300,
        bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
        border_color="#062C80",
        border_radius=10,
        content_padding=15,
        visible=True
    )

    login_button = ft.ElevatedButton(
        text="Login",
        width=300,
        height=50,
        bgcolor="#062C80",
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        visible=True,
    )

    cspc_button = ft.ElevatedButton(
        text="CSPC Email",
        width=300,
        height=50,
        bgcolor=ft.Colors.WHITE,
        color=ft.Colors.BLUE_900,
        icon=ft.Icons.EMAIL,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side=ft.BorderSide(2, ft.Colors.BLUE_900)
        ),
        visible=True,
    )

    login_form = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=70),
                ft.Text("LOGIN", size=35, font_family="Poppins-Bold",
                    color="#062C80",),
                ft.Container(width=120, height=8, bgcolor="#062C80", border_radius=5),
                ft.Container(height=60),
                role_dropdown,
                ft.Container(height=15),
                email_field,
                ft.Container(height=15),
                password_field,
                ft.Container(height=40),
                login_button,
                ft.Container(height=10),
                cspc_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        width=800,
        padding=40,
        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE),
        border_radius=20,
        blur=20,
    )

    main_stack = ft.Stack(
        [
            ft.Container(
                content=ft.Image(
                    src="cspc_logo.png",
                    width=450,
                    height=450,
                    fit=ft.ImageFit.CONTAIN,
                    opacity=0.5,
                ),
                alignment=ft.alignment.center,
                expand=True,
            ),
            ft.Container(
                content=login_form,
                alignment=ft.alignment.center,
                expand=True,
            ),
        ],
        expand=True,
    )

    page.add(main_stack)
    page.update()