import flet as ft
from app.services.google.google_auth import google_oauth_login
from app.services.auth.admin_account import validate_admin_credentials
from app.services.database.database import db
from app.views.dashboard.admin.admin_dashboard import admin_dashboard
from app.views.dashboard.user_dashboard import user_dashboard

def loginpage(page: ft.Page):
    page.controls.clear()
    page.floating_action_button = None 
    page.end_drawer = None 
    page.drawer = None 

    def show_snackbar(message, bgcolor=ft.Colors.RED_400):
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=bgcolor,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

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



    def login_clicked(e):
        role = role_dropdown.value
        email = email_field.value.strip() if email_field.value else ""
        password = password_field.value if password_field.value else ""

        if not role:
            show_snackbar("Please select a role")
            return
        
        if not email:
            show_snackbar("Please enter your email")
            return
        
        if not password:
            show_snackbar("Please enter your password")
            return

        # Check if role is Student or Faculty
        if role.lower() in ["student", "faculty"]:
            show_snackbar("Account not existed")
            return

        
        admin_account = validate_admin_credentials(email, password)
        if not admin_account:
            show_snackbar("Invalid admin credentials")
            return

        
        user_firstname = admin_account["name"].split()[0]

        # Use DB name if user already exists to preserve custom name
        existing = db.get_user_by_email(admin_account["email"])
        preserved_name = existing.get("name") if existing and existing.get("name") else admin_account["name"]

        user_data = {
            "name": preserved_name,
            "email": admin_account["email"],
            "type": "admin"
        }

        # Create or update user in database using preserved name
        db.create_or_update_user(admin_account["email"], preserved_name, "admin")

        page.controls.clear()
        admin_dashboard(page, user_data)
        page.update()

        show_snackbar(f"Welcome {user_firstname}!", ft.Colors.GREEN_400)

    def cspc_login_clicked(e):
        role = role_dropdown.value
        
        if not role:
            show_snackbar("Please select a role")
            return
        
        try:
            user_info = google_oauth_login(page)
            email = user_info["email"]
            name = user_info["name"]
            
            
            user_firstname = name.split()[0] if name else "User"

            # Preserve DB name if user has an existing custom name
            existing = db.get_user_by_email(email)
            preserved_name = existing.get("name") if existing and existing.get("name") else name

            user_data = {
                "name": preserved_name,
                "email": email,
                "type": role.lower()
            }

            # Create/update user in database using preserved name
            db.create_or_update_user(email, preserved_name, role.lower())

            page.controls.clear()
            user_dashboard(page, user_data)
            page.update()

            show_snackbar(f"Welcome {user_firstname}!", ft.Colors.GREEN_400)
            
        except Exception as ex:
            show_snackbar(str(ex))

    login_button = ft.ElevatedButton(
        text="Login",
        width=300,
        height=50,
        bgcolor="#062C80",
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        visible=True,
        on_click=login_clicked
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
        on_click=cspc_login_clicked
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