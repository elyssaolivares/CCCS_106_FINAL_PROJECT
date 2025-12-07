class ReportStatistics:
    def __init__(self, reports):
        self.reports = reports if reports else []
    
    def get_total_issues(self):
        
        return len(self.reports)
    
    def get_resolved_issues(self):
        
        return len([r for r in self.reports if self._normalize_status(r.get('status')) == 'Resolved'])
    
    def get_pending_reports(self):
        
        return [r for r in self.reports if self._normalize_status(r.get('status')) == 'Pending']
    
    def get_ongoing_reports(self):
        
        return [r for r in self.reports if self._normalize_status(r.get('status')) == 'In Progress']
    
    def get_resolved_reports(self):
        
        return [r for r in self.reports if self._normalize_status(r.get('status')) == 'Resolved']
    
    def get_rejected_reports(self):
        
        return [r for r in self.reports if self._normalize_status(r.get('status')) == 'Rejected']
    
    def get_filtered_reports(self, filter_type):
        
        filter_map = {
            "Pending": self.get_pending_reports,
            "In Progress": self.get_ongoing_reports,
            "Resolved": self.get_resolved_reports,
            "Rejected": self.get_rejected_reports,
            "All": lambda: self.reports
        }
        return filter_map.get(filter_type, lambda: self.reports)()

    def _normalize_status(self, status):
        """Normalize various legacy status strings to canonical set.

        Canonical statuses: 'Pending', 'In Progress', 'Resolved', 'Rejected'
        """
        if not status:
            return 'Pending'

        s = str(status).strip().lower()
        mapping = {
            'on going': 'In Progress',
            'ongoing': 'In Progress',
            'in progress': 'In Progress',
            'fixed': 'Resolved',
            'resolved': 'Resolved',
            'reject': 'Rejected',
            'rejected': 'Rejected',
            'pending': 'Pending'
        }
        return mapping.get(s, s.title())