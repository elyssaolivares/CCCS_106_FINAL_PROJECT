"""
Supabase PostgreSQL Database Module
Replaces SQLite implementation with Supabase PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class Database:
    def __init__(self):
        """Initialize Supabase connection"""
        self.db_config = {
            'host': os.getenv('SUPABASE_DB_HOST'),
            'database': os.getenv('SUPABASE_DB_NAME'),
            'user': os.getenv('SUPABASE_DB_USER'),
            'password': os.getenv('SUPABASE_DB_PASSWORD'),
            'port': 5432
        }
    
    def get_connection(self):
        """Get a new database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    @staticmethod
    def _canon(s):
        """Normalize status values to display format"""
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

    def _row_to_report(self, row):
        """Convert a DB row to report dict"""
        return {
            'id': row[0],
            'user_email': row[1],
            'user_name': row[2],
            'user_type': row[3],
            'issue_description': row[4],
            'location': row[5],
            'report_image': row[6],
            'category': row[7] or 'Uncategorized',
            'status': self._canon(row[8] or 'pending'),
            'admin_remarks': row[9],
            'status_updated_at': row[10],
            'status_updated_by': row[11],
            'created_at': row[12],
            'expires_at': row[13],
        }

    _REPORT_COLS = '''id, user_email, user_name, user_type, issue_description,
                      location, report_image, category, status, admin_remarks,
                      status_updated_at, status_updated_by, created_at, expires_at'''

    def add_report(self, user_email, user_name, user_type, issue_description, location, 
                   category="Uncategorized", report_image=None, expires_days=30):
        """Add a new report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(days=expires_days)
        
        try:
            cursor.execute('''
                INSERT INTO reports (user_email, user_name, user_type, issue_description,
                                    location, category, status, report_image, created_at, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
                RETURNING id
            ''', (user_email, user_name, user_type, issue_description, location, 
                  category, 'pending', report_image, expires_at))
            
            report_id = cursor.fetchone()[0]
            conn.commit()
            return report_id
        finally:
            cursor.close()
            conn.close()

    def get_all_reports(self):
        """Get all reports"""
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT {self._REPORT_COLS} FROM reports ORDER BY id DESC')
            reports = cursor.fetchall()
            return [self._row_to_report(r) for r in reports]
        finally:
            cursor.close()
            conn.close()
    
    def get_reports_by_user(self, user_email):
        """Get all reports by a specific user"""
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT {self._REPORT_COLS} FROM reports WHERE user_email = %s ORDER BY id DESC',
                          (user_email,))
            reports = cursor.fetchall()
            return [self._row_to_report(r) for r in reports]
        finally:
            cursor.close()
            conn.close()
    
    def get_reports_by_category(self, category):
        """Get all reports by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT {self._REPORT_COLS} FROM reports WHERE category = %s ORDER BY id DESC',
                          (category,))
            reports = cursor.fetchall()
            return [self._row_to_report(r) for r in reports]
        finally:
            cursor.close()
            conn.close()

    def get_report_by_id(self, report_id):
        """Return a single report dict by id or None if not found."""
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'SELECT {self._REPORT_COLS} FROM reports WHERE id = %s LIMIT 1',
                          (report_id,))
            r = cursor.fetchone()
            return self._row_to_report(r) if r else None
        finally:
            cursor.close()
            conn.close()

    def delete_expired_unresolved_reports(self):
        """Delete reports that have expired for 7 days and are unresolved"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM reports
                WHERE expires_at IS NOT NULL
                  AND (expires_at + INTERVAL '7 days') <= NOW()
                  AND LOWER(status) NOT IN ('resolved', 'rejected')
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def extend_report_expiration(self, report_id, days=7):
        """Extend a report's expiration date by N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE reports
                SET expires_at = COALESCE(expires_at, NOW()) + INTERVAL %s
                WHERE id = %s
            """, (f'{days} days', report_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def _normalize_status(new_status):
        """Normalize status to database format"""
        ns = (new_status or '').strip().lower()
        if 'pending' in ns:
            return 'pending'
        if 'on going' in ns or 'ongoing' in ns or 'in progress' in ns:
            return 'in progress'
        if 'fixed' in ns or 'resolved' in ns:
            return 'resolved'
        if 'reject' in ns or 'rejected' in ns:
            return 'rejected'
        return ns

    def update_report_status(self, report_id, new_status, remarks=None, updated_by=None):
        """Update report status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        ns = self._normalize_status(new_status)
        
        try:
            cursor.execute('''
                UPDATE reports
                SET status = %s, admin_remarks = %s, status_updated_at = NOW(),
                    status_updated_by = %s
                WHERE id = %s
            ''', (ns, remarks, updated_by, report_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def update_report(self, report_id, issue_description, location):
        """Update report details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE reports
                SET issue_description = %s, location = %s
                WHERE id = %s
            ''', (issue_description, location, report_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def delete_report(self, report_id):
        """Delete a report"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM reports WHERE id = %s', (report_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    def user_exists(self, user_email):
        """Check if user has any reports"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT 1 FROM reports WHERE user_email = %s LIMIT 1', (user_email,))
            exists = cursor.fetchone() is not None
            return exists
        finally:
            cursor.close()
            conn.close()
    
    def get_or_create_user(self, email, name, role, picture=None):
        """Get user from database or create if doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT email, name, role, profile_picture FROM users WHERE email = %s',
                          (email,))
            user = cursor.fetchone()
            
            if user:
                return {
                    'email': user[0],
                    'name': user[1],
                    'role': user[2],
                    'picture': user[3]
                }
            else:
                cursor.execute('''
                    INSERT INTO users (email, name, role, profile_picture)
                    VALUES (%s, %s, %s, %s)
                ''', (email, name, role, picture))
                conn.commit()
                
                return {
                    'email': email,
                    'name': name,
                    'role': role,
                    'picture': picture
                }
        finally:
            cursor.close()
            conn.close()
    
    def create_or_update_user(self, email, name, role, picture=None):
        """Create new user or update existing user (upsert operation)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
            exists = cursor.fetchone()
            
            if exists:
                if picture:
                    cursor.execute('''
                        UPDATE users
                        SET name = %s, role = %s, profile_picture = %s, updated_at = NOW()
                        WHERE email = %s
                    ''', (name, role, picture, email))
                else:
                    cursor.execute('''
                        UPDATE users
                        SET name = %s, role = %s, updated_at = NOW()
                        WHERE email = %s
                    ''', (name, role, email))
            else:
                cursor.execute('''
                    INSERT INTO users (email, name, role, profile_picture)
                    VALUES (%s, %s, %s, %s)
                ''', (email, name, role, picture))
            
            conn.commit()
            
            return {
                'email': email,
                'name': name,
                'role': role,
                'picture': picture
            }
        finally:
            cursor.close()
            conn.close()
    
    def update_user_profile(self, email, name=None, profile_picture=None):
        """Update user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            
            if profile_picture is not None:
                updates.append("profile_picture = %s")
                params.append(profile_picture)
            
            if not updates:
                return False
            
            updates.append("updated_at = NOW()")
            params.append(email)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE email = %s"
            cursor.execute(query, params)
            conn.commit()
            
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def get_user_by_email(self, email):
        """Get user profile by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT email, name, role, profile_picture, created_at, updated_at
                FROM users
                WHERE email = %s
            ''', (email,))
            
            user = cursor.fetchone()
            
            if not user:
                return None
            
            return {
                'email': user[0],
                'name': user[1],
                'role': user[2],
                'picture': user[3],
                'created_at': user[4],
                'updated_at': user[5]
            }
        finally:
            cursor.close()
            conn.close()
    
    def update_user_password(self, email, password):
        """Update user's password (hashed)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            cursor.execute('''
                UPDATE users
                SET password_hash = %s, updated_at = NOW()
                WHERE email = %s
            ''', (password_hash, email))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()
    
    def verify_user_password(self, email, password):
        """Verify user's password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT password_hash FROM users WHERE email = %s', (email,))
            result = cursor.fetchone()
            
            if not result or not result[0]:
                return False
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            return password_hash == result[0]
        finally:
            cursor.close()
            conn.close()

    # ── Analytics queries ──

    def get_reports_per_day(self, days=7):
        """Get report counts per day for the last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            window_days = max(int(days) - 1, 0)
            cursor.execute('''
                SELECT DATE(COALESCE(created_at, status_updated_at)) as day, COUNT(*) as cnt
                FROM reports
                WHERE DATE(COALESCE(created_at, status_updated_at)) >= CURRENT_DATE - INTERVAL %s
                GROUP BY DATE(COALESCE(created_at, status_updated_at))
                ORDER BY day ASC
            ''', (f'{window_days} days',))
            rows = cursor.fetchall()
            return [{'day': str(r[0]), 'count': r[1]} for r in rows if r[0]]
        finally:
            cursor.close()
            conn.close()

    def get_reports_per_category(self):
        """Get report count grouped by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COALESCE(category, 'Uncategorized') as cat, COUNT(*) as cnt
                FROM reports
                GROUP BY cat
                ORDER BY cnt DESC
            ''')
            rows = cursor.fetchall()
            return [{'category': r[0], 'count': r[1]} for r in rows]
        finally:
            cursor.close()
            conn.close()

    def get_reports_per_location(self):
        """Get report count grouped by location"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COALESCE(location, 'Unknown') as loc, COUNT(*) as cnt
                FROM reports
                GROUP BY loc
                ORDER BY cnt DESC
                LIMIT 10
            ''')
            rows = cursor.fetchall()
            return [{'location': r[0], 'count': r[1]} for r in rows]
        finally:
            cursor.close()
            conn.close()

    def get_resolution_rate(self):
        """Get overall resolution rate (resolved / total)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM reports')
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM reports WHERE LOWER(status) IN ('resolved', 'fixed')")
            resolved = cursor.fetchone()[0]
            
            return {
                'total': total,
                'resolved': resolved,
                'rate': round(resolved / total * 100, 1) if total > 0 else 0
            }
        finally:
            cursor.close()
            conn.close()

    def get_total_users_count(self):
        """Get count of registered users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            return count
        finally:
            cursor.close()
            conn.close()

    def get_top_reporters(self, limit=5):
        """Get the users who filed the most reports"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT user_name, user_email, COUNT(*) as cnt
                FROM reports
                GROUP BY user_email, user_name
                ORDER BY cnt DESC
                LIMIT %s
            ''', (limit,))
            rows = cursor.fetchall()
            return [{'name': r[0], 'email': r[1], 'count': r[2]} for r in rows]
        finally:
            cursor.close()
            conn.close()

# Initialize database instance
db = Database()
