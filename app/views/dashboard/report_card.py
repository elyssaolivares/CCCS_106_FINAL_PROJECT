import flet as ft
from app.services.database.database import db

# === Color Palette (mirrors dashboard_ui) — resolved per-instance ===
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_LIGHT = "#1A3A6B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_WHITE = "#FFFFFF"
_CARD = "#FFFFFF"
_BORDER = "#E0E6ED"

_STATUS_MAP_LIGHT = {
    "pending":     {"text": "#B45309", "bg": "#FEF3C7", "icon": ft.Icons.SCHEDULE_OUTLINED},
    "in progress": {"text": "#1565C0", "bg": "#DBEAFE", "icon": ft.Icons.AUTORENEW_ROUNDED},
    "resolved":    {"text": "#15803D", "bg": "#DCFCE7", "icon": ft.Icons.CHECK_CIRCLE_OUTLINE},
    "rejected":    {"text": "#DC2626", "bg": "#FEE2E2", "icon": ft.Icons.CANCEL_OUTLINED},
}
_STATUS_MAP_DARK = {
    "pending":     {"text": "#FBBF24", "bg": "#292516", "icon": ft.Icons.SCHEDULE_OUTLINED},
    "in progress": {"text": "#60A5FA", "bg": "#172032", "icon": ft.Icons.AUTORENEW_ROUNDED},
    "resolved":    {"text": "#34D399", "bg": "#0E2820", "icon": ft.Icons.CHECK_CIRCLE_OUTLINE},
    "rejected":    {"text": "#F87171", "bg": "#301414", "icon": ft.Icons.CANCEL_OUTLINED},
}


