import flet as ft
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
                user_dashboard(page, user_data)
            elif key == "reports":
                report_issue_page(page, user_data)
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
        ),
        bgcolor=_ACCENT,
        width=200,
        height=48,
        on_click=submit_clicked,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        ),
    )

    # ── Helper: field label with icon ──
    def field_label(icon, text, subtitle=None):
        controls = [
            ft.Row(
                [
                    ft.Icon(icon, size=16, color=_ACCENT),
                    ft.Text(text, size=13, font_family="Poppins-SemiBold", color=_NAVY),
                ],
                spacing=8,
            ),
        ]
        if subtitle:
            controls.append(
                ft.Text(subtitle, size=11, font_family="Poppins-Light", color=_NAVY_MUTED),
            )
        return ft.Column(controls, spacing=2)

    # ── Form card ──
    form_card = ft.Container(
        content=ft.Column(
            [
                # ── Form header ──
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=22, color=_ACCENT),
                                        width=44,
                                        height=44,
                                        border_radius=12,
                                        bgcolor=ft.Colors.with_opacity(0.08, _ACCENT),
                                        alignment=ft.alignment.center,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("New Report", size=20, font_family="Poppins-Bold", color=_NAVY),
                                            ft.Text(
                                                "Describe the issue",
                                                size=12, font_family="Poppins-Light", color=_NAVY_MUTED,
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                ],
                                spacing=14,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # ── Divider ──
                ft.Container(height=1, bgcolor=_BORDER),
                ft.Container(height=20),
                # ── Issue description ──
                field_label(
                    ft.Icons.DESCRIPTION_OUTLINED,
                    "Issue Description",
                    "Provide a detailed description of the problem.",
                ),
                ft.Container(height=8),
                issue_description_field,
                ft.Container(height=24),
                # ── Location ──
                field_label(
                    ft.Icons.LOCATION_ON_OUTLINED,
                    "Location",
                    "Where exactly is the problem?",
                ),
                ft.Container(height=8),
                location_field,
                ft.Container(height=10),
                # ── AI note ──
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, size=14, color=_ACCENT),
                            ft.Text(
                                "Your report will be automatically categorized using AI.",
                                size=11,
                                font_family="Poppins-Light",
                                color=_NAVY_MUTED,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.04, _ACCENT),
                ),
                ft.Container(height=28),
                # ── Submit ──
                ft.Row(
                    [submit_button],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            spacing=0,
        ),
        padding=ft.padding.all(28),
        bgcolor=_WHITE,
        border_radius=16,
        border=ft.border.all(1, _BORDER),
        width=600,
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
                        vertical=20 if is_mobile else 32,
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

    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = _BG

    layout = ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(layout)
    page.update()