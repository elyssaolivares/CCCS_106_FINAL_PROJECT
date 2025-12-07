import sqlite3
import hashlib

class Database:
    def __init__(self, db_name="app_database.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                user_name TEXT NOT NULL,
                user_type TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT DEFAULT 'Uncategorized',
                status TEXT DEFAULT 'Pending'
            )
        ''')
        
        cursor.execute("PRAGMA table_info(reports)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'category' not in columns:
            cursor.execute('ALTER TABLE reports ADD COLUMN category TEXT DEFAULT "Uncategorized"')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                profile_picture TEXT,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    
    def add_report(self, user_email, user_name, user_type, issue_description, location, category="Uncategorized"):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reports (user_email, user_name, user_type, issue_description, location, category, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_email, user_name, user_type, issue_description, location, category, 'Pending'))
        
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
                'status': report[7]
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
                'status': report[7]
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
                'status': report[7]
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

        return {
            'id': r[0],
            'user_email': r[1],
            'user_name': r[2],
            'user_type': r[3],
            'issue_description': r[4],
            'location': r[5],
            'category': r[6],
            'status': r[7]
        }
    
    def update_report_status(self, report_id, new_status):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reports
            SET status = ?
            WHERE id = ?
        ''', (new_status, report_id))
        
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
    
    
    def get_or_create_user(self, email, name, role, picture=None):
        """Get user from database or create if doesn't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT email, name, role, profile_picture FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            # User exists, return their data
            conn.close()
            return {
                'email': user[0],
                'name': user[1],
                'role': user[2],
                'picture': user[3]
            }
        else:
            # Create new user
            cursor.execute('''
                INSERT INTO users (email, name, role, profile_picture)
                VALUES (?, ?, ?, ?)
            ''', (email, name, role, picture))
            conn.commit()
            conn.close()
            
            return {
                'email': email,
                'name': name,
                'role': role,
                'picture': picture
            }
    
    def create_or_update_user(self, email, name, role, picture=None):
        """Create new user or update existing user (upsert operation)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing user
            if picture:
                cursor.execute('''
                    UPDATE users
                    SET name = ?, role = ?, profile_picture = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE email = ?
                ''', (name, role, picture, email))
            else:
                cursor.execute('''
                    UPDATE users
                    SET name = ?, role = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE email = ?
                ''', (name, role, email))
        else:
            # Create new user
            cursor.execute('''
                INSERT INTO users (email, name, role, profile_picture)
                VALUES (?, ?, ?, ?)
            ''', (email, name, role, picture))
        
        conn.commit()
        conn.close()
        
        return {
            'email': email,
            'name': name,
            'role': role,
            'picture': picture
        }
    
    def update_user_profile(self, email, name=None, profile_picture=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if profile_picture is not None:
            updates.append("profile_picture = ?")
            params.append(profile_picture)
        
        if not updates:
            conn.close()
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(email)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE email = ?"
        cursor.execute(query, params)
        
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    
    def get_user_by_email(self, email):
        """Get user profile by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, name, role, profile_picture, created_at, updated_at
            FROM users
            WHERE email = ?
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
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
    
    def update_user_password(self, email, password):
        """Update user's password (hashed)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            UPDATE users
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
        ''', (password_hash, email))
        
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0
    
    def verify_user_password(self, email, password):
        """Verify user's password"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT password_hash FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == result[0]

db = Database()