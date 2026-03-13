"""User Activity Monitoring Dashboard - displays login history, failed attempts, geo-location."""

import flet as ft
from datetime import datetime, timedelta
from app.services.activity.activity_monitor import activity_monitor
from .admin_sidebar import create_admin_sidebar

# ── Palette ──
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_WHITE = "#FFFFFF"

_SIDEBAR_BREAKPOINT = 768


def user_activity_monitoring_page(page: ft.Page, user_data=None):
    page.controls.clear()
    page.overlay.clear()
    page.floating_action_button = None
    page.end_drawer = None
    page.drawer = None
    page.scroll = None
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    if not user_data or user_data.get("type", "").lower() != "admin":
        page.snack_bar = ft.SnackBar(ft.Text("Access Denied: Admin only"))
        page.snack_bar.open = True
        page.update()
        return
    
    is_dark = page.session.get("is_dark_theme") or False
    is_mobile = not (page.width and page.width >= _SIDEBAR_BREAKPOINT)
    # Resolve palette from theme
    from app.theme import get_colors as _get_theme
    _t = _get_theme(page)
    _BG = _t["BG"]; _NAVY = _t["NAVY"]; _NAVY_MUTED = _t["NAVY_MUTED"]
    _ACCENT = _t["ACCENT"]; _WHITE = _t["WHITE"]
    _BORDER = _t["BORDER"]; _BORDER_LIGHT = _t["BORDER_LIGHT"]

    from app.views.dashboard.session_manager import SessionManager
    from app.views.dashboard.navigation_drawer import NavigationDrawerComponent
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        user_activity_monitoring_page(page, user_data)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)

    # ── Admin sidebar ──
    sidebar, _ = create_admin_sidebar(page, user_data, active_key="activity", on_toggle_theme=toggle_dark_theme)
    sidebar_wrapper = ft.Container(content=sidebar, visible=not is_mobile)

    def go_back(e=None):
        from .admin_dashboard import admin_dashboard
        admin_dashboard(page, user_data)

    def on_menu_click(e):
        if drawer:
            drawer.open = True
            page.update()
    
    header = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK_ROUNDED,
                            icon_color=_NAVY, icon_size=20,
                            on_click=go_back,
                        ),
                        ft.Text(
                            "User Activity Monitoring",
                            size=18 if is_mobile else 20,
                            font_family="Poppins-Bold",
                            color=_NAVY,
                        ),
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.IconButton(
                        ft.Icons.MENU_ROUNDED, icon_color=_NAVY, icon_size=20,
                        on_click=on_menu_click,
                    ),
                    width=36, height=36, border_radius=10,
                    bgcolor=_BORDER_LIGHT, alignment=ft.alignment.center,
                    visible=is_mobile,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=16 if is_mobile else 28, vertical=14),
        bgcolor=_WHITE,
        border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
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
        border_color="#0F2B5B",
        focused_border_color="#1565C0",
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
        border_color="#0F2B5B",
        focused_border_color="#0F2B5B",
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
        btn_all_users.style = ft.ButtonStyle(color="#0F2B5B")
        btn_user_details.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_failed_attempts.style = ft.ButtonStyle(color=ft.Colors.GREY)
        page.update()
    
    def show_user_details(e):
        main_view_container.content = user_detail_view
        btn_all_users.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_user_details.style = ft.ButtonStyle(color="#0F2B5B")
        btn_failed_attempts.style = ft.ButtonStyle(color=ft.Colors.GREY)
        page.update()
    
    def show_failed_attempts(e):
        main_view_container.content = failed_attempts_view
        btn_all_users.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_user_details.style = ft.ButtonStyle(color=ft.Colors.GREY)
        btn_failed_attempts.style = ft.ButtonStyle(color="#0F2B5B")
        page.update()
    
    btn_all_users = ft.TextButton(
        "All Users",
        on_click=show_all_users,
        style=ft.ButtonStyle(color="#0F2B5B"),
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
    content_area = ft.Container(
        content=ft.Column(
            [
                header,
                ft.Container(
                    content=ft.Column(
                        [
                            nav_bar,
                            ft.Container(height=10),
                            ft.Divider(height=1),
                            main_view_container,
                        ],
                        expand=True,
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(horizontal=12 if is_mobile else 25, vertical=10),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
        bgcolor=_BG,
    )

    # ── Resize handler ──
    def on_resize(e):
        nonlocal is_mobile
        w = page.width or 0
        was_mobile = is_mobile
        is_mobile = w < _SIDEBAR_BREAKPOINT
        if was_mobile != is_mobile:
            sidebar_wrapper.visible = not is_mobile
            page.update()

    page.on_resized = on_resize

    # ── Assemble ──
    page.end_drawer = drawer
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = _BG

    layout = ft.Row(
        [sidebar_wrapper, content_area],
        spacing=0, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    page.add(layout)
