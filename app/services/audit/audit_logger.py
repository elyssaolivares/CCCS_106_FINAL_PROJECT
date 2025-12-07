import sqlite3
from datetime import datetime

class AuditLogger:
    def __init__(self, db_path="app_database.db"):
        self.db_path = db_path
        self._init_audit_table()
    
    def _init_audit_table(self):
        """Initialize audit_logs table if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_email TEXT NOT NULL,
                actor_name TEXT,
                action_type TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'success'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_action(self, actor_email, actor_name, action_type, resource_type=None, resource_id=None, details=None, status="success"):
        """Log an audit entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_logs (actor_email, actor_name, action_type, resource_type, resource_id, details, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (actor_email, actor_name, action_type, resource_type, resource_id, details, status))
        
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return log_id
    
    def get_audit_logs(self, actor_email=None, action_type=None, resource_type=None, start_date=None, end_date=None, limit=100, offset=0):
        """Retrieve audit logs with optional filters."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT id, actor_email, actor_name, action_type, resource_type, resource_id, details, timestamp, status FROM audit_logs WHERE 1=1"
        params = []
        
        if actor_email:
            query += " AND actor_email = ?"
            params.append(actor_email)
        if action_type:
            query += " AND action_type = ?"
            params.append(action_type)
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        conn.close()
        
        return [{
            'id': log[0],
            'actor_email': log[1],
            'actor_name': log[2],
            'action_type': log[3],
            'resource_type': log[4],
            'resource_id': log[5],
            'details': log[6],
            'timestamp': log[7],
            'status': log[8]
        } for log in logs]
    
    def get_audit_logs_count(self, actor_email=None, action_type=None, resource_type=None, start_date=None, end_date=None):
        """Get total count of audit logs matching filters."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM audit_logs WHERE 1=1"
        params = []
        
        if actor_email:
            query += " AND actor_email = ?"
            params.append(actor_email)
        if action_type:
            query += " AND action_type = ?"
            params.append(action_type)
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count


audit_logger = AuditLogger()
