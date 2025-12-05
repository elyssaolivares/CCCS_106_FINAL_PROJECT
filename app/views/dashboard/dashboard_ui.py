import flet as ft

class DashboardUI:
    @staticmethod
    def create_header(first_name, user_type, is_dark, on_menu_click):
        """Create dashboard header"""
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
        """Create statistics cards row"""
        return ft.Row(
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("Total Reports", size=14, font_family="Poppins-Bold", color="#DA5656"),
                        ft.Text(str(total_issues), size=30, font_family="Poppins-Bold", color="#DA5656")
                    ]),
                    padding=30,
                    bgcolor="#FFEBEB",
                    border_radius=10,
                    expand=True,
                    
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Resolved", size=14, font_family="Poppins-Bold",color="#70B172"),
                        ft.Text(str(resolved_issues), size=30, font_family="Poppins-Bold", color="#70B172")
                    ]),
                    padding=30,
                    bgcolor="#E3F4DB",
                    border_radius=10,
                    expand=True,
                    
                ),
            ],
            spacing=10
        )
    
    @staticmethod
    def create_filter_buttons(on_filter_changed):
        """Create filter buttons for reports"""
        filter_button_refs = {}
        
        pending_btn = ft.ElevatedButton(
            "Pending",
            on_click=on_filter_changed("Pending"),
            bgcolor="#062C80",
            color=ft.Colors.WHITE,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
                text_style=ft.TextStyle(
                    font_family="Poppins-Bold", size=10
            ),
        ),
            )
        filter_button_refs["Pending"] = pending_btn
        
        ongoing_btn = ft.ElevatedButton(
            "Ongoing",
            on_click=on_filter_changed("In Progress"),
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
            expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                 text_style=ft.TextStyle(
                    font_family="Poppins-Bold", size=10),
        ))
        filter_button_refs["In Progress"] = ongoing_btn
        
        resolved_btn = ft.ElevatedButton(
            "Resolved",
            on_click=on_filter_changed("Resolved"),
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
            expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                 text_style=ft.TextStyle(
                    font_family="Poppins-Bold", size=10)),
        )
        filter_button_refs["Resolved"] = resolved_btn
        
        rejected_btn = ft.ElevatedButton(
            "Rejected",
            on_click=on_filter_changed("Rejected"),
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
            expand=True,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5),
                                 text_style=ft.TextStyle(
                    font_family="Poppins-Bold", size=10)),
        )
        filter_button_refs["Rejected"] = rejected_btn
        
        filter_row = ft.Row(
            [pending_btn, ongoing_btn, resolved_btn, rejected_btn],
            spacing=10,
        )
        
        return filter_row, filter_button_refs
    
    @staticmethod
    def create_empty_state(first_name, is_dark, on_report_click):
        """Create empty state when no reports exist"""
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
                    border=ft.border.all(1, ft.Colors.GREY_300 if not is_dark else ft.Colors.GREY_700),
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=40, vertical=20),
                ),
            ],
            spacing=0,
        )
    
    @staticmethod
    def create_no_reports_message():
        """Create message when filter returns no results"""
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
        """Create floating action button"""
        return ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=on_click,
            bgcolor="#062C80"
        )