"""Audit Log Viewer page for admins - compliance + debugging."""

import flet as ft
from datetime import datetime, timedelta
from app.services.audit.audit_logger import audit_logger


def audit_logs_page(page: ft.Page, user_data=None):
    page.controls.clear()
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    if not user_data or user_data.get("type", "").lower() != "admin":
        page.snack_bar = ft.SnackBar(ft.Text("Access Denied: Admin only"))
        page.snack_bar.open = True
        page.update()
        return
    
    is_dark = page.session.get("is_dark_theme") or False
    
    def go_back_to_dashboard(e):
        from .admin_dashboard import admin_dashboard
        admin_dashboard(page, user_data)
    
    
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "Audit Logs",
                    size=20,
                    font_family="Poppins-Bold",
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    on_click=go_back_to_dashboard,
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
    
    filter_actor_email = ft.TextField(
        label="Actor Email",
        width=200,
        border_color="#062C80",
        focused_border_color="#093AA5",
    )
    
    filter_action = ft.Dropdown(
        label="Action Type",
        width=200,
        options=[
            ft.dropdown.Option("login"),
            ft.dropdown.Option("logout"),
            ft.dropdown.Option("report_create"),
            ft.dropdown.Option("report_update"),
            ft.dropdown.Option("report_delete"),
            ft.dropdown.Option("user_edit"),
            ft.dropdown.Option("password_change"),
        ],
        border_color="#062C80",
    )
    
    filter_status = ft.Dropdown(
        label="Status",
        width=150,
        options=[
            ft.dropdown.Option("success"),
            ft.dropdown.Option("failed"),
        ],
        border_color="#062C80",
    )
    
    start_date_field = ft.TextField(
        label="Start Date (YYYY-MM-DD)",
        width=200,
        border_color="#062C80",
        focused_border_color="#093AA5",
        hint_text="2025-01-01",
    )
    
    end_date_field = ft.TextField(
        label="End Date (YYYY-MM-DD)",
        width=200,
        border_color="#062C80",
        focused_border_color="#093AA5",
        hint_text="2025-12-31",
    )

    logs_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)
    
    current_page = {"page": 0}
    page_size = 50
    
    def load_logs():
        logs_list.controls.clear()
        
        actor_email = filter_actor_email.value if filter_actor_email.value else None
        action_type = filter_action.value if filter_action.value else None
        status = filter_status.value if filter_status.value else None
        start_date = start_date_field.value if start_date_field.value else None
        end_date = end_date_field.value if end_date_field.value else None
        
        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").isoformat()
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").isoformat()
        except ValueError:
            logs_list.controls.append(
                ft.Container(
                    content=ft.Text("Invalid date format. Use YYYY-MM-DD", color=ft.Colors.RED),
                    padding=10,
                )
            )
            page.update()
            return
        
        offset = current_page["page"] * page_size
        logs = audit_logger.get_audit_logs(
            actor_email=actor_email,
            action_type=action_type,
            start_date=start_date,
            end_date=end_date,
            limit=page_size,
            offset=offset
        )
        
        total_count = audit_logger.get_audit_logs_count(
            actor_email=actor_email,
            action_type=action_type,
            start_date=start_date,
            end_date=end_date
        )
        
        if not logs:
            logs_list.controls.append(
                ft.Container(
                    content=ft.Text("No audit logs found", color=ft.Colors.GREY),
                    padding=10,
                )
            )
        else:
            for log in logs:
                log_card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(f"Actor: {log['actor_name'] or log['actor_email']}", weight="bold"),
                                            ft.Text(f"Email: {log['actor_email']}", size=12, color=ft.Colors.GREY),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(f"Action: {log['action_type']}", weight="bold"),
                                            ft.Text(f"Resource: {log['resource_type'] or 'N/A'} (ID: {log['resource_id'] or 'N/A'})", size=12, color=ft.Colors.GREY),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(log['timestamp'][:19], size=12),
                                            ft.Container(
                                                content=ft.Text(
                                                    log['status'].upper(),
                                                    size=11,
                                                    color=ft.Colors.WHITE,
                                                ),
                                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                                bgcolor=ft.Colors.GREEN if log['status'] == 'success' else ft.Colors.RED,
                                                border_radius=4,
                                            ),
                                        ],
                                        spacing=2,
                                        alignment=ft.MainAxisAlignment.END,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                expand=True,
                            ),
                            ft.Divider(height=1, color=ft.Colors.GREY_400),
                            ft.Text(f"Details: {log['details'] or 'N/A'}", size=11, color=ft.Colors.GREY),
                        ],
                        spacing=5,
                    ),
                    padding=ft.padding.all(12),
                    bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.GREY_100,
                    border_radius=8,
                )
                logs_list.controls.append(log_card)
        
        # Pagination info
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
        pagination_text = ft.Text(
            f"Page {current_page['page'] + 1} of {total_pages} ({total_count} total logs)",
            size=12,
            color=ft.Colors.GREY,
        )
        logs_list.controls.append(pagination_text)
        
        page.update()
    
    def on_filter_click(e):
        current_page["page"] = 0
        load_logs()
    
    def on_prev_page(e):
        if current_page["page"] > 0:
            current_page["page"] -= 1
            load_logs()
    
    def on_next_page(e):
        total_count = audit_logger.get_audit_logs_count()
        total_pages = (total_count + page_size - 1) // page_size
        if current_page["page"] < total_pages - 1:
            current_page["page"] += 1
            load_logs()
    
    def on_export_csv(e):
        """Export logs to CSV."""
        import csv
        from datetime import datetime
        
        actor_email = filter_actor_email.value if filter_actor_email.value else None
        action_type = filter_action.value if filter_action.value else None
        
        logs = audit_logger.get_audit_logs(
            actor_email=actor_email,
            action_type=action_type,
            limit=10000  # Export up to 10k logs
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_logs_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'actor_email', 'actor_name', 'action_type', 'resource_type', 'resource_id', 'details', 'timestamp', 'status'])
                writer.writeheader()
                writer.writerows(logs)
            
            page.snack_bar = ft.SnackBar(ft.Text(f"Exported to {filename}"))
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Export failed: {str(ex)}"), bgcolor=ft.Colors.RED)
        
        page.snack_bar.open = True
        page.update()
    
    # Filter section
    filter_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Filters", size=16, font_family="Poppins-SemiBold", color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
                ft.Row(
                    [filter_actor_email, filter_action, filter_status],
                    spacing=10,
                    wrap=True,
                ),
                ft.Row(
                    [start_date_field, end_date_field],
                    spacing=10,
                    wrap=True,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton("Search", on_click=on_filter_click, bgcolor="#062C80"),
                        ft.ElevatedButton("Export CSV", on_click=on_export_csv, bgcolor="#4CAF50"),
                    ],
                    spacing=10,
                ),
            ],
            spacing=10,
        ),
        padding=ft.padding.all(15),
        bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
        border_radius=8,
        margin=ft.margin.all(10),
    )
    
    pagination_row = ft.Row(
        [
            ft.ElevatedButton("< Previous", on_click=on_prev_page, width=150),
            ft.ElevatedButton("Next >", on_click=on_next_page, width=150),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    main_container = ft.Column(
        [
            filter_section,
            ft.Container(height=10),
            ft.Text("Logs", size=14, font_family="Poppins-SemiBold", color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
            logs_list,
            ft.Container(height=10),
            pagination_row,
        ],
        expand=True,
        spacing=0,
    )
    
    responsive_wrapper = ft.Column(
        [
            header,
            ft.Container(height=20),
            ft.Container(
                content=main_container,
                alignment=ft.alignment.top_center,
                expand=True,
                padding=ft.padding.symmetric(horizontal=25),
            ),
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
    
    page.bgcolor = ft.Colors.GREY_900 if is_dark else ft.Colors.GREY_100
    page.add(responsive_wrapper)
    
    # Load initial logs
    load_logs()