class ReportCard:
    def __init__(self, page: ft.Page, report, user_data, on_update):
        self.page = page
        self.report = report
        self.user_data = user_data
        self.on_update = on_update
        # Resolve theme colors once per card instance
        from app.theme import get_colors
        _t = get_colors(page)
        self._is_dark = page.session.get("is_dark_theme") or False
        self._BG = _t["BG"]; self._NAVY = _t["NAVY"]; self._NAVY_MUTED = _t["NAVY_MUTED"]
        self._ACCENT = _t["ACCENT"]; self._WHITE = _t["WHITE"]
        self._CARD = _t["CARD"]; self._BORDER = _t["BORDER"]
        self._BORDER_LIGHT = _t["BORDER_LIGHT"]
        self._STATUS_MAP = _STATUS_MAP_DARK if self._is_dark else _STATUS_MAP_LIGHT

    def create(self):
        # Local aliases from instance theme
        _BG = self._BG; _NAVY = self._NAVY; _NAVY_MUTED = self._NAVY_MUTED
        _ACCENT = self._ACCENT; _WHITE = "#FFFFFF"; _CARD = self._CARD
        _BORDER = self._BORDER; _STATUS_MAP = self._STATUS_MAP
        try:
            latest = db.get_report_by_id(self.report.get("id"))
            if latest:
                self.report = latest
        except Exception:
            pass

        location = self.report.get("location", "Unknown Location")
        description = self.report.get("issue_description", "No description")
        status = self.report.get("status", "unknown")

        display_description = (description[:80] + "...") if len(description) > 80 else description
        status_key = (status or "").strip().lower()
        palette = _STATUS_MAP.get(status_key, _STATUS_MAP["pending"])

        remarks = self.report.get("admin_remarks")
        updated_at = self.report.get("status_updated_at")
        updated_by = self.report.get("status_updated_by")
        report_image = self.report.get("report_image")

        # ── Build the column children ──
        col_children = [
            ft.Text(
                location, size=13,
                font_family="Poppins-SemiBold", color=_NAVY,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Text(
                display_description, size=11,
                font_family="Poppins-Light", color=_NAVY_MUTED,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            # Status pill
            ft.Container(
                content=ft.Text(
                    status.title(), size=9,
                    font_family="Poppins-SemiBold",
                    color=palette["text"],
                ),
                bgcolor=palette["bg"],
                padding=ft.padding.symmetric(horizontal=10, vertical=3),
                border_radius=6,
            ),
        ]

        # ── Admin remarks section ──
        if remarks:
            col_children.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.NOTES_ROUNDED, size=12, color=_ACCENT),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Admin Note", size=9,
                                        font_family="Poppins-SemiBold",
                                        color=_ACCENT,
                                    ),
                                    ft.Text(
                                        remarks, size=11,
                                        font_family="Poppins-Light",
                                        color=_NAVY_MUTED, italic=True,
                                        max_lines=3,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                                spacing=1, expand=True,
                            ),
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    bgcolor=ft.Colors.with_opacity(0.05, _ACCENT),
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.1, _ACCENT)),
                    margin=ft.margin.only(top=2),
                )
            )

        # ── Attached issue photo ──
        if report_image:
            image_control = None
            if isinstance(report_image, str) and report_image.startswith("data:image") and "," in report_image:
                image_control = ft.Image(
                    src_base64=report_image.split(",", 1)[1],
                    fit=ft.ImageFit.COVER,
                )
            elif isinstance(report_image, str) and report_image.startswith(("http://", "https://")):
                image_control = ft.Image(
                    src=report_image,
                    fit=ft.ImageFit.COVER,
                )

            if image_control:
                col_children.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Attached Photo", size=9,
                                    font_family="Poppins-SemiBold", color=_NAVY,
                                ),
                                ft.Container(
                                    content=image_control,
                                    width=180,
                                    height=110,
                                    border_radius=8,
                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                    border=ft.border.all(1, _BORDER),
                                ),
                            ],
                            spacing=4,
                            tight=True,
                        ),
                        margin=ft.margin.only(top=2),
                    )
                )

        # ── Last updated info ──
        if updated_at:
            ts_display = str(updated_at)[:16].replace("T", " ") if updated_at else ""
            by_display = f" by {updated_by}" if updated_by else ""
            col_children.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.UPDATE_ROUNDED, size=10, color=_NAVY_MUTED),
                        ft.Text(
                            f"Updated {ts_display}{by_display}", size=9,
                            font_family="Poppins-Light", color=_NAVY_MUTED,
                        ),
                    ],
                    spacing=4,
                )
            )

        return ft.Container(
            content=ft.Row(
                [
                    # Status icon badge
                    ft.Container(
                        content=ft.Icon(palette["icon"], size=16, color=palette["text"]),
                        width=34,
                        height=34,
                        border_radius=8,
                        bgcolor=palette["bg"],
                        alignment=ft.alignment.center,
                    ),
                    # Text content
                    ft.Column(
                        col_children,
                        spacing=3,
                        expand=True,
                    ),
                    # 3-dot menu
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        icon_color=_NAVY_MUTED,
                        icon_size=18,
                        items=[
                            ft.PopupMenuItem(icon=ft.Icons.EDIT_OUTLINED, text="Edit", on_click=self._show_edit_dialog),
                            ft.PopupMenuItem(icon=ft.Icons.DELETE_OUTLINE, text="Delete", on_click=self._show_delete_dialog),
                        ],
                    ),
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=ft.padding.all(12),
            margin=ft.margin.only(bottom=6),
            bgcolor=_CARD,
            border_radius=12,
            border=ft.border.all(1, _BORDER),
        )

    # ── legacy helpers (kept for dialogs) ──
    def _get_status_bg(self, status):
        s = (status or "").strip().lower()
        return self._STATUS_MAP.get(s, self._STATUS_MAP["pending"])["bg"]

    def _get_status_color(self, status):
        s = (status or "").strip().lower()
        return self._STATUS_MAP.get(s, self._STATUS_MAP["pending"])["text"]

    def _show_edit_dialog(self, e):
        # Local aliases from instance theme
        _NAVY = self._NAVY; _NAVY_MUTED = self._NAVY_MUTED
        _ACCENT = self._ACCENT; _WHITE = "#FFFFFF"
        _BORDER = self._BORDER
        location = self.report.get('location', '')
        description = self.report.get('issue_description', '')
        report_id = self.report.get('id')

        location_field = ft.TextField(
            value=location,
            hint_text="e.g. Building A, Room 201",
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
            border_color=_BORDER,
            focused_border_color=_ACCENT,
            border_radius=10,
            bgcolor=self._BORDER_LIGHT,
            color=_NAVY,
            text_size=13,
            content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
        )

        issue_field = ft.TextField(
            value=description,
            multiline=True,
            min_lines=4,
            max_lines=6,
            hint_text="Describe the issue in detail…",
            border_color=_BORDER,
            focused_border_color=_ACCENT,
            border_radius=10,
            bgcolor=self._BORDER_LIGHT,
            color=_NAVY,
            text_size=13,
            content_padding=ft.padding.all(14),
        )

        error_text = ft.Text("", size=11, color="#DC2626", visible=False)

        def save_and_close(e):
            if not issue_field.value or not issue_field.value.strip():
                error_text.value = "Please describe the issue."
                error_text.visible = True
                self.page.update()
                return
            if not location_field.value or not location_field.value.strip():
                error_text.value = "Please provide a location."
                error_text.visible = True
                self.page.update()
                return
            try:
                db.update_report(
                    report_id,
                    issue_field.value.strip(),
                    location_field.value.strip(),
                )
                dialog.open = False
                self.page.update()
                self._show_snackbar("Report updated successfully!", "#15803D")
                self.on_update()
            except Exception as ex:
                print(f"Error updating report: {ex}")
                self._show_snackbar(f"Error updating report: {str(ex)}", "#DC2626")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=18, color=_WHITE),
                        width=34, height=34,
                        border_radius=10,
                        bgcolor=_ACCENT,
                        alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text("Edit Report", size=15, font_family="Poppins-Bold", color=_NAVY),
                            ft.Text(f"Report #{report_id}", size=10,
                                    font_family="Poppins-Light", color=_NAVY_MUTED),
                        ],
                        spacing=1,
                        expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Location", size=11, font_family="Poppins-SemiBold", color=_NAVY),
                        ft.Container(height=4),
                        location_field,
                        ft.Container(height=14),
                        ft.Text("Issue Description", size=11, font_family="Poppins-SemiBold", color=_NAVY),
                        ft.Container(height=4),
                        issue_field,
                        error_text,
                    ],
                    spacing=0,
                    tight=True,
                ),
                width=380,
                padding=ft.padding.only(top=4),
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancel", size=13, font_family="Poppins-Medium", color=_NAVY_MUTED),
                    on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                ),
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_ROUNDED, size=15, color=_WHITE),
                            ft.Text("Save Changes", size=13, font_family="Poppins-SemiBold", color=_WHITE),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    bgcolor=_ACCENT,
                    on_click=save_and_close,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=18, vertical=10),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=_WHITE,
            shape=ft.RoundedRectangleBorder(radius=16),
        )

        self.page.open(dialog)
    
    def _show_delete_dialog(self, e):
        # Local aliases from instance theme
        _NAVY = self._NAVY; _NAVY_MUTED = self._NAVY_MUTED
        _ACCENT = self._ACCENT; _WHITE = "#FFFFFF"
        _BORDER = self._BORDER
        _AMBER = self._is_dark and "#FBBF24" or "#B45309"
        _AMBER_BG = self._is_dark and "#292516" or "#FEF3C7"
        report_id = self.report.get('id')
        location = self.report.get('location', 'Unknown Location')
        desc = self.report.get('issue_description', '')
        short_desc = (desc[:60] + '…') if len(desc) > 60 else desc

        def confirm_delete(e):
            try:
                from app.services.audit.audit_logger import audit_logger
                db.delete_report(report_id)
                user_email = self.user_data.get('email', 'unknown@example.com') if self.user_data else 'unknown@example.com'
                user_name = self.user_data.get('name', 'Unknown User') if self.user_data else 'Unknown User'
                audit_logger.log_action(
                    actor_email=user_email,
                    actor_name=user_name,
                    action_type='report_delete',
                    resource_type='report',
                    resource_id=report_id,
                    details=f'Deleted report at {location}',
                    status='success',
                )
                dialog.open = False
                self.page.update()
                self._show_snackbar("Report deleted successfully!", "#15803D")
                self.on_update()
            except Exception as ex:
                print(f"Error deleting report: {ex}")
                self._show_snackbar(f"Error deleting report: {str(ex)}", "#DC2626")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED, size=18, color=_WHITE),
                        width=34, height=34,
                        border_radius=10,
                        bgcolor="#DC2626",
                        alignment=ft.alignment.center,
                    ),
                    ft.Text("Delete Report", size=15, font_family="Poppins-Bold", color=_NAVY),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        # Report preview card
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=13, color=_NAVY_MUTED),
                                            ft.Text(location, size=12, font_family="Poppins-SemiBold",
                                                    color=_NAVY, expand=True,
                                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ],
                                        spacing=4,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Text(short_desc, size=11, font_family="Poppins-Light",
                                            color=_NAVY_MUTED, max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS),
                                ],
                                spacing=4,
                                tight=True,
                            ),
                            padding=ft.padding.all(12),
                            bgcolor=self._BORDER_LIGHT if hasattr(self, '_BORDER_LIGHT') else "#F8FAFC",
                            border_radius=10,
                            border=ft.border.all(1, _BORDER),
                        ),
                        ft.Container(height=14),
                        # Warning text
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color=_AMBER),
                                    ft.Text(
                                        "This action is permanent and cannot be undone.",
                                        size=11, font_family="Poppins-Medium", color=_AMBER,
                                        expand=True,
                                    ),
                                ],
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.symmetric(horizontal=12, vertical=10),
                            border_radius=8,
                            bgcolor=_AMBER_BG,
                            border=ft.border.all(1, ft.Colors.with_opacity(0.3, _AMBER)),
                        ),
                    ],
                    spacing=0,
                    tight=True,
                ),
                width=360,
                padding=ft.padding.only(top=4),
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancel", size=13, font_family="Poppins-Medium", color=_NAVY_MUTED),
                    on_click=lambda e: (setattr(dialog, 'open', False), self.page.update()),
                ),
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED, size=15, color=_WHITE),
                            ft.Text("Delete", size=13, font_family="Poppins-SemiBold", color=_WHITE),
                        ],
                        spacing=6,
                        tight=True,
                    ),
                    bgcolor="#DC2626",
                    on_click=confirm_delete,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=18, vertical=10),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=_WHITE,
            shape=ft.RoundedRectangleBorder(radius=16),
        )

        self.page.open(dialog)
    
    def _show_snackbar(self, message, bgcolor):
        """Show snackbar notification"""
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=bgcolor,
            duration=3000,
        )
        self.page.overlay.append(snackbar)
        snackbar.open = True
        self.page.update()