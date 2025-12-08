"""User Activity Monitoring Service - tracks login history, failed attempts, IP/Geo data."""

import sqlite3
from datetime import datetime
import socket
import os

class ActivityMonitor:
    def __init__(self, db_path="app_database.db"):
        self.db_path = db_path
        self._init_activity_table()
    
    def _init_activity_table(self):
        """Initialize user_activity table if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main activity log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                user_name TEXT,
                activity_type TEXT NOT NULL,
                ip_address TEXT,
                location_country TEXT,
                location_city TEXT,
                location_isp TEXT,
                device_info TEXT,
                status TEXT DEFAULT 'success',
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_email) REFERENCES users(email)
            )
        ''')
        
        # User login statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_login_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT UNIQUE NOT NULL,
                last_login TIMESTAMP,
                last_login_ip TEXT,
                last_login_location TEXT,
                total_logins INTEGER DEFAULT 0,
                total_failed_attempts INTEGER DEFAULT 0,
                last_failed_attempt TIMESTAMP,
                account_locked INTEGER DEFAULT 0,
                lock_until TIMESTAMP,
                FOREIGN KEY(user_email) REFERENCES users(email)
            )
        ''')
        
        # Failed login attempts table (for security)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failed_login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                ip_address TEXT,
                location TEXT,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_device_info(self):
        """Get device information (OS, hostname, etc.)"""
        try:
            hostname = socket.gethostname()
            os_name = os.name
            return f"{os_name}:{hostname}"
        except:
            return "Unknown"
    
    def get_ip_address(self):
        """Get client IP address"""
        try:
            # Try to get external IP via gethostbyname
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except:
            return "127.0.0.1"
    
    def get_geolocation(self, ip_address):
        """Fetch geolocation data for IP address (mocked for demo)"""
        # In production, use geoip2 or ipstack API
        # For now, return mock data based on common IPs
        
        mock_locations = {
            "127.0.0.1": {"country": "Local", "city": "Localhost", "isp": "Local"},
            "192.168": {"country": "Local", "city": "Private Network", "isp": "Private"},
        }
        
        # Check for private IP
        if ip_address.startswith("192.168") or ip_address.startswith("10."):
            return {"country": "Local", "city": "Private Network", "isp": "Private"}
        
        # Default to mock location for demo
        return {
            "country": "Philippines",
            "city": "Cebu City",
            "isp": "ISP Provider"
        }
    
    def log_login_attempt(self, email, name, success=True, details=None):
        """Log a login attempt with IP and location info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        ip = self.get_ip_address()
        geo = self.get_geolocation(ip)
        device = self.get_device_info()
        
        # Log to activity table
        cursor.execute('''
            INSERT INTO user_activity (user_email, user_name, activity_type, ip_address, 
                                      location_country, location_city, location_isp, 
                                      device_info, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, name, 'login', ip, geo['country'], geo['city'], geo['isp'], 
              device, 'success' if success else 'failed', details))
        
        # Update login stats
        cursor.execute('SELECT id FROM user_login_stats WHERE user_email = ?', (email,))
        exists = cursor.fetchone()
        
        if exists:
            if success:
                cursor.execute('''
                    UPDATE user_login_stats
                    SET last_login = CURRENT_TIMESTAMP,
                        last_login_ip = ?,
                        last_login_location = ?,
                        total_logins = total_logins + 1
                    WHERE user_email = ?
                ''', (ip, f"{geo['city']}, {geo['country']}", email))
            else:
                cursor.execute('''
                    UPDATE user_login_stats
                    SET total_failed_attempts = total_failed_attempts + 1,
                        last_failed_attempt = CURRENT_TIMESTAMP
                    WHERE user_email = ?
                ''', (email,))
        else:
            # Create new entry
            if success:
                cursor.execute('''
                    INSERT INTO user_login_stats 
                    (user_email, last_login, last_login_ip, last_login_location, total_logins)
                    VALUES (?, CURRENT_TIMESTAMP, ?, ?, 1)
                ''', (email, ip, f"{geo['city']}, {geo['country']}"))
            else:
                cursor.execute('''
                    INSERT INTO user_login_stats 
                    (user_email, total_failed_attempts, last_failed_attempt)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                ''', (email,))
        
        # Log failed attempt separately
        if not success:
            cursor.execute('''
                INSERT INTO failed_login_attempts (email, ip_address, location, reason)
                VALUES (?, ?, ?, ?)
            ''', (email, ip, f"{geo['city']}, {geo['country']}", details or 'Unknown reason'))
        
        conn.commit()
        conn.close()
    
    def get_user_activity(self, email, limit=50, offset=0):
        """Get user's activity history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_email, user_name, activity_type, ip_address, 
                   location_country, location_city, location_isp, device_info, 
                   status, details, timestamp
            FROM user_activity
            WHERE user_email = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        ''', (email, limit, offset))
        
        activities = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': a[0],
                'email': a[1],
                'name': a[2],
                'type': a[3],
                'ip': a[4],
                'country': a[5],
                'city': a[6],
                'isp': a[7],
                'device': a[8],
                'status': a[9],
                'details': a[10],
                'timestamp': a[11]
            }
            for a in activities
        ]
    
    def get_user_stats(self, email):
        """Get user login statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_email, last_login, last_login_ip, last_login_location,
                   total_logins, total_failed_attempts, last_failed_attempt, account_locked
            FROM user_login_stats
            WHERE user_email = ?
        ''', (email,))
        
        stats = cursor.fetchone()
        conn.close()
        
        if not stats:
            return None
        
        return {
            'email': stats[0],
            'last_login': stats[1],
            'last_login_ip': stats[2],
            'last_login_location': stats[3],
            'total_logins': stats[4],
            'total_failed_attempts': stats[5],
            'last_failed_attempt': stats[6],
            'account_locked': stats[7]
        }
    
    def get_failed_attempts(self, email, limit=20):
        """Get recent failed login attempts for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, email, ip_address, location, reason, timestamp
            FROM failed_login_attempts
            WHERE email = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (email, limit))
        
        attempts = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': a[0],
                'email': a[1],
                'ip': a[2],
                'location': a[3],
                'reason': a[4],
                'timestamp': a[5]
            }
            for a in attempts
        ]
    
    def get_all_user_stats(self, limit=100):
        """Get login stats for all users (for admin dashboard)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_email, last_login, last_login_ip, last_login_location,
                   total_logins, total_failed_attempts, last_failed_attempt, account_locked
            FROM user_login_stats
            ORDER BY last_login DESC
            LIMIT ?
        ''', (limit,))
        
        stats = cursor.fetchall()
        conn.close()
        
        return [
            {
                'email': s[0],
                'last_login': s[1],
                'last_login_ip': s[2],
                'last_login_location': s[3],
                'total_logins': s[4],
                'total_failed_attempts': s[5],
                'last_failed_attempt': s[6],
                'account_locked': s[7]
            }
            for s in stats
        ]
    
    def log_logout(self, email, name):
        """Log user logout"""
        ip = self.get_ip_address()
        device = self.get_device_info()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_activity (user_email, user_name, activity_type, ip_address, 
                                      device_info, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (email, name, 'logout', ip, device, 'success'))
        
        conn.commit()
        conn.close()
    
    def log_profile_update(self, email, name, details):
        """Log profile update activity"""
        ip = self.get_ip_address()
        device = self.get_device_info()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_activity (user_email, user_name, activity_type, ip_address, 
                                      device_info, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email, name, 'profile_update', ip, device, 'success', details))
        
        conn.commit()
        conn.close()


activity_monitor = ActivityMonitor()
