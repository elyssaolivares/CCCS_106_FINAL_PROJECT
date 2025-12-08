"""User Activity Monitoring Dashboard - displays login history, failed attempts, geo-location."""

import flet as ft
from datetime import datetime, timedelta
from app.services.activity.activity_monitor import activity_monitor


def user_activity_monitoring_page(page: ft.Page, user_data=None):
    page.controls.clear()
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    if not user_data or user_data.get("type", "").lower() != "admin":
        page.snack_bar = ft.SnackBar(ft.Text("Access Denied: Admin only"))
        page.snack_bar.open = True
        page.update()
        return
    
    is_dark = page.session.get("is_dark_theme") or False
    
    from app.views.dashboard.session_manager import SessionManager
    from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        user_activity_monitoring_page(page, user_data)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    page.end_drawer = drawer
    
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "User Activity Monitoring",
                    size=20,
                    font_family="Poppins-Bold",
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                ),
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=ft.Colors.BLACK,
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
    
    # Main content container - will hold different views
    main_view_container = ft.Container(expand=True)
    
    # === TAB 1: All Users Stats ===
    all_users_list = ft.ListView(expand=True, spacing=10)
    
    def load_all_users_stats():
        all_users_list.controls.clear()
        all_stats = activity_monitor.get_all_user_stats(limit=50)
        
        if not all_stats:
            all_users_list.controls.append(
                ft.Text("No user activity data available", color=ft.Colors.GREY)
            )
        else:
            for stat in all_stats:
                last_login_str = stat['last_login'] if stat['last_login'] else "Never"
                last_failed_str = stat['last_failed_attempt'] if stat['last_failed_attempt'] else "Never"
                
                card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.Text(stat['email'], size=12, font_family="Poppins-Bold"),
                                            ft.Text(stat['last_login_location'] or "Unknown", 
                                                   size=11, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=4,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text(f"Logins: {stat['total_logins']}", size=11),
                                            ft.Text(f"Failed: {stat['total_failed_attempts']}", 
                                                   size=11, 
                                                   color=ft.Colors.RED if stat['total_failed_attempts'] > 0 else ft.Colors.GREEN),
                                        ],
                                        spacing=4,
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                expand=True,
                            ),
                            ft.Divider(height=1),
                            ft.Row(
                                [
                                    ft.Text(f"Last Login: {last_login_str}", size=10, color=ft.Colors.GREY),
                                    ft.Text(f"IP: {stat['last_login_ip'] or 'N/A'}", size=10, color=ft.Colors.GREY),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.all(12),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    border_radius=8,
                )
                all_users_list.controls.append(card)
        
        page.update()
    
    all_users_view = ft.Container(
        content=all_users_list,
        expand=True,
        padding=ft.padding.all(15),
    )
    
    # === TAB 2: User Activity Details ===
    search_email = ft.TextField(
        label="Search User Email",
        width=300,
        border_color="#062C80",
        focused_border_color="#093AA5",
    )
    
    activity_list = ft.ListView(expand=True, spacing=8)
    stats_display = ft.Column(spacing=10)
    
    def load_user_activity(email):
        activity_list.controls.clear()
        stats_display.controls.clear()
        
        # Get and display stats
        stats = activity_monitor.get_user_stats(email)
        if stats:
            last_login = stats['last_login'] if stats['last_login'] else "Never"
            
            stats_display.controls.extend([
                ft.Text(f"Email: {stats['email']}", size=12, font_family="Poppins-Bold"),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Column([
                                ft.Text("Total Logins", size=11, color=ft.Colors.GREY),
                                ft.Text(str(stats['total_logins']), size=14, font_family="Poppins-Bold"),
                            ]),
                            ft.Column([
                                ft.Text("Failed Attempts", size=11, color=ft.Colors.GREY),
                                ft.Text(str(stats['total_failed_attempts']), size=14, 
                                       font_family="Poppins-Bold", 
                                       color=ft.Colors.RED if stats['total_failed_attempts'] > 0 else ft.Colors.GREEN),
                            ]),
                            ft.Column([
                                ft.Text("Last Login", size=11, color=ft.Colors.GREY),
                                ft.Text(last_login[:10] if last_login != "Never" else "Never", size=12),
                            ]),
                        ],
                        spacing=30,
                    ),
                    padding=ft.padding.all(12),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    border_radius=8,
                ),
                ft.Text("Location Info", size=12, font_family="Poppins-Bold"),
                ft.Text(f"Last IP: {stats['last_login_ip'] or 'N/A'}", size=11),
                ft.Text(f"Last Location: {stats['last_login_location'] or 'Unknown'}", size=11),
            ])
        
        # Get activity history
        activities = activity_monitor.get_user_activity(email, limit=50)
        
        if not activities:
            activity_list.controls.append(
                ft.Text("No activity history", color=ft.Colors.GREY)
            )
        else:
            for activity in activities:
                status_color = ft.Colors.GREEN if activity['status'] == 'success' else ft.Colors.RED
                
                details_text = ft.Text(f"Details: {activity['details']}", size=9, color=ft.Colors.GREY) if activity['details'] else None
                
                activity_card_controls = [
                    ft.Row(
                        [
                            ft.Text(activity['type'].upper(), size=11, 
                                   font_family="Poppins-Bold", color=status_color),
                            ft.Text(activity['timestamp'][-8:] if activity['timestamp'] else "", 
                                   size=10, color=ft.Colors.GREY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(f"IP: {activity['ip'] or 'N/A'}", size=10),
                    ft.Text(f"Location: {activity['city']}, {activity['country']}", size=10),
                    ft.Text(f"ISP: {activity['isp']}", size=10),
                ]
                
                if details_text:
                    activity_card_controls.append(details_text)
                
                activity_card = ft.Container(
                    content=ft.Column(
                        activity_card_controls,
                        spacing=6,
                    ),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    border_radius=8,
                )
                activity_list.controls.append(activity_card)
        
        page.update()
    
    def on_search_click(e):
        email = search_email.value.strip()
        if not email:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter an email"))
            page.snack_bar.open = True
            page.update()
            return
        load_user_activity(email)
    
    user_detail_view = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        search_email,
                        ft.IconButton(
                            icon=ft.Icons.SEARCH,
                            on_click=on_search_click,
                            tooltip="Search user activity",
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(),
                ft.Container(
                    content=stats_display,
                    bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE) if is_dark else ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
                    padding=ft.padding.all(12),
                    border_radius=8,
                ),
                ft.Text("Activity History", size=12, font_family="Poppins-Bold"),
                ft.Container(
                    content=activity_list,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=12,
        ),
        padding=ft.padding.all(15),
        expand=True,
    )
    
    # === TAB 3: Failed Attempts ===
    failed_attempts_list = ft.ListView(expand=True, spacing=8)
    failed_search_email = ft.TextField(
        label="Search User Email for Failed Attempts",
        width=300,
        border_color="#062C80",
        focused_border_color="#062C805",
    )
    
    def load_failed_attempts(email):
        failed_attempts_list.controls.clear()
        
        attempts = activity_monitor.get_failed_attempts(email, limit=50)
        
        if not attempts:
            failed_attempts_list.controls.append(
                ft.Text("No failed attempts recorded", color=ft.Colors.GREEN)
            )
        else:
            for attempt in attempts:
                attempt_card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text("Failed Login Attempt", size=11, 
                                           font_family="Poppins-Bold", color=ft.Colors.RED),
                                    ft.Text(attempt['timestamp'][-8:] if attempt['timestamp'] else "", 
                                           size=10, color=ft.Colors.GREY),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(f"Email: {attempt['email']}", size=10),
                            ft.Text(f"IP: {attempt['ip']}", size=10),
                            ft.Text(f"Location: {attempt['location']}", size=10),
                            ft.Text(f"Reason: {attempt['reason']}", size=10, color=ft.Colors.ORANGE),
                        ],
                        spacing=6,
                    ),
                    padding=ft.padding.all(10),
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.RED) if is_dark else ft.Colors.with_opacity(0.05, ft.Colors.RED),
                    border_radius=8,
                )
                failed_attempts_list.controls.append(attempt_card)
        
        page.update()
    
    def on_failed_search_click(e):
        email = failed_search_email.value.strip()
        if not email:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter an email"))
            page.snack_bar.open = True
            page.update()
            return
        load_failed_attempts(email)
    
    failed_attempts_view = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        failed_search_email,
                        ft.IconButton(
                            icon=ft.Icons.SEARCH,
                            on_click=on_failed_search_click,
                            tooltip="Search failed attempts",
                        ),
                    ],
                    spacing=10,
                ),
                ft.Divider(),
                ft.Container(
                    content=failed_attempts_list,
                    expand=True,
                ),
            ],
            expand=True,
            spacing=12,
        ),
        padding=ft.padding.all(15),
        expand=True,
    )
    
    # Navigation buttons to switch views
    def show_all_users(e):
        main_view_container.content = all_users_view
        load_all_users_stats()
        btn_all_users.style = ft.ButtonStyle(color="#062C80")
        btn_user_details.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_failed_attempts.style = ft.ButtonStyle(color=ft.Colors.GREY)
        page.update()
    
    def show_user_details(e):
        main_view_container.content = user_detail_view
        btn_all_users.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_user_details.style = ft.ButtonStyle(color="#062C80")
        btn_failed_attempts.style = ft.ButtonStyle(color=ft.Colors.GREY)
        page.update()
    
    def show_failed_attempts(e):
        main_view_container.content = failed_attempts_view
        btn_all_users.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_user_details.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_failed_attempts.style = ft.ButtonStyle(color="#062C80")
        page.update()
    
    btn_all_users = ft.TextButton(
        "All Users",
        on_click=show_all_users,
        style=ft.ButtonStyle(color="#062C80"),
    )
    btn_user_details = ft.TextButton(
        "User Details",
        on_click=show_user_details,
        style=ft.ButtonStyle(color=ft.Colors.GREY),
    )
    btn_failed_attempts = ft.TextButton(
        "Failed Attempts",
        on_click=show_failed_attempts,
        style=ft.ButtonStyle(color=ft.Colors.GREY),
    )
    
    nav_bar = ft.Row(
        [btn_all_users, btn_user_details, btn_failed_attempts],
        spacing=10,
    )
    
    # Initialize with all users view
    main_view_container.content = all_users_view
    load_all_users_stats()
    
    # Main layout
    main_content = ft.Column(
        [
            header,
            ft.Container(height=20),
            nav_bar,
            ft.Container(height=10),
            ft.Divider(height=1),
            main_view_container,
        ],
        expand=True,
        spacing=10,
    )
    
    page.add(main_content)
