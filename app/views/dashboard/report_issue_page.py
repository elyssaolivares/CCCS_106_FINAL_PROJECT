import flet as ft
import base64
import io
import mimetypes
import os
import time
import uuid
from app.services.database.database import db
from app.services.ai.ai_services import predict_category
from .session_manager import SessionManager
from .navigation_drawer import NavigationDrawerComponent
from .dashboard_ui import DashboardUI

# ── Palette (matches dashboard) ──
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_WHITE = "#FFFFFF"
_FIELD_BORDER = "#CFD8DC"
_FIELD_FOCUS = "#1565C0"
_SUCCESS = "#2E7D32"
_MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
_MAX_IMAGE_PX = 1080          # max width/height after resize
_JPEG_QUALITY = 78            # JPEG quality for compressed output

_SIDEBAR_BREAKPOINT = 768


def report_issue_page(page: ft.Page, user_data=None):

    page.controls.clear()
    page.overlay.clear()
    page.floating_action_button = None
    page.end_drawer = None
    page.drawer = None

    if not user_data:
        user_data = page.session.get("user_data")
    if not user_data:
        from app.views.loginpage import loginpage
        loginpage(page)
        return

    full_name = user_data.get("name", "User")
    first_name = full_name.split()[0] if full_name else "User"
    user_email = user_data.get("email", "")
    user_type = user_data.get("type", "user")
    is_dark = SessionManager.get_theme_preference(page)

    # Resolve palette from theme
    from app.theme import get_colors as _get_theme
    _t = _get_theme(page)
    _BG = _t["BG"]; _NAVY = _t["NAVY"]; _NAVY_MUTED = _t["NAVY_MUTED"]
    _ACCENT = _t["ACCENT"]; _BORDER = _t["BORDER"]; _BORDER_LIGHT = _t["BORDER_LIGHT"]
    _WHITE = _t["WHITE"]; _FIELD_BORDER = _t["FIELD_BORDER"]; _FIELD_FOCUS = _t["FIELD_FOCUS"]

    # ── Success dialog ──
    def show_success_dialog(category):
        dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                border_radius=16,
                padding=ft.padding.all(28),
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Icon(ft.Icons.CHECK_CIRCLE, size=44, color=_SUCCESS),
                            width=76,
                            height=76,
                            border_radius=38,
                            bgcolor=ft.Colors.with_opacity(0.08, _SUCCESS),
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(height=16),
                        ft.Text(
                            "Report Submitted!",
                            size=18,
                            font_family="Poppins-Bold",
                            color=_NAVY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=6),
                        ft.Text(
                            f"Categorized as: {category}",
                            size=12,
                            font_family="Poppins-Light",
                            color=_NAVY_MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=24),
                        ft.ElevatedButton(
                            text="Done",
                            bgcolor=_ACCENT,
                            color=_WHITE,
                            width=120,
                            height=40,
                            on_click=lambda e: close_dialog(dialog),
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                ),
            ),
            bgcolor=_WHITE,
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        page.dialog = dialog
        if dialog not in page.overlay:
            page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()
        from .user_dashboard import user_dashboard
        user_dashboard(page, user_data)

    # ── Theme toggle ──
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        report_issue_page(page, user_data)

    # ── Nav callbacks ──
    def nav_handler(key):
        def handler(e):
            if key == "home":
                from .user_dashboard import user_dashboard
                user_dashboard(page, user_data, active_section="home")
            elif key == "reports":
                from .user_dashboard import user_dashboard
                user_dashboard(page, user_data, active_section="reports")
            elif key == "account":
                from .account_page import account_page
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

    # ── Sidebar (desktop) ──
    sidebar = DashboardUI.create_sidebar(
        first_name, user_data,
        on_nav=nav_handler,
        on_logout=on_logout,
        active="reports",
        is_dark=is_dark,
    )
    sidebar_ref = ft.Ref[ft.Container]()
    sidebar_wrapper = ft.Container(
        content=sidebar,
        ref=sidebar_ref,
        visible=True,
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )

    # ── Mobile drawer fallback ──
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)

    # ── Form fields ──
    issue_description_field = ft.TextField(
        multiline=True,
        min_lines=5,
        max_lines=8,
        hint_text="What happened? Provide as much detail as possible\u2026",
        border_color=_FIELD_BORDER,
        focused_border_color=_FIELD_FOCUS,
        border_width=1,
        border_radius=12,
        bgcolor=_WHITE,
        color=_NAVY,
        text_size=14,
        content_padding=ft.padding.all(16),
    )

    location_field = ft.TextField(
        hint_text="e.g. Building A, Room 201, 2nd Floor",
        border_color=_FIELD_BORDER,
        focused_border_color=_FIELD_FOCUS,
        border_width=1,
        border_radius=12,
        bgcolor=_WHITE,
        color=_NAVY,
        text_size=14,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
    )

    # ── Optional report photo attachment ──
    selected_report_image = {"data": None, "name": None}
    pending_upload = {"server_name": None, "display_name": None}

    def _compress_image_bytes(raw_bytes, mime_type):
        """Resize to _MAX_IMAGE_PX on longest side and re-encode as JPEG."""
        try:
            from PIL import Image as PilImage, ImageOps
            img = PilImage.open(io.BytesIO(raw_bytes))
            img = ImageOps.exif_transpose(img)  # auto-rotate from EXIF
            img = img.convert("RGB")            # ensure no alpha channel
            w, h = img.size
            if max(w, h) > _MAX_IMAGE_PX:
                scale = _MAX_IMAGE_PX / max(w, h)
                img = img.resize((int(w * scale), int(h * scale)), PilImage.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=_JPEG_QUALITY, optimize=True)
            return buf.getvalue(), "image/jpeg"
        except Exception as ex:
            print(f"Image compression failed, using original: {ex}")
            return raw_bytes, mime_type

    image_name_text = ft.Text(
        "No photo selected",
        size=11,
        font_family="Poppins-Light",
        color=_NAVY_MUTED,
    )

    image_preview = ft.Container(visible=False)

    # Loading indicator shown while the image is uploading / being compressed
    image_upload_status_text = ft.Text(
        "Uploading photo…",
        size=11,
        font_family="Poppins-Medium",
        color=_ACCENT,
    )
    image_upload_status = ft.Container(
        visible=False,
        content=ft.Row(
            [
                ft.ProgressRing(width=14, height=14, stroke_width=2, color=_ACCENT),
                image_upload_status_text,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.06, _ACCENT),
    )

    def _refresh_image_preview():
        image_data = selected_report_image.get("data")
        image_name = selected_report_image.get("name")

        if image_data:
            image_name_text.value = image_name or "Attached photo"
            image_preview.visible = True
            image_preview.content = ft.Stack(
                [
                    ft.Container(
                        content=ft.Image(
                            src_base64=image_data.split(",", 1)[1] if image_data.startswith("data:image") else image_data,
                            fit=ft.ImageFit.COVER,
                        ),
                        width=180,
                        height=110,
                        border_radius=10,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        border=ft.border.all(1, _BORDER),
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_color=_WHITE,
                            icon_size=14,
                            on_click=lambda e: _clear_image(),
                            style=ft.ButtonStyle(
                                bgcolor=ft.Colors.with_opacity(0.7, "#111827"),
                            ),
                        ),
                        right=4,
                        top=4,
                    ),
                ],
                width=180,
                height=110,
            )
        else:
            image_name_text.value = "No photo selected"
            image_preview.visible = False
            image_preview.content = None

        page.update()

    def _clear_image():
        selected_report_image["data"] = None
        selected_report_image["name"] = None
        _refresh_image_preview()

    def _load_image_from_path(path, display_name=None, retries=6, retry_delay=0.4):
        """Read, compress, and base64-encode an image from a local path.
        Retries to handle the race condition where Flet reports upload
        progress=1 before the OS has finished flushing the temp file.
        """
        try:
            if not path:
                _show_snackbar("Selected file could not be accessed.", ft.Colors.RED_400)
                return

            # Wait for file to be fully written (upload race condition)
            for attempt in range(retries):
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    break
                time.sleep(retry_delay)
            else:
                _show_snackbar("Photo upload timed out. Please try again.", ft.Colors.RED_400)
                image_upload_status.visible = False
                page.update()
                return

            file_size = os.path.getsize(path)
            if file_size > _MAX_IMAGE_SIZE_BYTES:
                _show_snackbar("Photo is too large. Max size is 5MB.", ft.Colors.RED_400)
                image_upload_status.visible = False
                page.update()
                return

            mime_type, _ = mimetypes.guess_type(path)
            if not mime_type or not mime_type.startswith("image/"):
                _show_snackbar("Please select a valid image file.", ft.Colors.RED_400)
                image_upload_status.visible = False
                page.update()
                return

            with open(path, "rb") as image_file:
                raw_bytes = image_file.read()

            compressed, mime_type = _compress_image_bytes(raw_bytes, mime_type)
            encoded = base64.b64encode(compressed).decode("utf-8")

            selected_report_image["data"] = f"data:{mime_type};base64,{encoded}"
            selected_report_image["name"] = display_name or os.path.basename(path)
            image_upload_status.visible = False
            _refresh_image_preview()
            _show_snackbar("Photo attached.", ft.Colors.GREEN_400)

        except Exception as ex:
            print(f"Error loading selected image: {ex}")
            image_upload_status.visible = False
            page.update()
            _show_snackbar("Unable to attach this image.", ft.Colors.RED_400)

    def _on_pick_image_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return

        selected_file = e.files[0]

        # Desktop: path is directly accessible — no upload needed
        if selected_file.path:
            image_upload_status.visible = True
            image_upload_status_text.value = "Processing photo…"
            page.update()
            _load_image_from_path(selected_file.path)
            return

        # Mobile/web: must upload to server first, then read back
        file_name = selected_file.name or "report_photo"
        upload_name = f"{uuid.uuid4().hex}_{file_name}"
        pending_upload["server_name"] = upload_name
        pending_upload["display_name"] = file_name

        image_upload_status.visible = True
        image_upload_status_text.value = "Uploading photo…"
        page.update()

        try:
            file_picker.upload(
                [
                    ft.FilePickerUploadFile(
                        file_name,
                        upload_url=page.get_upload_url(upload_name, 600),
                    ),
                ]
            )
        except Exception as ex:
            print(f"Error starting image upload: {ex}")
            image_upload_status.visible = False
            page.update()
            _show_snackbar("Could not upload selected image.", ft.Colors.RED_400)

    def _on_upload_progress(e: ft.FilePickerUploadEvent):
        if e.error:
            _show_snackbar(f"Upload failed: {e.error}", ft.Colors.RED_400)
            image_upload_status.visible = False
            page.update()
            pending_upload["server_name"] = None
            pending_upload["display_name"] = None
            return

        # Update progress text while uploading
        if e.progress is not None and e.progress < 1:
            pct = int(e.progress * 100)
            image_upload_status_text.value = f"Uploading… {pct}%"
            page.update()
            return

        if e.progress is None or e.progress < 1:
            return

        image_upload_status_text.value = "Processing photo…"
        page.update()

        server_name = pending_upload.get("server_name")
        if not server_name:
            return

        uploaded_path = os.path.join("storage", "temp", server_name)
        display_name = pending_upload.get("display_name")
        pending_upload["server_name"] = None
        pending_upload["display_name"] = None

        # _load_image_from_path handles the retry + compression then removes the temp file
        _load_image_from_path(uploaded_path, display_name)

        try:
            if os.path.exists(uploaded_path):
                os.remove(uploaded_path)
        except Exception:
            pass

    file_picker = ft.FilePicker(on_result=_on_pick_image_result, on_upload=_on_upload_progress)
    if file_picker not in page.overlay:
        page.overlay.append(file_picker)

    attach_image_button = ft.OutlinedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ADD_A_PHOTO_OUTLINED, size=16, color=_ACCENT),
                ft.Text("Attach Photo", size=12, font_family="Poppins-Medium", color=_ACCENT),
            ],
            spacing=6,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        on_click=lambda e: file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
        ),
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side=ft.BorderSide(1, _ACCENT),
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
        ),
    )

    # ── Submit logic ──
    def submit_clicked(e):
        issue_desc = issue_description_field.value
        location = location_field.value

        if not issue_desc or not issue_desc.strip():
            _show_snackbar("Please describe the issue before submitting.", ft.Colors.RED_400)
            return

        if not location or not location.strip():
            _show_snackbar("Please provide a location.", ft.Colors.RED_400)
            return

        # Disable button while processing
        submit_button.disabled = True
        submit_button.content.controls[1].value = "Submitting\u2026"
        page.update()

        try:
            category = predict_category(issue_desc)
        except Exception as ex:
            print(f"Error predicting category: {ex}")
            category = "Uncategorized"

        try:
            if not user_email:
                _show_snackbar("Error: User email not found.", ft.Colors.RED_400)
                _reset_submit_button()
                return

            report_id = db.add_report(
                user_email=user_email,
                user_name=full_name,
                user_type=user_type,
                issue_description=issue_desc.strip(),
                location=location.strip(),
                category=category,
                report_image=selected_report_image.get("data"),
            )

            from app.services.audit.audit_logger import audit_logger
            audit_logger.log_action(
                actor_email=user_email,
                actor_name=full_name,
                action_type="report_create",
                resource_type="report",
                resource_id=report_id,
                details=f"Created report at {location.strip()} in category {category}",
                status="success",
            )

            issue_description_field.value = ""
            location_field.value = ""
            _clear_image()
            _reset_submit_button()
            show_success_dialog(category)

        except Exception as ex:
            print(f"Error saving report: {ex}")
            _show_snackbar(f"Error saving report: {str(ex)}", ft.Colors.RED_400)
            _reset_submit_button()

    def _show_snackbar(message, color):
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=_WHITE, font_family="Poppins-Medium", size=13),
            bgcolor=color,
        )
        page.overlay.append(snackbar)
        snackbar.open = True
        page.update()

    def _reset_submit_button():
        submit_button.disabled = False
        submit_button.content.controls[1].value = "Submit Report"
        page.update()

    # ── Submit button ──
    submit_button = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SEND_ROUNDED, size=18, color=_WHITE),
                ft.Text("Submit Report", size=14, font_family="Poppins-SemiBold", color=_WHITE),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
        ),
        bgcolor=_ACCENT,
        height=46,
        on_click=submit_clicked,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=22, vertical=11),
        ),
    )

    # ── Helper: section header chip (numbered step) ──
    def section_chip(number, label):
        return ft.Row(
            [
                ft.Container(
                    content=ft.Text(str(number), size=11, font_family="Poppins-Bold", color=_WHITE),
                    width=22, height=22,
                    border_radius=11,
                    bgcolor=_ACCENT,
                    alignment=ft.alignment.center,
                ),
                ft.Text(label, size=13, font_family="Poppins-SemiBold", color=_NAVY),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def section_hint(text):
        return ft.Text(text, size=11, font_family="Poppins-Light", color=_NAVY_MUTED)

    def section_divider():
        return ft.Container(height=1, bgcolor=_BORDER_LIGHT, margin=ft.margin.symmetric(vertical=20))

    # ── Form card ──
    form_card = ft.Container(
        content=ft.Column(
            [
                # ── Card header ──
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=20, color=_WHITE),
                                width=40, height=40,
                                border_radius=12,
                                bgcolor=_ACCENT,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column(
                                [
                                    ft.Text("Submit a Report", size=17, font_family="Poppins-Bold", color=_NAVY),
                                    ft.Text("Fill in all required fields below", size=11,
                                            font_family="Poppins-Light", color=_NAVY_MUTED),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(bottom=16),
                ),
                ft.Container(height=1, bgcolor=_BORDER),
                ft.Container(height=20),

                # ── Step 1: Description ──
                section_chip(1, "Issue Description"),
                ft.Container(height=4),
                section_hint("Give a clear, detailed description of the problem."),
                ft.Container(height=10),
                issue_description_field,

                section_divider(),

                # ── Step 2: Location ──
                section_chip(2, "Location"),
                ft.Container(height=4),
                section_hint("Where exactly is the issue located?"),
                ft.Container(height=10),
                location_field,

                section_divider(),

                # ── Step 3: Photo ──
                section_chip(3, "Attach a Photo"),
                ft.Container(height=4),
                section_hint("Optional — a photo helps admins assess the issue faster."),
                ft.Container(height=12),
                # Photo upload zone
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    attach_image_button,
                                    ft.Column(
                                        [
                                            image_name_text,
                                            image_upload_status,
                                        ],
                                        spacing=4,
                                    ),
                                ],
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                wrap=True,
                            ),
                            image_preview,
                        ],
                        spacing=10,
                        tight=True,
                    ),
                    padding=ft.padding.all(16),
                    border_radius=12,
                    border=ft.border.all(1.5, _BORDER),
                    bgcolor=_BG,
                ),

                ft.Container(height=20),

                # ── AI note banner ──
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=15, color=_ACCENT),
                                width=28, height=28,
                                border_radius=8,
                                bgcolor=ft.Colors.with_opacity(0.08, _ACCENT),
                                alignment=ft.alignment.center,
                            ),
                            ft.Text(
                                "Your report will be automatically categorized using AI.",
                                size=11, font_family="Poppins-Light", color=_NAVY_MUTED,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(horizontal=14, vertical=11),
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.04, _ACCENT),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.12, _ACCENT)),
                ),

                ft.Container(height=24),

                # ── Submit footer ──
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column(
                                [
                                    ft.Text("Ready to submit?", size=12, font_family="Poppins-SemiBold", color=_NAVY),
                                    ft.Text("You can track status from your dashboard.", size=10,
                                            font_family="Poppins-Light", color=_NAVY_MUTED),
                                ],
                                spacing=1,
                                expand=True,
                            ),
                            submit_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16,
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=14),
                    border_radius=12,
                    bgcolor=_BORDER_LIGHT,
                    border=ft.border.all(1, _BORDER),
                ),
            ],
            spacing=0,
        ),
        padding=ft.padding.all(24),
        bgcolor=_WHITE,
        border_radius=16,
        border=ft.border.all(1, _BORDER),
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=16,
            color=ft.Colors.with_opacity(0.06, "#0F2B5B"),
            offset=ft.Offset(0, 4),
        ),
        width=620,
    )

    # ── Mobile top bar (menu only, no back button) ──
    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()

    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)
    show_sidebar = not is_mobile

    mobile_top_bar = ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("New Report", size=16, font_family="Poppins-Bold", color=_NAVY),
                        ft.Text("Submit a facility issue", size=11, font_family="Poppins-Light", color=_NAVY_MUTED),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Container(
                    content=ft.IconButton(
                        ft.Icons.MENU_ROUNDED,
                        icon_color=_NAVY,
                        icon_size=20,
                        on_click=on_menu_click,
                    ),
                    width=36,
                    height=36,
                    border_radius=10,
                    bgcolor=_BORDER_LIGHT,
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=14, vertical=12),
        bgcolor=_WHITE,
        border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
        visible=is_mobile,
    )
    mobile_top_bar_ref = ft.Ref[ft.Container]()

    # ── Content area ──
    content_area = ft.Container(
        content=ft.Column(
            [
                ft.Container(content=mobile_top_bar, ref=mobile_top_bar_ref),
                ft.Container(
                    content=ft.Column(
                        [form_card],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    padding=ft.padding.symmetric(
                        horizontal=12 if is_mobile else 32,
                        vertical=16 if is_mobile else 28,
                    ),
                    expand=True,
                    alignment=ft.alignment.top_center,
                ),
            ],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        ),
        expand=True,
        bgcolor=_BG,
    )
    content_padding_ref = ft.Ref[ft.Container]()

    # ── Responsive handler ──
    def on_resize(e):
        nonlocal show_sidebar, is_mobile
        w = page.width or 0
        was_mobile = is_mobile
        is_mobile = w < _SIDEBAR_BREAKPOINT
        show_sidebar = not is_mobile

        if was_mobile != is_mobile:
            sidebar_wrapper.visible = show_sidebar
            if mobile_top_bar_ref.current:
                mobile_top_bar_ref.current.content.visible = is_mobile
            page.update()

    page.on_resized = on_resize

    # ── Assemble layout ──
    sidebar_wrapper.visible = show_sidebar
    page.end_drawer = drawer

    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = _BG

    layout = ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(layout)
    page.update()