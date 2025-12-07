import flet as ft
from .report_issue_page import report_issue_page
from app.services.database.database import db
from .session_manager import SessionManager
from .report_statistics import ReportStatistics
from .navigation_drawer import NavigationDrawerComponent
from .report_card import ReportCard
from .dashboard_ui import DashboardUI

def user_dashboard(page: ft.Page, user_data=None):

    if user_data:
        SessionManager.set_user_data(page, user_data)
    else:
        user_data = SessionManager.validate_session(page)
        if not user_data:
            return
    
    page.controls.clear()
    
    
    full_name = user_data.get("name", "User")
    first_name = full_name.split()[0] if full_name else "User"
    user_email = user_data.get("email")
    user_type = user_data.get("type", "user")
    
    if not user_email:
        page.add(ft.Text("Error: No email found in user data", color=ft.Colors.RED))
        page.update()
        return
    
    
    try:
        if user_type == "admin":
            user_reports = db.get_all_reports()
        else:
            user_reports = db.get_reports_by_user(user_email)
    except Exception as e:
        print(f"Error fetching reports: {e}")
        user_reports = []
    
    if user_reports is None:
        user_reports = []
    
    
    stats = ReportStatistics(user_reports)
    
    
    is_dark = SessionManager.get_theme_preference(page)
    selected_filter = ft.Ref[str]()
    selected_filter.current = "Pending"
    
    
    def report_issue_clicked(e):
        report_issue_page(page, user_data)
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        user_dashboard(page, user_data)
    
   
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    
   
    report_cards_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def update_dashboard():
        
        user_dashboard(page, user_data)
    
    def update_report_list():
        
        report_cards_column.controls.clear()
        
        filtered_reports = stats.get_filtered_reports(selected_filter.current)
        
        if filtered_reports:
            for report in filtered_reports:
                card = ReportCard(page, report, user_data, update_dashboard)
                report_cards_column.controls.append(card.create())
        else:
            report_cards_column.controls.append(DashboardUI.create_no_reports_message())
        
        page.update()
    
    
    def filter_changed(filter_name):
        def handler(e):
            selected_filter.current = filter_name
            
            for btn_name, btn_data in filter_button_refs.items():
                if btn_name == filter_name:
                    btn_data["btn"].bgcolor = "#062C80"
                    btn_data["text"].color = ft.Colors.WHITE
                else:
                    
                    btn_data["btn"].bgcolor = ft.Colors.TRANSPARENT
                    btn_data["text"].color = ft.Colors.GREY_500
            
            page.update()
            update_report_list()
        return handler
    
    filter_buttons, filter_button_refs = DashboardUI.create_filter_buttons(filter_changed)
    
    
    update_report_list()
    
    
    header = DashboardUI.create_header(first_name, user_type, is_dark, nav_drawer.open_drawer)
    
    total_issues = stats.get_total_issues()
    
    if total_issues > 0:
     
        stats_row = DashboardUI.create_statistics_row(total_issues, stats.get_resolved_issues())
        
        main_content = ft.Column(
            [
                stats_row,
                ft.Container(height=10),
                filter_buttons,
                ft.Container(height=10),
                report_cards_column,
            ],
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO
        )
        fab = DashboardUI.create_fab(report_issue_clicked)
    else:
        
        main_content = DashboardUI.create_empty_state(first_name, is_dark, report_issue_clicked)
        fab = None
    
    main_content_container = ft.Container(
        content=main_content,
        padding=20,
        expand=True
    )
    
    
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_900 if is_dark else ft.Colors.WHITE
    page.end_drawer = drawer
    page.floating_action_button = fab
    page.add(ft.Column([header, main_content_container], expand=True, spacing=0))
    page.update()