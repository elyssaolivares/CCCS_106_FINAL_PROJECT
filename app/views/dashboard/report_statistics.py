class ReportStatistics:
    def __init__(self, reports):
        self.reports = reports if reports else []
    
    def get_total_issues(self):
        
        return len(self.reports)
    
    def get_resolved_issues(self):
        
        return len([r for r in self.reports if r.get('status') == 'Resolved'])
    
    def get_pending_reports(self):
        
        return [r for r in self.reports if r.get('status') == 'Pending']
    
    def get_ongoing_reports(self):
        
        return [r for r in self.reports if r.get('status') == 'In Progress']
    
    def get_resolved_reports(self):
        
        return [r for r in self.reports if r.get('status') == 'Resolved']
    
    def get_rejected_reports(self):
        
        return [r for r in self.reports if r.get('status') == 'Rejected']
    
    def get_filtered_reports(self, filter_type):
        
        filter_map = {
            "Pending": self.get_pending_reports,
            "In Progress": self.get_ongoing_reports,
            "Resolved": self.get_resolved_reports,
            "Rejected": self.get_rejected_reports,
            "All": lambda: self.reports
        }
        return filter_map.get(filter_type, lambda: self.reports)()