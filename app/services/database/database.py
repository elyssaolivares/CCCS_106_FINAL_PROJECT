import sqlite3

class Database:
    def __init__(self, db_name="app_database.db"):
        
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                user_name TEXT NOT NULL,
                user_type TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT DEFAULT 'Uncategorized',
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        cursor.execute("PRAGMA table_info(reports)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'category' not in columns:
            cursor.execute('ALTER TABLE reports ADD COLUMN category TEXT DEFAULT "Uncategorized"')
        
        conn.commit()
        conn.close()
        
        try:
            self.migrate_statuses_to_canonical()
        except Exception:
            pass
    
    def add_report(self, user_email, user_name, user_type, issue_description, location, category="Uncategorized"):
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (user_email, user_name, user_type, issue_description, location, category, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_email, user_name, user_type, issue_description, location, category, 'pending'))
        
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id
    
    def get_all_reports(self):
        """Get all reports"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_email, user_name, user_type, issue_description, 
                   location, category, status
            FROM reports
            ORDER BY id DESC
        ''')
        
        reports = cursor.fetchall()
        conn.close()
        
        def _canon(s):
            if not s:
                return 'Pending'
            s = s.strip().lower()
            if 'pending' in s:
                return 'Pending'
            if 'on going' in s or 'ongoing' in s or 'in progress' in s:
                return 'In Progress'
            if 'fixed' in s or 'resolved' in s:
                return 'Resolved'
            if 'reject' in s or 'rejected' in s:
                return 'Rejected'
            return str(s).title()

        report_list = []
        for report in reports:
            report_list.append({
                'id': report[0],
                'user_email': report[1],
                'user_name': report[2],
                'user_type': report[3],
                'issue_description': report[4],
                'location': report[5],
                'category': report[6],
                'status': _canon(report[7])
            })

        return report_list
    
    def get_reports_by_user(self, user_email):
        """Get all reports by a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_email, user_name, user_type, issue_description, 
                   location, category, status
            FROM reports
            WHERE user_email = ?
            ORDER BY id DESC
        ''', (user_email,))
        
        reports = cursor.fetchall()
        conn.close()
        
        def _canon(s):
            if not s:
                return 'Pending'
            s = s.strip().lower()
            if 'pending' in s:
                return 'Pending'
            if 'on going' in s or 'ongoing' in s or 'in progress' in s:
                return 'In Progress'
            if 'fixed' in s or 'resolved' in s:
                return 'Resolved'
            if 'reject' in s or 'rejected' in s:
                return 'Rejected'
            return str(s).title()

        report_list = []
        for report in reports:
            report_list.append({
                'id': report[0],
                'user_email': report[1],
                'user_name': report[2],
                'user_type': report[3],
                'issue_description': report[4],
                'location': report[5],
                'category': report[6],
                'status': _canon(report[7])
            })

        return report_list
    
    def get_reports_by_category(self, category):
        """Get all reports by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_email, user_name, user_type, issue_description, 
                   location, category, status
            FROM reports
            WHERE category = ?
            ORDER BY id DESC
        ''', (category,))
        
        reports = cursor.fetchall()
        conn.close()

        def _canon(s):
            if not s:
                return 'Pending'
            s = s.strip().lower()
            if 'pending' in s:
                return 'Pending'
            if 'on going' in s or 'ongoing' in s or 'in progress' in s:
                return 'In Progress'
            if 'fixed' in s or 'resolved' in s:
                return 'Resolved'
            if 'reject' in s or 'rejected' in s:
                return 'Rejected'
            return str(s).title()

        report_list = []
        for report in reports:
            report_list.append({
                'id': report[0],
                'user_email': report[1],
                'user_name': report[2],
                'user_type': report[3],
                'issue_description': report[4],
                'location': report[5],
                'category': report[6],
                'status': _canon(report[7])
            })

        return report_list

    def get_report_by_id(self, report_id):
        """Return a single report dict by id or None if not found."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, user_email, user_name, user_type, issue_description,
                   location, category, status
            FROM reports
            WHERE id = ?
            LIMIT 1
        ''', (report_id,))

        r = cursor.fetchone()
        conn.close()

        if not r:
            return None

        def _canon(s):
            if not s:
                return 'Pending'
            s = s.strip().lower()
            if 'pending' in s:
                return 'Pending'
            if 'on going' in s or 'ongoing' in s or 'in progress' in s:
                return 'In Progress'
            if 'fixed' in s or 'resolved' in s:
                return 'Resolved'
            if 'reject' in s or 'rejected' in s:
                return 'Rejected'
            return str(s).title()

        return {
            'id': r[0],
            'user_email': r[1],
            'user_name': r[2],
            'user_type': r[3],
            'issue_description': r[4],
            'location': r[5],
            'category': r[6],
            'status': _canon(r[7])
        }
    
    def update_report_status(self, report_id, new_status):
        
        conn = self.get_connection()
        cursor = conn.cursor()
        ns = (new_status or '').strip().lower()
        if 'pending' in ns:
            ns = 'pending'
        elif 'on going' in ns or 'ongoing' in ns or 'in progress' in ns:
            ns = 'in progress'
        elif 'fixed' in ns or 'resolved' in ns:
            ns = 'resolved'
        elif 'reject' in ns or 'rejected' in ns:
            ns = 'rejected'

        cursor.execute('''
            UPDATE reports
            SET status = ?
            WHERE id = ?
        ''', (ns, report_id))
        
        conn.commit()
        conn.close()
    
    def migrate_statuses_to_canonical(self):
        """Normalize existing status values in DB to canonical lowercase values."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, status FROM reports')
        rows = cursor.fetchall()

        def _canon_val(s):
            if not s:
                return 'pending'
            s0 = s.strip().lower()
            if 'pending' in s0:
                return 'pending'
            if 'on going' in s0 or 'ongoing' in s0 or 'in progress' in s0:
                return 'in progress'
            if 'fixed' in s0 or 'resolved' in s0:
                return 'resolved'
            if 'reject' in s0 or 'rejected' in s0:
                return 'rejected'
            return s0

        for r in rows:
            rid, val = r
            canon = _canon_val(val)
            if canon != (val or '').strip().lower():
                cursor.execute('UPDATE reports SET status = ? WHERE id = ?', (canon, rid))

        conn.commit()
        conn.close()
    
    def update_report(self, report_id, issue_description, location):
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reports
            SET issue_description = ?, location = ?
            WHERE id = ?
        ''', (issue_description, location, report_id))
        
        conn.commit()
        conn.close()
    
    def delete_report(self, report_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM reports WHERE id = ?', (report_id,))
        
        conn.commit()
        conn.close()
    
    def user_exists(self, user_email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM reports WHERE user_email = ? LIMIT 1', (user_email,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

db = Database()
