import flet as ft
from app.services.database.database import db
from .session_manager import SessionManager
from .navigation_drawer import NavigationDrawerComponent


def admin_reports(page: ft.Page, user_data=None):
    page.controls.clear()
    page.floating_action_button = None
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    if not user_data:
        from app.views.loginpage import loginpage
        loginpage(page)
        return
    
    is_dark = SessionManager.get_theme_preference(page)
    current_tab = {"status": "Pending"}
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        admin_reports(page, user_data)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    
    # Header
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "All Reports",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                ),
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                    on_click=nav_drawer.open_drawer,
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
    
    # Get all reports from database
    all_reports = db.get_all_reports()
    
    # Reports list container
    reports_list = ft.Column(spacing=10, expand=True)
    
    # Create tab buttons
    def create_tab_button(label, count, is_active):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        label,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE if is_active else ft.Colors.GREY_600,
                    ),
                    ft.Text(
                        str(count),
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.WHITE if is_active else ft.Colors.GREY_600,
                    ),
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor="#062C80" if is_active else ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            border_radius=ft.border_radius.only(top_left=5, top_right=5) if is_active else 0,
            alignment=ft.alignment.center,
        )
    
    tab_buttons = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO)
    
    def update_tabs():
        tab_buttons.controls.clear()
        
        pending_reports = [r for r in all_reports if r['status'] == 'Pending']
        ongoing_reports = [r for r in all_reports if r['status'] == 'In Progress']
        fixed_reports = [r for r in all_reports if r['status'] == 'Resolved']
        rejected_reports = [r for r in all_reports if r['status'] == 'Rejected']
        
        pending_btn = ft.TextButton(
            content=create_tab_button("Pending", len(pending_reports), current_tab["status"] == "Pending"),
            on_click=lambda e: switch_tab("Pending"),
        )
        ongoing_btn = ft.TextButton(
            content=create_tab_button("In Progress", len(ongoing_reports), current_tab["status"] == "In Progress"),
            on_click=lambda e: switch_tab("In Progress"),
        )
        fixed_btn = ft.TextButton(
            content=create_tab_button("Resolved", len(fixed_reports), current_tab["status"] == "Resolved"),
            on_click=lambda e: switch_tab("Resolved"),
        )
        rejected_btn = ft.TextButton(
            content=create_tab_button("Rejected", len(rejected_reports), current_tab["status"] == "Rejected"),
            on_click=lambda e: switch_tab("Rejected"),
        )
        
        tab_buttons.controls.extend([pending_btn, ongoing_btn, fixed_btn, rejected_btn])
        page.update()
    
    def switch_tab(tab_name):
        current_tab["status"] = tab_name
        update_tabs()
        update_reports_list(tab_name)
    
    def update_reports_list(status_filter="Pending"):
        reports_list.controls.clear()
        
        filtered_reports = [r for r in all_reports if r['status'] == status_filter]
        
        if not filtered_reports:
            # Empty state
            reports_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                size=48,
                                color=ft.Colors.GREY_400,
                            ),
                            ft.Text(
                                "No reported issues yet.",
                                size=14,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.GREY_100 if not is_dark else ft.Colors.GREY_800,
                    border_radius=10,
                    border=ft.border.all(2, ft.Colors.BLUE_400),
                    height=200,
                )
            )
        else:
            # Display all reports for the selected status
            for report in filtered_reports:
                description = report['issue_description'] or ""
                if len(description) > 120:
                    description = description[:120] + "..."

                report_card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"#{report['id']}",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.GREY_300,
                                    ),
                                    ft.Container(width=8),
                                    ft.Text(
                                        description,
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                                        expand=True,
                                        max_lines=2,
                                    ),
                                ],
                            ),
                            ft.Container(height=8),
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.PLACE, size=16, color=ft.Colors.GREY_400),
                                    ft.Container(width=6),
                                    ft.Text(f"{report['location']}", size=11, color=ft.Colors.GREY_500 if is_dark else ft.Colors.GREY_700),
                                    ft.Container(width=20),
                                    ft.Icon(ft.Icons.PERSON, size=16, color=ft.Colors.GREY_400),
                                    ft.Container(width=6),
                                    ft.Text(f"{report['user_name']}", size=11, color=ft.Colors.GREY_500 if is_dark else ft.Colors.GREY_700),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            ft.Container(height=6),
                            ft.Row(
                                [
                                    ft.Text(f"Status: {report['status']}", size=11, color=ft.Colors.AMBER_300),
                                    ft.Container(width=12),
                                    ft.Text(f"Category: {report.get('category','Uncategorized')}", size=11, color=ft.Colors.GREY_500 if is_dark else ft.Colors.GREY_700),
                                ]
                            )
                        ],
                        spacing=6,
                    ),
                    padding=ft.padding.all(12),
                    bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.GREY_50,
                    border_radius=10,
                    margin=ft.margin.only(bottom=8),
                )

                reports_list.controls.append(report_card)

        page.update()
    
    # Main content (no stats row)
    main_content = ft.Column(
        [
            ft.Text(
                "Reports",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
            ),
            ft.Container(height=15),
            tab_buttons,
            ft.Container(height=20),
            ft.Container(
                content=reports_list,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
    
    main_container = ft.Container(
        content=main_content,
        padding=ft.padding.symmetric(horizontal=20, vertical=20),
    )
    
    responsive_wrapper = ft.Column(
        [
            header,
            ft.Container(
                content=main_container,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
    
    # Initialize
    update_tabs()
    update_reports_list("Pending")
    
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_900 if is_dark else ft.Colors.WHITE
    page.end_drawer = drawer
    page.add(responsive_wrapper)
    page.update()
