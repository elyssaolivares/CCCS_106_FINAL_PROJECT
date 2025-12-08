import flet as ft
from app.services.database.database import db

class ReportCard:
    def __init__(self, page: ft.Page, report, user_data, on_update):
        self.page = page
        self.report = report
        self.user_data = user_data
        self.on_update = on_update
    
    def create(self):
        try:
            latest = db.get_report_by_id(self.report.get('id'))
            if latest:
                self.report = latest
        except Exception:
            pass

        location = self.report.get('location', 'Unknown Location')
        description = self.report.get('issue_description', 'No description')
        status = self.report.get('status', 'unknown')
        
        display_description = description[:50] + "..." if len(description) > 50 else description
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row([
                                ft.Icon(ft.Icons.PLACE, size=20, color=ft.Colors.WHITE), 
                                ft.Text(location.upper(), size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                            ], spacing=8),
                            ft.Text(display_description, size=14, color=ft.Colors.WHITE70),
                            ft.Text(
                                status.title(),
                                size=12,
                                color=self._get_status_color(status),
                                italic=True
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        icon_color=ft.Colors.WHITE,
                        items=[
                            ft.PopupMenuItem(
                                icon=ft.Icons.EDIT_OUTLINED,
                                text="Edit",
                                on_click=self._show_edit_dialog
                            ),
                            ft.PopupMenuItem(
                                icon=ft.Icons.DELETE_OUTLINE,
                                text="Delete",
                                on_click=self._show_delete_dialog
                            ),
                        ],
                    ),
                ],
                spacing=15,
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=15,
            margin=ft.margin.only(bottom=10),
            bgcolor="#062C80",
            border_radius=10,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        )
    
    def _get_status_color(self, status):
        color_map = {
            'resolved': ft.Colors.GREEN,
            'in progress': ft.Colors.ORANGE,
            'rejected': ft.Colors.RED_400,
            'pending': ft.Colors.AMBER_700,
        }
        return color_map.get((status or '').strip().lower(), ft.Colors.WHITE70)
    
    def _show_edit_dialog(self, e):
        location = self.report.get('location', 'Unknown Location')
        description = self.report.get('issue_description', 'No description')
        report_id = self.report.get('id')
        
        
        location_field = ft.TextField(
            value=location,
            label="Location",
            border_color="#003D82",
            focused_border_color="#003D82",
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
            filled=True,
        )
        
        issue_field = ft.TextField(
            value=description,
            multiline=True,
            min_lines=3,
            max_lines=5,
            label="Issue Description",
            hint_text="Describe the issue here...",
            border_color="#003D82",
            focused_border_color="#003D82",
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
            filled=True,
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
            title=ft.Text("Edit Report", weight=ft.FontWeight.BOLD, size=18),
            content=ft.Container(
                content=ft.Column([
                    location_field, 
                    ft.Container(height=10), 
                    issue_field
                ], spacing=10, tight=True),
                width=400,
                padding=10
            ),
            actions=[
                ft.TextButton(
                    "Cancel", 
                    on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()
                ),
                ft.ElevatedButton(
                    "OK", 
                    on_click=save_and_close, 
                    bgcolor=ft.Colors.DEEP_ORANGE_400, 
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.WHITE)
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
            title=ft.Text("Confirm Delete", weight=ft.FontWeight.BOLD, color=ft.Colors.RED_900),
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_400, size=48),
                    ft.Container(height=10),
                    ft.Text(
                        "Are you sure you want to delete this report?", 
                        text_align=ft.TextAlign.CENTER, 
                        weight=ft.FontWeight.W_500
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        f'"{location}"',
                        text_align=ft.TextAlign.CENTER,
                        size=14,
                        color=ft.Colors.GREY_800,
                        italic=True
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        "This action cannot be undone.", 
                        text_align=ft.TextAlign.CENTER, 
                        size=12, 
                        color=ft.Colors.GREY_700
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
                    bgcolor=ft.Colors.RED_400, 
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
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