import flet as ft
from app.services.database.database import db
from app.services.ai.ai_services import predict_category
from .session_manager import SessionManager
from .navigation_drawer import NavigationDrawerComponent

def report_issue_page(page: ft.Page, user_data=None):

    page.controls.clear()
    page.floating_action_button = None
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    
    if not user_data:
        from app.views.loginpage import loginpage
        loginpage(page)
        return
    
    is_dark = SessionManager.get_theme_preference(page)
    
    def show_success_dialog(category):
        dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "Report successfully submitted!",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            text="Ok",
                            bgcolor="#062C80",
                            color=ft.Colors.WHITE,
                            width=100,
                            on_click=lambda e: close_dialog(dialog),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=5),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                ),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
            ),
            modal=True,
            bgcolor=ft.Colors.TRANSPARENT,
        )

        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def close_dialog(dialog):
        dialog.open = False
        page.update()
        from .userdashboard import user_dashboard
        user_dashboard(page, user_data)
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        report_issue_page(page, user_data)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "Add Report",
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
    
    issue_description_field = ft.TextField(
        multiline=True,
        min_lines=5,
        max_lines=5,
        hint_text="Describe the issue here...",
        border_color=ft.Colors.BLUE_900,
        border_width=2,
        border_radius=10,
        bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
        color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
        hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
    )
    
    location_field = ft.TextField(
        multiline=True,
        min_lines=3,
        max_lines=3,
        hint_text="Enter location...",
        border_color=ft.Colors.BLUE_900,
        border_width=2,
        border_radius=10,
        bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
        color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
        hint_style=ft.TextStyle(color=ft.Colors.GREY_400),
    )
    
    submit_button = ft.ElevatedButton(
        text="SUBMIT",
        bgcolor=ft.Colors.DEEP_ORANGE_400,
        color=ft.Colors.WHITE,
        width=100,
        height=40,
        on_click=lambda e: submit_clicked(e),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=5),
        ),
    )
    
    def submit_clicked(e):
        issue_desc = issue_description_field.value
        location = location_field.value
        
        if not issue_desc or not issue_desc.strip():
            snackbar = ft.SnackBar(
                content=ft.Text("Please describe the issue", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_400,
            )
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
            return
        
        if not location or not location.strip():
            snackbar = ft.SnackBar(
                content=ft.Text("Please provide a location", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_400,
            )
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
            return
        
        try:
            category = predict_category(issue_desc)
        except Exception as ex:
            print(f"Error predicting category: {ex}")
            category = "Uncategorized"
        
        try:
            user_email = user_data.get("email")
            user_name = user_data.get("name", "Unknown User")
            user_type = user_data.get("type", "user")
            
            if not user_email:
                snackbar = ft.SnackBar(
                    content=ft.Text("Error: User email not found", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.RED_400,
                )
                page.overlay.append(snackbar)
                snackbar.open = True
                page.update()
                return
            
            report_id = db.add_report(
                user_email=user_email,
                user_name=user_name,
                user_type=user_type,
                issue_description=issue_desc.strip(),
                location=location.strip(),
                category=category
            )
            
            print(f"Report saved with ID: {report_id}, Category: {category}")
            
            issue_description_field.value = ""
            location_field.value = ""
            
            show_success_dialog(category)
            
        except Exception as ex:
            print(f"Error saving report: {ex}")
            snackbar = ft.SnackBar(
                content=ft.Text(f"Error saving report: {str(ex)}", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_400,
            )
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
    
    form_content = ft.Column(
        [
            ft.Text(
                "Issue Description:",
                size=12,
                color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                weight=ft.FontWeight.W_500,
            ),
            ft.Container(height=5),
            issue_description_field,
            ft.Container(height=20),
            ft.Text(
                "Location:",
                size=12,
                color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                weight=ft.FontWeight.W_500,
            ),
            ft.Container(height=5),
            location_field,
            ft.Container(height=25),
            ft.Container(
                content=submit_button,
                alignment=ft.alignment.center_right,
            ),
        ],
        spacing=0,
    )
    
    main_container = ft.Container(
        content=form_content,
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
    page.end_drawer = drawer
    page.add(responsive_wrapper)
    page.update()