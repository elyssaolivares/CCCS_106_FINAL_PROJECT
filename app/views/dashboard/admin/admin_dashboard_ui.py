
import flet as ft


class UIComponents:
    @staticmethod
    def create_stat_card(label, count, color_bg, text_color):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=12, weight=ft.FontWeight.W_600, color=text_color),
                    ft.Text(str(count), size=28, weight=ft.FontWeight.BOLD, color=text_color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            bgcolor=color_bg,
            padding=ft.padding.all(16),
            border_radius=10,
            expand=1,
            height=100,
            width=150,
        )
    
    @staticmethod
    def create_tab_button(label, count, active):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(label, size=13, weight=ft.FontWeight.W_600,
                            color=ft.Colors.WHITE if active else ft.Colors.GREY_500),
                    ft.Container(
                        content=ft.Text(str(count), size=11, weight=ft.FontWeight.BOLD,
                                       color=ft.Colors.WHITE if active else ft.Colors.GREY_500),
                        bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE) if active else ft.Colors.with_opacity(0.1, ft.Colors.GREY_500),
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        border_radius=12,
                    ),
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            bgcolor="#062C80" if active else ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=8,
        )
    
    @staticmethod
    def create_report_card(report, on_status_change):
        desc = (report.get('issue_description') or "").strip()
        if len(desc) > 120:
            desc = desc[:120] + "..."
        
        btn_row = ft.Row(
        [
            ft.ElevatedButton(
                "In Progress",
                on_click=lambda e: on_status_change(report.get('id'), "In Progress"),
                bgcolor="#FBE18B",
                color="#C5A026",
                height=20,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=10)
                ),
            ),
            ft.ElevatedButton(
                "Resolved",
                on_click=lambda e: on_status_change(report.get('id'), "Resolved"),
                bgcolor="#87EC8A",
                color="#427D44",
                height=20,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=10)
                ),
            ),
            ft.ElevatedButton(
                "Rejected",
                on_click=lambda e: on_status_change(report.get('id'), "Rejected"),
                bgcolor="#FE8F89",
                color="#87322D",
                height=20,
                style=ft.ButtonStyle(
                    text_style=ft.TextStyle(size=10)
                ),
            ),
        ],
        spacing=8,
        wrap=True,
    )

        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(f"#{report.get('id')}", size=11, weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.BLUE_700,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4,
                            ),
                            ft.Text(desc, size=13, font_family="Poppins-SemiBold",
                                    color=ft.Colors.WHITE, expand=True),
                        ],
                        spacing=10,
                    ),
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.PLACE, size=16, color=ft.Colors.WHITE),
                            ft.Text(report.get('location') or '-', size=12, color=ft.Colors.WHITE, expand=True),
                        ],
                        spacing=6,
                    ),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.WHITE),
                            ft.Text(report.get('user_name') or report.get('user_email') or '-', 
                                   size=12, color=ft.Colors.WHITE, expand=True),
                        ],
                        spacing=6,
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(report.get('status'), size=10, weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.AMBER_700,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                border_radius=4,
                            ),
                            ft.Container(
                                content=ft.Text(report.get('category','Uncategorized'), size=10),
                                bgcolor=ft.Colors.BLUE_GREY_700,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                border_radius=4,
                            ),
                        ],
                        spacing=8,
                    ),
                    btn_row
                ],
                spacing=10,
                tight=True,
            ),
            padding=ft.padding.all(16),
            bgcolor="#062C80",
            border_radius=10,
            margin=ft.margin.only(bottom=12),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        )
    
    @staticmethod
    def create_empty_state(status_filter):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.INBOX_OUTLINED, size=64, color=ft.Colors.GREY_600),
                    ft.Container(height=10),
                    ft.Text("No reports found", size=16, weight=ft.FontWeight.BOLD, 
                           color=ft.Colors.GREY_500),
                    ft.Text(f"There are no {status_filter.lower()} reports at the moment.", 
                           size=13, color=ft.Colors.GREY_600),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                tight=True,
            ),
            padding=ft.padding.all(40),
            alignment=ft.alignment.center,
        )
    
    @staticmethod
    def create_header(is_dark, on_menu_click):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text("Admin Dashboard", size=20, font_family="Poppins-Bold",
                            color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK),
                    ft.IconButton(icon=ft.Icons.MENU,
                                  icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                                  on_click=on_menu_click),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, 2)
            ),
        )

    @staticmethod
    def create_page_header(is_dark, title, on_back, on_menu):
        """Create header for subpages with back button"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                        on_click=lambda e: on_back(),
                    ),
                    ft.Text(
                        title,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                        on_click=on_menu,
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
    
    @staticmethod
    def create_category_list_item(category_name, count, on_click):
        """Create full-width category list item"""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        category_name,
                        size=14,
                        font_family="Poppins-Bold",
                        color=ft.Colors.BLACK,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(
                            str(count),
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        bgcolor="#EE7738",
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        border_radius=16,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            bgcolor=ft.Colors.with_opacity(0.1, "#062C80"),
            border_radius=8,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            on_click=on_click,
        )
    
    @staticmethod
    def create_category_card(category_name, count, on_click):
        return ft.GestureDetector(
            on_tap=on_click,
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            f"{category_name}",
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.WHITE,
                            max_lines=2,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Container(height=6),
                        ft.Text(
                            f"({count})",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.AMBER_300,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    tight=True,
                ),
                bgcolor="#4A7BA7",
                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                border_radius=8,
                border=ft.border.all(2, ft.Colors.with_opacity(0.4, ft.Colors.BLUE_300)),
            )
        )
    
    @staticmethod
    def create_empty_category_message(category_name=None):
        """Create empty state for category view"""
        return ft.Column(
            [
                ft.Icon(ft.Icons.INBOX_OUTLINED, size=64, color=ft.Colors.GREY_600),
                ft.Container(height=10),
                ft.Text("No reports found", size=16, weight=ft.FontWeight.BOLD,
                       color=ft.Colors.GREY_500),
                ft.Text(
                    f"There are no reports in this category." if category_name else "No categories found",
                    size=13, color=ft.Colors.GREY_600
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )

