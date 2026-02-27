import flet as ft
import os
import base64
from .session_manager import SessionManager
from .navigation_drawer import NavigationDrawerComponent
from .dashboard_ui import DashboardUI
from app.services.database.database import db

# ── Palette (matching dashboard) ──
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_LIGHT = "#1A3A6B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_ACCENT_HOVER = "#0D47A1"
_WHITE = "#FFFFFF"
_CARD = "#FFFFFF"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_GREEN = "#15803D"
_GREEN_BG = "#DCFCE7"
_RED = "#DC2626"
_RED_BG = "#FEE2E2"

_SIDEBAR_BREAKPOINT = 768


def account_page(page: ft.Page, user_data=None):
    page.controls.clear()
    page.overlay.clear()
    page.floating_action_button = None
    page.end_drawer = None
    page.drawer = None

    if not user_data:
        user_data = page.session.get("user_data")

    # Load latest from DB
    email = user_data.get("email") if user_data else None
    if email:
        db_user = db.get_user_by_email(email)
        if db_user:
            user_data["name"] = db_user.get("name", user_data.get("name", "User"))
            user_data["picture"] = db_user.get("picture", user_data.get("picture"))

    full_name = user_data.get("name", "User") if user_data else "User"
    first_name = full_name.split()[0] if full_name else "User"
    raw_role = None
    if user_data:
        raw_role = user_data.get("role") or user_data.get("type")
    role = str(raw_role).title() if raw_role else "Student"
    email = user_data.get("email", "user@example.com") if user_data else "user@example.com"
    picture = user_data.get("picture") if user_data else None
    first_letter = full_name[0].upper() if full_name else "U"
    is_admin = role.lower() == "admin"
    user_type = user_data.get("type", "user") if user_data else "user"

    is_dark = page.session.get("is_dark_theme") or False

    edit_mode = {"active": False}
    current_picture = {"path": picture}

    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        fresh = db.get_user_by_email(email)
        if fresh:
            user_data.update(fresh)
        account_page(page, user_data)

    # ── Navigation ──
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)

    def go_back(e):
        from .user_dashboard import user_dashboard
        if is_admin:
            from app.views.dashboard.admin.admin_dashboard import admin_dashboard
            admin_dashboard(page, user_data)
        else:
            user_dashboard(page, user_data)

    # ── Profile image logic ──
    profile_image_content = ft.Container()

    def update_profile_image():
        img_size = 100
        if current_picture["path"]:
            if current_picture["path"].startswith("data:image"):
                b64 = current_picture["path"].split(",")[1] if "," in current_picture["path"] else current_picture["path"]
                profile_image_content.content = ft.Image(
                    src_base64=b64, width=img_size, height=img_size,
                    fit=ft.ImageFit.COVER, border_radius=img_size // 2,
                )
            elif current_picture["path"].startswith(("http://", "https://")):
                profile_image_content.content = ft.Image(
                    src=current_picture["path"], width=img_size, height=img_size,
                    fit=ft.ImageFit.COVER, border_radius=img_size // 2,
                )
            else:
                try:
                    if os.path.exists(current_picture["path"]):
                        with open(current_picture["path"], 'rb') as f:
                            image_data = f.read()
                            base64_image = base64.b64encode(image_data).decode('utf-8')
                            ext = current_picture["path"].lower().split('.')[-1]
                            mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                            current_picture["path"] = f"data:{mime_type};base64,{base64_image}"
                            profile_image_content.content = ft.Image(
                                src_base64=base64_image, width=img_size, height=img_size,
                                fit=ft.ImageFit.COVER, border_radius=img_size // 2,
                            )
                    else:
                        profile_image_content.content = ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=img_size, color=_NAVY_MUTED)
                except Exception:
                    profile_image_content.content = ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=img_size, color=_NAVY_MUTED)
        else:
            profile_image_content.content = ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=img_size, color=_NAVY_MUTED)
        try:
            profile_image_content.update()
        except Exception:
            pass

    # ── File picker (works on desktop AND web/browser) ──
    _upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "storage", "temp")

    def _read_uploaded_file(upload_name: str):
        """Read the uploaded file from the server-side upload directory."""
        upload_path = os.path.normpath(os.path.join(_upload_dir, upload_name))
        if os.path.exists(upload_path):
            with open(upload_path, "rb") as f:
                return f.read()
        return None

    def _process_image_data(image_data: bytes, filename: str):
        """Convert raw bytes to a data-URI and apply to profile picture."""
        base64_image = base64.b64encode(image_data).decode("utf-8")
        ext = filename.lower().rsplit(".", 1)[-1]
        mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
        current_picture["path"] = f"data:{mime_type};base64,{base64_image}"
        update_profile_image()
        toast("Picture selected — save to apply.")

    def handle_upload_progress(e: ft.FilePickerUploadEvent):
        """Called when a web upload finishes (or errors)."""
        if e.progress == 1.0:
            # Upload complete — read from server-side storage
            image_data = _read_uploaded_file(e.file_name)
            if image_data:
                _process_image_data(image_data, e.file_name)
            else:
                toast("Unable to read uploaded image.", is_error=True)
        elif e.error:
            toast("Upload failed. Please try again.", is_error=True)

    def handle_file_picker_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return
        file = e.files[0]
        valid_types = ['.jpg', '.jpeg', '.png', '.gif']
        if not any(file.name.lower().endswith(ext) for ext in valid_types):
            toast("Invalid file type. Use JPG, PNG, or GIF.", is_error=True)
            return
        if file.size and file.size > 5 * 1024 * 1024:
            toast("File too large. Max 5 MB.", is_error=True)
            return

        # Desktop path available — read directly
        if hasattr(file, "path") and file.path:
            try:
                with open(file.path, "rb") as f:
                    image_data = f.read()
                _process_image_data(image_data, file.name)
                return
            except Exception:
                pass  # fall through to web upload

        # Web / browser — use Flet's upload mechanism
        try:
            upload_url = page.get_upload_url(file.name, 60)
            file_picker.upload([
                ft.FilePickerUploadFile(file.name, upload_url=upload_url),
            ])
        except Exception as ex:
            toast(f"Unable to upload image: {ex}", is_error=True)

    file_picker = ft.FilePicker(
        on_result=handle_file_picker_result,
        on_upload=handle_upload_progress,
    )
    page.overlay.append(file_picker)

    # ── Toast helper ──
    def toast(msg, is_error=False):
        snackbar = ft.SnackBar(
            content=ft.Text(msg, color=_WHITE, size=12, font_family="Poppins-Medium"),
            bgcolor=_RED if is_error else _GREEN,
            duration=3000,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    # ── Form fields ──
    name_field = ft.TextField(
        value=full_name, label="Full Name",
        border_color=_BORDER, focused_border_color=_ACCENT,
        border_radius=10, text_size=13, bgcolor=_WHITE, color=_NAVY,
        prefix_icon=ft.Icons.PERSON_OUTLINE_ROUNDED,
    )

    email_field = ft.TextField(
        value=email, label="Email", read_only=True,
        border_color=_BORDER, focused_border_color=_ACCENT,
        border_radius=10, text_size=13, bgcolor=_BORDER_LIGHT, color=_NAVY_MUTED,
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
    )

    current_password_field = ft.TextField(
        label="Current Password", password=True, can_reveal_password=True,
        border_color=_BORDER, focused_border_color=_ACCENT,
        border_radius=10, text_size=13, bgcolor=_WHITE, color=_NAVY,
        prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
    )

    new_password_field = ft.TextField(
        label="New Password", password=True, can_reveal_password=True,
        border_color=_BORDER, focused_border_color=_ACCENT,
        border_radius=10, text_size=13, bgcolor=_WHITE, color=_NAVY,
        prefix_icon=ft.Icons.LOCK_RESET_ROUNDED,
    )

    confirm_password_field = ft.TextField(
        label="Confirm New Password", password=True, can_reveal_password=True,
        border_color=_BORDER, focused_border_color=_ACCENT,
        border_radius=10, text_size=13, bgcolor=_WHITE, color=_NAVY,
        prefix_icon=ft.Icons.LOCK_OUTLINE_ROUNDED,
    )

    status_text = ft.Text("", size=12, color=_GREEN, font_family="Poppins-Medium")
    error_text = ft.Text("", size=12, color=_RED, font_family="Poppins-Medium")

    # ── .env password helper ──
    def update_env_password(new_password):
        try:
            env_path = ".env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('ADMIN_PASSWORD='):
                    lines[i] = f'ADMIN_PASSWORD={new_password}\n'
                    updated = True
                    break
            if not updated:
                lines.append(f'ADMIN_PASSWORD={new_password}\n')
            with open(env_path, 'w') as f:
                f.writelines(lines)
            return True
        except Exception:
            return False

    # ── Save profile ──
    def save_profile(e):
        error_text.value = ""
        status_text.value = ""

        if not name_field.value or len(name_field.value.strip()) < 2:
            error_text.value = "Name must be at least 2 characters"
            page.update()
            return

        if is_admin and (current_password_field.value or new_password_field.value or confirm_password_field.value):
            current_admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            if not current_password_field.value:
                error_text.value = "Current password is required"
                page.update()
                return
            if current_password_field.value != current_admin_password:
                error_text.value = "Current password is incorrect"
                page.update()
                return
            if len(new_password_field.value) < 6:
                error_text.value = "New password must be at least 6 characters"
                page.update()
                return
            if new_password_field.value != confirm_password_field.value:
                error_text.value = "New passwords do not match"
                page.update()
                return
            if update_env_password(new_password_field.value):
                status_text.value = "Password changed successfully!"
            else:
                error_text.value = "Failed to update password"
                page.update()
                return

        new_name = name_field.value.strip()
        new_picture = current_picture["path"] if current_picture["path"] != user_data.get("picture") else None

        try:
            db.create_or_update_user(email, new_name, role.lower(), new_picture)
        except Exception as db_error:
            error_text.value = f"Save failed: {str(db_error)}"
            page.update()
            return

        user_data["name"] = new_name
        if new_picture:
            user_data["picture"] = new_picture
        page.session.set("user_data", user_data)

        if not status_text.value:
            status_text.value = "Profile updated!"

        current_password_field.value = ""
        new_password_field.value = ""
        confirm_password_field.value = ""
        page.update()

        import time
        time.sleep(1)
        account_page(page, user_data)

    # ── Toggle edit ──
    def toggle_edit_mode(e):
        edit_mode["active"] = not edit_mode["active"]
        edit_section.visible = edit_mode["active"]
        info_rows_container.visible = not edit_mode["active"]
        if is_admin:
            password_section.visible = edit_mode["active"]
        edit_button.text = "Cancel" if edit_mode["active"] else "Edit Profile"
        edit_button.icon = ft.Icons.CLOSE_ROUNDED if edit_mode["active"] else ft.Icons.EDIT_OUTLINED
        edit_button.bgcolor = _NAVY_MUTED if edit_mode["active"] else _ACCENT
        save_button.visible = edit_mode["active"]
        status_text.value = ""
        error_text.value = ""
        if not edit_mode["active"]:
            current_picture["path"] = user_data.get("picture")
            update_profile_image()
        page.update()

    # ═══════════════════════════════════════════
    #   BUILD UI
    # ═══════════════════════════════════════════

    # ── Header ──
    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)

    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

    header = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_ROUNDED,
                            icon_color=_NAVY, icon_size=20,
                            on_click=go_back,
                        ),
                        ft.Text("Account", size=18 if is_mobile else 20,
                                font_family="Poppins-Bold", color=_NAVY),
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.IconButton(
                        ft.Icons.MENU_ROUNDED, icon_color=_NAVY, icon_size=20,
                        on_click=on_menu_click,
                    ),
                    width=36, height=36, border_radius=10,
                    bgcolor=_BORDER_LIGHT, alignment=ft.alignment.center,
                    visible=is_mobile,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=16 if is_mobile else 28, vertical=14),
        bgcolor=_WHITE,
        border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
    )

    # ── Profile hero card ──
    upload_btn = ft.Container(
        content=ft.IconButton(
            ft.Icons.CAMERA_ALT_ROUNDED, icon_color=_WHITE, icon_size=16,
            bgcolor=_ACCENT,
            on_click=lambda e: file_picker.pick_files(
                allowed_extensions=["jpg", "jpeg", "png", "gif"],
                dialog_title="Select Profile Picture",
            ),
            style=ft.ButtonStyle(padding=ft.padding.all(6)),
        ),
        right=0, bottom=0,
    )

    profile_picture_stack = ft.Stack(
        [
            ft.Container(
                content=profile_image_content,
                width=100, height=100, border_radius=50,
                alignment=ft.alignment.center,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                border=ft.border.all(3, _BORDER_LIGHT),
            ),
            upload_btn,
        ],
        width=100, height=100,
    )

    role_pill = ft.Container(
        content=ft.Text(role, size=10, font_family="Poppins-SemiBold", color=_ACCENT),
        padding=ft.padding.symmetric(horizontal=12, vertical=3),
        border_radius=6,
        bgcolor=ft.Colors.with_opacity(0.08, _ACCENT),
    )

    def _info_row(icon, label, value):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=16, color=_ACCENT),
                        width=32, height=32, border_radius=8,
                        bgcolor=ft.Colors.with_opacity(0.08, _ACCENT),
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(label, size=10, font_family="Poppins-Medium", color=_NAVY_MUTED),
                            ft.Text(value, size=13, font_family="Poppins-SemiBold", color=_NAVY,
                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=0, expand=True,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=10,
            bgcolor=_BORDER_LIGHT,
        )

    info_rows_container = ft.Column(
        [
            _info_row(ft.Icons.EMAIL_OUTLINED, "Email", email),
            _info_row(ft.Icons.BADGE_OUTLINED, "Role", role),
        ],
        spacing=8,
        visible=True,
    )

    profile_hero = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=6),
                profile_picture_stack,
                ft.Container(height=12),
                ft.Text(full_name, size=20, font_family="Poppins-Bold", color=_NAVY,
                        text_align=ft.TextAlign.CENTER, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Container(height=4),
                role_pill,
                ft.Container(height=16),
                info_rows_container,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.all(20),
        bgcolor=_CARD,
        border_radius=16,
        border=ft.border.all(1, _BORDER),
    )

    # ── Edit section ──
    edit_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Profile Information", size=14, font_family="Poppins-SemiBold", color=_NAVY),
                ft.Container(height=12),
                name_field,
                ft.Container(height=10),
                email_field,
            ],
            spacing=0,
        ),
        visible=False,
    )

    # ── Password section (admin only) ──
    password_section = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=16),
                ft.Container(height=1, bgcolor=_BORDER),
                ft.Container(height=16),
                ft.Text("Change Password", size=14, font_family="Poppins-SemiBold", color=_NAVY),
                ft.Container(height=12),
                current_password_field,
                ft.Container(height=10),
                new_password_field,
                ft.Container(height=10),
                confirm_password_field,
            ],
            spacing=0,
        ),
        visible=False,
    )

    # ── Action buttons ──
    edit_button = ft.ElevatedButton(
        "Edit Profile", icon=ft.Icons.EDIT_OUTLINED,
        on_click=toggle_edit_mode, bgcolor=_ACCENT, color=_WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        ),
    )

    save_button = ft.ElevatedButton(
        "Save Changes", icon=ft.Icons.CHECK_ROUNDED,
        on_click=save_profile, bgcolor=_GREEN, color=_WHITE,
        visible=False,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        ),
    )

    # ── Settings card (edit + password) ──
    settings_card = ft.Container(
        content=ft.Column(
            [
                edit_section,
                password_section if is_admin else ft.Container(),
                status_text,
                error_text,
                ft.Container(height=12),
                ft.Row(
                    [edit_button, save_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    wrap=True,
                ),
            ],
            spacing=0,
        ),
        padding=ft.padding.all(20),
        bgcolor=_CARD,
        border_radius=16,
        border=ft.border.all(1, _BORDER),
    )

    # ── Sidebar (desktop) ──
    def nav_handler(key):
        def handler(e):
            if key == "home":
                go_back(e)
            elif key == "reports":
                if is_admin:
                    from app.views.dashboard.admin.admin_all_reports import admin_all_reports
                    admin_all_reports(page, user_data)
                else:
                    from .report_issue_page import report_issue_page
                    report_issue_page(page, user_data)
            elif key == "audit":
                from app.views.dashboard.admin.audit_logs_viewer import audit_logs_page
                audit_logs_page(page, user_data)
            elif key == "activity":
                from app.views.dashboard.admin.user_activity_monitoring import user_activity_monitoring_page
                user_activity_monitoring_page(page, user_data)
            elif key == "account":
                account_page(page, user_data)
        return handler

    def on_logout(e):
        page.session.clear()
        page.controls.clear()
        page.overlay.clear()
        page.floating_action_button = None
        page.end_drawer = None
        page.drawer = None
        page.on_resized = None
        from app.views.loginpage import loginpage
        loginpage(page)

    if is_admin:
        def _admin_nav_item(icon, label, key, on_click):
            is_active = key == "account"
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(icon, size=18,
                                color=_ACCENT if is_active else _NAVY_MUTED),
                        ft.Text(label, size=13, font_family="Poppins-Medium",
                                color=_NAVY if is_active else _NAVY_MUTED),
                    ],
                    spacing=12,
                ),
                padding=ft.padding.symmetric(horizontal=14, vertical=11),
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.08, _ACCENT) if is_active else ft.Colors.TRANSPARENT,
                on_click=on_click,
                ink=True,
            )

        admin_nav_items = [
            _admin_nav_item(ft.Icons.GRID_VIEW_ROUNDED, "Dashboard", "home", nav_handler("home")),
            _admin_nav_item(ft.Icons.CAMPAIGN_OUTLINED, "Reports", "reports", nav_handler("reports")),
            _admin_nav_item(ft.Icons.SECURITY_OUTLINED, "Audit Logs", "audit", nav_handler("audit")),
            _admin_nav_item(ft.Icons.VISIBILITY_OUTLINED, "User Activity", "activity", nav_handler("activity")),
            _admin_nav_item(ft.Icons.PERSON_OUTLINE_ROUNDED, "Account", "account", nav_handler("account")),
        ]

        admin_picture = user_data.get("picture") if user_data else None
        admin_first_letter = full_name[0].upper() if full_name else "A"

        sidebar = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED, size=20, color=_WHITE),
                                    width=34, height=34, border_radius=10,
                                    bgcolor=_ACCENT, alignment=ft.alignment.center,
                                ),
                                ft.Text("FIXIT Admin", size=16, font_family="Poppins-Bold", color=_NAVY),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.only(left=16, right=16, top=28, bottom=20),
                    ),
                    ft.Container(height=1, bgcolor=_BORDER, margin=ft.margin.symmetric(horizontal=12)),
                    ft.Container(height=12),
                    ft.Container(
                        content=ft.Column(admin_nav_items, spacing=4),
                        padding=ft.padding.symmetric(horizontal=8),
                    ),
                    ft.Container(expand=True),
                    ft.Container(height=1, bgcolor=_BORDER, margin=ft.margin.symmetric(horizontal=12)),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=18, color=_NAVY_MUTED),
                                ft.Text("Logout", size=13, font_family="Poppins-Medium", color=_NAVY_MUTED),
                            ],
                            spacing=12,
                        ),
                        padding=ft.padding.symmetric(horizontal=14, vertical=11),
                        border_radius=10,
                        on_click=on_logout,
                        ink=True,
                        margin=ft.margin.symmetric(horizontal=8),
                    ),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row(
                            [
                                DashboardUI._build_avatar(admin_picture, admin_first_letter, 34, 10, _NAVY, _WHITE),
                                ft.Column(
                                    [
                                        ft.Text(full_name, size=12, font_family="Poppins-SemiBold", color=_NAVY),
                                        ft.Text("Admin", size=10, font_family="Poppins-Light", color=_NAVY_MUTED),
                                    ],
                                    spacing=0,
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.all(12),
                        margin=ft.margin.only(left=8, right=8, bottom=16),
                        border_radius=10,
                        bgcolor=_BORDER_LIGHT,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            width=230,
            bgcolor=_WHITE,
            border=ft.border.only(right=ft.BorderSide(1, _BORDER)),
        )
    else:
        sidebar = DashboardUI.create_sidebar(
            first_name, user_data,
            on_nav=nav_handler,
            on_logout=on_logout,
            active="account",
        )

    sidebar_wrapper = ft.Container(
        content=sidebar, visible=not is_mobile,
    )

    # ── Main body ──
    body_padding = 16 if is_mobile else 32

    body = ft.Container(
        content=ft.Column(
            [
                profile_hero,
                ft.Container(height=12),
                settings_card,
                ft.Container(height=20),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=ft.padding.symmetric(horizontal=body_padding, vertical=12),
        expand=True,
    )

    content_area = ft.Container(
        content=ft.Column([header, body], spacing=0, expand=True),
        expand=True, bgcolor=_BG,
    )

    # ── Responsive handler ──
    def on_resize(e):
        nonlocal is_mobile
        w = page.width or 0
        was_mobile = is_mobile
        is_mobile = w < _SIDEBAR_BREAKPOINT
        if was_mobile != is_mobile:
            sidebar_wrapper.visible = not is_mobile
            body.padding = ft.padding.symmetric(
                horizontal=16 if is_mobile else 32, vertical=12
            )
            page.update()

    page.on_resized = on_resize

    # ── Assemble ──
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = _BG
    page.end_drawer = drawer

    layout = ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(layout)
    update_profile_image()
    page.update()