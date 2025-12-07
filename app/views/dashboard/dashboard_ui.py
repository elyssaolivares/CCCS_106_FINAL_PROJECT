import flet as ft

class DashboardUI:
    @staticmethod
    def create_header(first_name, user_type, is_dark, on_menu_click):
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    f"{first_name}'s Dashboard" + (" (Admin)" if user_type == "admin" else ""),
                    size=20,
                    font_family="Poppins-Bold",
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                ),
                ft.IconButton(
                    ft.Icons.MENU, 
                    icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK, 
                    on_click=on_menu_click
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )
    
    @staticmethod
    def create_statistics_row(total_issues, resolved_issues):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Reports", size=14, font_family="Poppins-Bold", color="#3A3EB8"),
                            ft.Text(str(total_issues), size=25, font_family="Poppins-Bold", color="#3A3EB8")
                        ]),
                        padding=25,
                        bgcolor="#DFE4FA",
                        border_radius=10,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Resolved", size=14, font_family="Poppins-Bold",color="#4CAF50"),
                            ft.Text(str(resolved_issues), size=25, font_family="Poppins-Bold", color="#4CAF50")
                        ]),
                        padding=25,
                        bgcolor="#E8F5E9",
                        border_radius=10,
                        expand=True,
                    ),
                ],
                spacing=10
            ),
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
            padding=12,
            border_radius=10,
        )
    
    @staticmethod
    def create_content_container(content, is_dark):
        return ft.Container(
            content=content,
            bgcolor=ft.Colors.GREY_900 if is_dark else ft.Colors.GREY_100,
            expand=True,
            padding=20,
        )
    
    @staticmethod
    def create_reports_container(content):
        """Create reports list container with floating card effect"""
        return ft.Container(
            content=content,
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
            border_radius=10,
            padding=12,
        )
    
    @staticmethod
    def create_filter_buttons(on_filter_changed):
        filter_button_refs = {}

        pending_text = ft.Text("Pending", size=10, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)
        ongoing_text = ft.Text("Ongoing", size=10, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_500)
        resolved_text = ft.Text("Resolved", size=10, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_500)
        rejected_text = ft.Text("Rejected", size=10, weight=ft.FontWeight.W_600, color=ft.Colors.GREY_500)
        
        pending_btn = ft.Container(
            content=pending_text,
            bgcolor="#062C80",
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
            border_radius=8,
            alignment=ft.alignment.center,
            on_click=on_filter_changed("Pending"),
            expand=True,
        )
        filter_button_refs["Pending"] = {"btn": pending_btn, "text": pending_text}
        
        ongoing_btn = ft.Container(
            content=ongoing_text,
            bgcolor=ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
            border_radius=8,
            alignment=ft.alignment.center,
            on_click=on_filter_changed("In Progress"),
            expand=True,
        )
        filter_button_refs["In Progress"] = {"btn": ongoing_btn, "text": ongoing_text}
        
        resolved_btn = ft.Container(
            content=resolved_text,
            bgcolor=ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
            border_radius=8,
            alignment=ft.alignment.center,
            on_click=on_filter_changed("Resolved"),
            expand=True,
        )
        filter_button_refs["Resolved"] = {"btn": resolved_btn, "text": resolved_text}
        
        rejected_btn = ft.Container(
            content=rejected_text,
            bgcolor=ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
            border_radius=8,
            alignment=ft.alignment.center,
            on_click=on_filter_changed("Rejected"),
            expand=True,
        )
        filter_button_refs["Rejected"] = {"btn": rejected_btn, "text": rejected_text}
        
        filter_row = ft.Row(
            [pending_btn, ongoing_btn, resolved_btn, rejected_btn],
            spacing=10,
        )
        
        filter_container = ft.Container(
            content=filter_row,
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
            padding=8,
            border_radius=8,
        )
        
        return filter_container, filter_button_refs
    
    @staticmethod
    def create_empty_state(first_name, is_dark, on_report_click):
        return ft.Column(
            [
                ft.Container(height=20),
                ft.Text(
                    f"Welcome, {first_name}",
                    size=28,
                    font_family="Poppins-Bold",
                    color="#062C80",
                ),
                ft.Container(height=30),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Container(height=30),
                            ft.Icon(
                                ft.Icons.DESCRIPTION_OUTLINED,
                                size=80,
                                color=ft.Colors.GREY_400,
                            ),
                            ft.Container(height=20),
                            ft.Text(
                                "You haven't reported",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800 if not is_dark else ft.Colors.GREY_400,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "any issues yet.",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_800 if not is_dark else ft.Colors.GREY_400,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=15),
                            ft.Text(
                                "Click \"Report Issue\" to get started.",
                                size=12,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(height=25),
                            ft.ElevatedButton(
                                text="Report Issue",
                                bgcolor=ft.Colors.DEEP_ORANGE_400,
                                color=ft.Colors.WHITE,
                                width=140,
                                height=40,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=5),
                                ),
                                on_click=on_report_click,
                            ),
                            ft.Container(height=30),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    bgcolor=ft.Colors.WHITE if not is_dark else ft.Colors.GREY_800,
                    border=ft.border.all(1, ft.Colors.GREY_300 if not is_dark else ft.Colors.GREY_700),
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=40, vertical=20),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 4),
                    ),
                ),
            ],
            spacing=0,
        )
    
    @staticmethod
    def create_no_reports_message():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.INBOX_OUTLINED, size=64, color=ft.Colors.GREY_400),
                    ft.Text(
                        "No reports found",
                        size=16,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=40,
            alignment=ft.alignment.center
        )
    
    @staticmethod
    def create_fab(on_click):
        return ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=on_click,
            bgcolor="#062C80"
        )