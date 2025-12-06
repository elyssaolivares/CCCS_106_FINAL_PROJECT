from app.services.database.database import db


class StatusNormalizer:
    @staticmethod
    def normalize(status_string):
        return (status_string or "").strip().lower().replace("-", " ").replace("_", " ")


class DataManager:
    @staticmethod
    def fetch_all_reports():
        return db.get_all_reports() or []
    
    @staticmethod
    def update_report_status(report_id, new_status):
        db.update_report_status(report_id, new_status)
    
    @staticmethod
    def calculate_status_counts(reports):
        counts = {
            "pending": 0,
            "on going": 0,
            "fixed": 0,
            "rejected": 0
        }
        for report in reports:
            normalized = StatusNormalizer.normalize(report.get('status'))
            if "pending" in normalized:
                counts["pending"] += 1
            elif "on going" in normalized or "ongoing" in normalized:
                counts["on going"] += 1
            elif "fixed" in normalized:
                counts["fixed"] += 1
            elif "reject" in normalized:
                counts["rejected"] += 1
        return counts
    
    @staticmethod
    def filter_reports_by_status(reports, status_filter):
        target = StatusNormalizer.normalize(status_filter)
        return [r for r in reports if target in StatusNormalizer.normalize(r.get('status'))]
    
    @staticmethod
    def calculate_category_counts(reports):
        
        counts = {}
        for report in reports:
            category = report.get('category', 'Uncategorized')
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    @staticmethod
    def get_top_categories(reports, limit=5):
        """Get top N categories by report count"""
        category_counts = DataManager.calculate_category_counts(reports)
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_categories[:limit]
    
    @staticmethod
    def filter_reports_by_category(reports, category):
        
        if not category or category == "All":
            return reports
        return [r for r in reports if r.get('category', 'Uncategorized') == category]

