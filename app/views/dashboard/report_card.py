import flet as ft
from app.services.database.database import db

# === Color Palette (mirrors dashboard_ui) ===
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_LIGHT = "#1A3A6B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_WHITE = "#FFFFFF"
_CARD = "#FFFFFF"
_BORDER = "#E0E6ED"

_STATUS_MAP = {
    "pending":     {"text": "#B45309", "bg": "#FEF3C7", "icon": ft.Icons.SCHEDULE_OUTLINED},
    "in progress": {"text": "#1565C0", "bg": "#DBEAFE", "icon": ft.Icons.AUTORENEW_ROUNDED},
    "resolved":    {"text": "#15803D", "bg": "#DCFCE7", "icon": ft.Icons.CHECK_CIRCLE_OUTLINE},
    "rejected":    {"text": "#DC2626", "bg": "#FEE2E2", "icon": ft.Icons.CANCEL_OUTLINED},
}


class ReportCard:
    def __init__(self, page: ft.Page, report, user_data, on_update):
        self.page = page
        self.report = report
        self.user_data = user_data
        self.on_update = on_update

    def create(self):
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
        return _STATUS_MAP.get(s, _STATUS_MAP["pending"])["bg"]

    def _get_status_color(self, status):
        s = (status or "").strip().lower()
        return _STATUS_MAP.get(s, _STATUS_MAP["pending"])["text"]
    
    def _show_edit_dialog(self, e):
        location = self.report.get('location', 'Unknown Location')
        description = self.report.get('issue_description', 'No description')
        report_id = self.report.get('id')
        
        
        location_field = ft.TextField(
            value=location,
            label="Location",
            border_color=_BORDER,
            focused_border_color=_ACCENT,
            border_radius=10,
            bgcolor=_BG,
            color=_NAVY,
            text_size=13,
        )

        issue_field = ft.TextField(
            value=description,
            multiline=True,
            min_lines=3,
            max_lines=5,
            label="Issue Description",
            hint_text="Describe the issue here...",
            border_color=_BORDER,
            focused_border_color=_ACCENT,
            border_radius=10,
            bgcolor=_BG,
            color=_NAVY,
            text_size=13,
        )
        
        def save_and_close(e):
            
            if not issue_field.value or not issue_field.value.strip():
                self._show_snackbar("Please describe the issue", ft.Colors.RED_400)
                return
            
            if not location_field.value or not location_field.value.strip():
                self._show_snackbar("Please provide a location", ft.Colors.RED_400)
                return
            
            try:
                
                db.update_report(
                    report_id, 
                    issue_field.value.strip(), 
                    location_field.value.strip()
                )
                
                
                dialog.open = False
                self.page.update()
                
                
                self._show_snackbar("Report updated successfully!", ft.Colors.GREEN_400)
                
                
                self.on_update()
                    
            except Exception as ex:
                print(f"Error updating report: {ex}")
                self._show_snackbar(f"Error updating report: {str(ex)}", ft.Colors.RED_400)
        
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Report", font_family="Poppins-Bold", size=18, color=_NAVY),
            content=ft.Container(
                content=ft.Column([
                    location_field,
                    ft.Container(height=10),
                    issue_field
                ], spacing=10, tight=True),
                padding=10,
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()
                ),
                ft.ElevatedButton(
                    "Save",
                    on_click=save_and_close,
                    bgcolor=_ACCENT,
                    color=_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=_WHITE,
            shape=ft.RoundedRectangleBorder(radius=16),
        )
        
        
        self.page.open(dialog)
    
    def _show_delete_dialog(self, e):
        report_id = self.report.get('id')
        location = self.report.get('location', 'Unknown Location')
        
        def confirm_delete(e):
            try:
                from app.services.audit.audit_logger import audit_logger
                
                db.delete_report(report_id)
                
                # Log the delete action to audit logs
                user_email = self.user_data.get('email', 'unknown@example.com') if self.user_data else 'unknown@example.com'
                user_name = self.user_data.get('name', 'Unknown User') if self.user_data else 'Unknown User'
                audit_logger.log_action(
                    actor_email=user_email,
                    actor_name=user_name,
                    action_type='report_delete',
                    resource_type='report',
                    resource_id=report_id,
                    details=f'Deleted report at {location}',
                    status='success'
                )
                
                dialog.open = False
                self.page.update()
                
                
                self._show_snackbar("Report deleted successfully!", ft.Colors.GREEN_400)
                
                
                self.on_update()
                    
            except Exception as ex:
                print(f"Error deleting report: {ex}")
                self._show_snackbar(f"Error deleting report: {str(ex)}", ft.Colors.RED_400)
        
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete Report", font_family="Poppins-Bold", color="#DC2626"),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#DC2626", size=40),
                        width=70,
                        height=70,
                        border_radius=35,
                        bgcolor="#FEE2E2",
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Are you sure you want to delete this report?",
                        text_align=ft.TextAlign.CENTER,
                        font_family="Poppins-Medium",
                        size=14,
                        color=_NAVY,
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        f'"  {location}"',
                        text_align=ft.TextAlign.CENTER,
                        size=13,
                        color=_NAVY_MUTED,
                        italic=True,
                        font_family="Poppins-Light",
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        "This action cannot be undone.",
                        text_align=ft.TextAlign.CENTER,
                        size=11,
                        color=_NAVY_MUTED,
                        font_family="Poppins-Light",
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()
                ),
                ft.ElevatedButton(
                    "Delete",
                    on_click=confirm_delete,
                    bgcolor="#DC2626",
                    color=_WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                )
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