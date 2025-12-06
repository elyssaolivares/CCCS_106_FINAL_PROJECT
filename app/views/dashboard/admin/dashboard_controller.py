import flet as ft


class DashboardState:
    def __init__(self):
        self.current_status = "Pending"
        self.stats_row = ft.Row(spacing=12, wrap=False, scroll=ft.ScrollMode.AUTO)
        self.tab_buttons = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO, tight=True)
        self.reports_list = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO)
    
    def set_current_status(self, status):
        self.current_status = status


class DashboardController:
    def __init__(self, page, user_data, state, data_manager, ui_components):
        self.page = page
        self.user_data = user_data
        self.state = state
        self.data_manager = data_manager
        self.ui_components = ui_components
    
    def handle_status_change(self, report_id, new_status):
        self.data_manager.update_report_status(report_id, new_status)
        self.refresh_dashboard(self.state.current_status)
    
    def handle_tab_click(self, tab_name):
        self.state.set_current_status(tab_name)
        self.refresh_dashboard(tab_name)
    
    def update_stats_and_tabs(self, reports, counts):
        self.state.stats_row.controls.clear()
        self.state.stats_row.controls.extend([
            self.ui_components.create_stat_card("Pending", counts["pending"], "#FFE5D9", "#FF6B35"),
            self.ui_components.create_stat_card("On Going", counts["on going"], "#FFF9E6", "#FFC107"),
            self.ui_components.create_stat_card("Fixed", counts["fixed"], "#E8F5E9", "#4CAF50"),
            self.ui_components.create_stat_card("Rejected", counts["rejected"], "#FFEBEE", "#F44336"),
        ])
        
        self.state.tab_buttons.controls.clear()
        self.state.tab_buttons.controls.extend([
            ft.TextButton(
                content=self.ui_components.create_tab_button("Pending", counts["pending"], 
                                                             self.state.current_status == "Pending"),
                on_click=lambda e: self.handle_tab_click("Pending")
            ),
            ft.TextButton(
                content=self.ui_components.create_tab_button("On Going", counts["on going"], 
                                                             self.state.current_status == "On Going"),
                on_click=lambda e: self.handle_tab_click("On Going")
            ),
            ft.TextButton(
                content=self.ui_components.create_tab_button("Fixed", counts["fixed"], 
                                                             self.state.current_status == "Fixed"),
                on_click=lambda e: self.handle_tab_click("Fixed")
            ),
            ft.TextButton(
                content=self.ui_components.create_tab_button("Rejected", counts["rejected"], 
                                                             self.state.current_status == "Rejected"),
                on_click=lambda e: self.handle_tab_click("Rejected")
            ),
        ])
    
    def update_reports_list(self, filtered_reports, status_filter):
        self.state.reports_list.controls.clear()
        
        if not filtered_reports:
            self.state.reports_list.controls.append(
                self.ui_components.create_empty_state(status_filter)
            )
        else:
            for report in filtered_reports:
                self.state.reports_list.controls.append(
                    self.ui_components.create_report_card(report, self.handle_status_change)
                )
    
    def refresh_dashboard(self, status="Pending"):
        all_reports = self.data_manager.fetch_all_reports()
        counts = self.data_manager.calculate_status_counts(all_reports)
        filtered_reports = self.data_manager.filter_reports_by_status(all_reports, status)
        
        self.update_stats_and_tabs(all_reports, counts)
        self.update_reports_list(filtered_reports, status)
        self.page.update()