import flet as ft


class DashboardState:
    def __init__(self):
        self.category_status_filter = "All"  # Track which status filter is selected for categories
        self.stats_row = ft.Row(spacing=12, wrap=False, scroll=ft.ScrollMode.AUTO)
        self.category_filter_buttons = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO, tight=True)
        self.category_list_view = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)


class DashboardController:
    def __init__(self, page, user_data, state, data_manager, ui_components):
        self.page = page
        self.user_data = user_data
        self.state = state
        self.data_manager = data_manager
        self.ui_components = ui_components
    
    def handle_tab_click(self, tab_name):
        
        from .admin_category_reports import admin_category_reports
        admin_category_reports(self.page, self.user_data, status=tab_name)
    
    def handle_category_filter_click(self, status_filter):
        
        self.state.category_status_filter = status_filter
        self.refresh_dashboard()
    
    def handle_category_click(self, category_name, status_filter="All"):
        
        from .admin_category_reports import admin_category_reports
        admin_category_reports(self.page, self.user_data, category=category_name, status=status_filter)
    
    def update_stats_and_tabs(self, reports, counts):
        self.state.stats_row.controls.clear()
        self.state.stats_row.controls.extend([
            self.ui_components.create_stat_card("Pending", counts["pending"], "#FFE5D9", "#FF6B35"),
            self.ui_components.create_stat_card("On Going", counts["on going"], "#FFF9E6", "#FFC107"),
            self.ui_components.create_stat_card("Fixed", counts["fixed"], "#E8F5E9", "#4CAF50"),
            self.ui_components.create_stat_card("Rejected", counts["rejected"], "#FFEBEE", "#F44336"),
        ])
    
    def update_category_filter_buttons(self, reports, counts):
        #build category filter buttons by status
        self.state.category_filter_buttons.controls.clear()
        
        # Add "All" button
        all_button = ft.TextButton(
            content=self.ui_components.create_tab_button(
                "All", len(reports), self.state.category_status_filter == "All"
            ),
            on_click=lambda e: self.handle_category_filter_click("All")
        )
        self.state.category_filter_buttons.controls.append(all_button)
        
        
        status_mapping = {
            "Pending": "pending",
            "On Going": "on going",
            "Fixed": "fixed",
            "Rejected": "rejected"
        }
        
        for label, count_key in status_mapping.items():
            status_count = counts.get(count_key, 0)
            btn = ft.TextButton(
                content=self.ui_components.create_tab_button(
                    label, status_count, self.state.category_status_filter == label
                ),
                on_click=lambda e, s=label: self.handle_category_filter_click(s)
            )
            self.state.category_filter_buttons.controls.append(btn)
    
    def update_category_cards(self, reports):
        
        self.state.category_list_view.controls.clear()
        
        
        filtered_reports = reports
        if self.state.category_status_filter != "All":
            filtered_reports = [r for r in reports if r.get('status') == self.state.category_status_filter]
        
        
        top_categories = self.data_manager.get_top_categories(filtered_reports, limit=5)
        
        for category_name, count in top_categories:
            item = self.ui_components.create_category_list_item(
                category_name, 
                count,
                lambda e, cat=category_name, status=self.state.category_status_filter: 
                    self.handle_category_click(cat, status)
            )
            self.state.category_list_view.controls.append(item)
    
    def refresh_dashboard(self):
        
        all_reports = self.data_manager.fetch_all_reports()
        counts = self.data_manager.calculate_status_counts(all_reports)
        
        
        self.update_stats_and_tabs(all_reports, counts)
        
        
        self.update_category_filter_buttons(all_reports, counts)
        
        self.update_category_cards(all_reports)
        
        self.page.update()