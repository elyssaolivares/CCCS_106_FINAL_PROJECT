import flet as ft
import os
from app.services.google.google_auth import google_oauth_login
from app.services.auth.admin_account import validate_admin_credentials
from app.services.database.database import db
from app.services.audit.audit_logger import audit_logger
from app.services.activity.activity_monitor import activity_monitor
from app.views.dashboard.admin.admin_dashboard import admin_dashboard
from app.views.dashboard.user_dashboard import user_dashboard
from app.services.session import get_session_manager
from app.services.google.oauth_server import get_auth_url
# ── Color palette ──
_PRIMARY = "#0F2B5B"
_PRIMARY_LIGHT = "#1565C0"
_ACCENT = "#4FC3F7"
_BG = "#F5F7FA"
_CARD = "#FFFFFF"
_TEXT_MUTED = "#90A4AE"
_DIVIDER = "#E0E6ED"
_FIELD_BORDER = "#CFD8DC"
_FIELD_FOCUS = "#1565C0"

def loginpage(page: ft.Page):
    page.controls.clear()
    page.overlay.clear()
    page.floating_action_button = None
    page.end_drawer = None
    page.drawer = None
    page.on_resized = None

    # Resolve palette from theme (login always light unless user had dark pref from prior session)
    from app.theme import get_colors as _get_theme
    _t = _get_theme(page)
    _PRIMARY = _t["NAVY"]; _PRIMARY_LIGHT = _t["ACCENT"]
    _BG = _t["BG"]; _CARD = _t["WHITE"]
    _FIELD_BORDER = _t["FIELD_BORDER"]; _FIELD_FOCUS = _t["FIELD_FOCUS"]
    _TEXT_MUTED = _t["TEXT_MUTED"]; _DIVIDER = _t["DIVIDER"]
    is_dark = page.session.get("is_dark_theme") or False

    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = _BG
    page.update()

    # ── Snackbar helper ──
    def show_snackbar(message, bgcolor=ft.Colors.RED_400):
        display_message = str(message).strip() if message is not None else "Operation completed"
        if not display_message:
            display_message = "Operation completed"

        snackbar = ft.SnackBar(
            content=ft.Text(display_message, color=ft.Colors.WHITE, size=13, font_family="Poppins-Medium"),
            bgcolor=bgcolor,
        )
        if hasattr(page, "show_snack_bar"):
            page.show_snack_bar(snackbar)
            return

        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    # ── Form field width (responsive, updated in build_layout) ──
    _FIELD_W = 320

    # ── Form controls ──
    role_dropdown = ft.Dropdown(
        hint_text="Select your role",
        width=_FIELD_W,
        options=[
            ft.dropdown.Option("Admin"),
            ft.dropdown.Option("Student"),
            ft.dropdown.Option("Faculty"),
        ],
        bgcolor=_CARD,
        border_color=_FIELD_BORDER,
        focused_border_color=_FIELD_FOCUS,
        border_radius=10,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        text_size=14,
    )

    email_field = ft.TextField(
        hint_text="Email address",
        text_size=14,
        width=_FIELD_W,
        bgcolor=_CARD,
        border_color=_FIELD_BORDER,
        focused_border_color=_FIELD_FOCUS,
        border_radius=10,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
    )

    password_field = ft.TextField(
        hint_text="Password",
        text_size=14,
        password=True,
        can_reveal_password=True,
        width=_FIELD_W,
        bgcolor=_CARD,
        border_color=_FIELD_BORDER,
        focused_border_color=_FIELD_FOCUS,
        border_radius=10,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        prefix_icon=ft.Icons.LOCK_OUTLINED,
    )

    # ── Login logic ──
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

        if role.lower() in ["student", "faculty"]:
            show_snackbar("Account not existed")
            audit_logger.log_action(email, email, "login_attempt", status="failed", details="Account not existed")
            activity_monitor.log_login_attempt(email, email, success=False, details="Account not existed")
            return

        admin_account = validate_admin_credentials(email, password)
        if not admin_account:
            show_snackbar("Invalid admin credentials")
            audit_logger.log_action(email, email, "login_attempt", status="failed", details="Invalid credentials")
            activity_monitor.log_login_attempt(email, email, success=False, details="Invalid credentials")
            return

        user_firstname = admin_account["name"].split()[0]
        existing = db.get_user_by_email(admin_account["email"])
        preserved_name = existing.get("name") if existing and existing.get("name") else admin_account["name"]

        user_data = {
            "name": preserved_name,
            "email": admin_account["email"],
            "type": "admin",
        }
        if existing and existing.get("picture"):
            user_data["picture"] = existing["picture"]

        db.create_or_update_user(admin_account["email"], preserved_name, "admin")
        session_manager = get_session_manager()
        session_manager.create_session(admin_account["email"], preserved_name, "admin")

        audit_logger.log_action(admin_account["email"], preserved_name, "login", status="success", details="Admin login successful")
        activity_monitor.log_login_attempt(admin_account["email"], preserved_name, success=True, details="Admin login successful")
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
            # Redirect URI must exactly match one configured in Google Cloud OAuth client.
            redirect_uri = os.environ.get("REDIRECT_URI")
            if not redirect_uri:
                redirect_uri = "http://localhost:8550/api/oauth/redirect"

            auth_url, state = get_auth_url(redirect_uri)
            
            # Store state in session for verification
            page.session.set("oauth_state", state)
            page.session.set("oauth_role", role)
            
            # Open Google login in new window
            page.launch_url(auth_url)
            
        except Exception as ex:
            show_snackbar(str(ex))
            
    # ── Buttons ──
    login_button = ft.Container(
        content=ft.Text("Sign In", size=15, font_family="Poppins-SemiBold", color=ft.Colors.WHITE),
        width=_FIELD_W,
        height=48,
        bgcolor=_PRIMARY,
        border_radius=10,
        alignment=ft.alignment.center,
        on_click=login_clicked,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
    )

    cspc_button = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SCHOOL_OUTLINED, size=18, color=_PRIMARY),
                ft.Text("Continue with CSPC Email", size=14, font_family="Poppins-Medium", color=_PRIMARY),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        width=_FIELD_W,
        height=48,
        bgcolor=_CARD,
        border=ft.border.all(1.5, _DIVIDER),
        border_radius=10,
        alignment=ft.alignment.center,
        on_click=cspc_login_clicked,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
    )

    # ── Divider row ──
    divider_row = ft.Row(
        [
            ft.Container(expand=True, height=1, bgcolor=_DIVIDER),
            ft.Container(
                content=ft.Text("or", size=12, color=_TEXT_MUTED, font_family="Poppins-Regular"),
                padding=ft.padding.symmetric(horizontal=14),
            ),
            ft.Container(expand=True, height=1, bgcolor=_DIVIDER),
        ],
        width=_FIELD_W,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ── Login form column ──
    login_form_column = ft.Column(
        [
            ft.Text("Welcome back", size=28, font_family="Poppins-Bold", color=_PRIMARY),
            ft.Container(height=6),
            ft.Text(
                "Sign in to your account to continue",
                size=13,
                font_family="Poppins-Regular",
                color=_TEXT_MUTED,
            ),
            ft.Container(height=36),
            role_dropdown,
            ft.Container(height=14),
            email_field,
            ft.Container(height=14),
            password_field,
            ft.Container(height=28),
            login_button,
            ft.Container(height=20),
            divider_row,
            ft.Container(height=20),
            cspc_button,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
    )

    # ── Left branding panel builder ──
    def make_left_panel_content():
        return ft.Stack(
            [
                # Background image
                ft.Container(
                    expand=True,
                    bgcolor="#0A1628",
                    image=ft.DecorationImage(
                        src="/bg.jpg",
                        fit=ft.ImageFit.COVER,
                    ),
                ),
                # Dark overlay for dimming the bg image
                ft.Container(
                    expand=True,
                    bgcolor=ft.Colors.with_opacity(0.65, "#0A1628"),
                ),
                # Content
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Image(
                                src="/cspc_logo.png",
                                width=100,
                                height=100,
                                fit=ft.ImageFit.CONTAIN,
                            ),
                            ft.Container(height=24),
                            ft.Text(
                                "FIXIT",
                                size=50,
                                font_family="Poppins-Bold",
                                color=ft.Colors.WHITE,
                            ),
                            ft.Container(height=10),
                            ft.Container(
                                width=44,
                                height=3,
                                bgcolor=_ACCENT,
                                border_radius=3,
                            ),
                            ft.Container(height=16),
                            ft.Text(
                                "Faculty Issue eXchange",
                                size=10,
                                font_family="Poppins-Medium",
                                color= ft.Colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "& Information Tracker",
                                size=10,
                                font_family="Poppins-Medium",
                                color=ft.Colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=36),
                            ft.Text(
                                "Report, track, and resolve",
                                size=11,
                                font_family="Poppins-Light",
                                color=ft.Colors.with_opacity(0.45, ft.Colors.WHITE),
                                text_align=ft.TextAlign.CENTER,
                                italic=True,
                            ),
                            ft.Text(
                                "campus facility issues with ease.",
                                size=12,
                                font_family="Poppins-Light",
                                color=ft.Colors.with_opacity(0.45, ft.Colors.WHITE),
                                text_align=ft.TextAlign.CENTER,
                                italic=True,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=40),
                ),
            ],
        )

    # ── Main layout container ──
    main_container = ft.Container(expand=True)

    def build_layout():
        w = page.width or 800

        if w < 700:
            # ── Mobile ──
            login_form_column.horizontal_alignment = ft.CrossAxisAlignment.CENTER

            mobile_card = ft.Container(
                content=ft.Column(
                    [
                        # Compact branding header
                        ft.Container(
                            content=ft.Stack(
                                [
                                    ft.Container(
                                        expand=True,
                                        bgcolor="#0A1628",
                                        image=ft.DecorationImage(
                                            src="/bg.jpg",
                                            fit=ft.ImageFit.COVER,
                                        ),
                                    ),
                                    ft.Container(
                                        expand=True,
                                        bgcolor=ft.Colors.with_opacity(0.7, "#0A1628"),
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("F I X I T", size=22, font_family="Poppins-Bold", color=ft.Colors.WHITE),
                                                ft.Container(height=4),
                                                ft.Text(
                                                    "Faculty Issue eXchange & Information Tracker",
                                                    size=10,
                                                    font_family="Poppins-Medium",
                                                    color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                                                    text_align=ft.TextAlign.CENTER,
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=0,
                                        ),
                                        alignment=ft.alignment.center,
                                        expand=True,
                                    ),
                                ],
                            ),
                            height=120,
                            border_radius=ft.border_radius.only(top_left=16, top_right=16),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        ),
                        # Form area
                        ft.Container(
                            content=login_form_column,
                            padding=ft.padding.only(left=24, right=24, top=28, bottom=32),
                            bgcolor=_CARD,
                        ),
                    ],
                    spacing=0,
                ),
                width=min(w - 32, 420),
                border_radius=16,
                bgcolor=_CARD,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                shadow=ft.BoxShadow(
                    blur_radius=24,
                    spread_radius=0,
                    color=ft.Colors.with_opacity(0.08, "#000000"),
                    offset=ft.Offset(0, 4),
                ),
            )

            main_container.content = ft.Column(
                [mobile_card],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        else:
            # ── Desktop ──
            left_panel = ft.Container(
                content=make_left_panel_content(),
                expand=True,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )

            right_panel = ft.Container(
                content=ft.Container(
                    content=login_form_column,
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(horizontal=40),
                ),
                expand=True,
                bgcolor=_CARD,
                alignment=ft.alignment.center,
            )

            main_container.content = ft.Row(
                [left_panel, right_panel],
                spacing=0,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )

        main_container.alignment = ft.alignment.center

    def on_resize(e):
        build_layout()
        page.update()

    page.on_resized = on_resize
    page.bgcolor = _BG
    build_layout()
    page.add(main_container)
    page.update()