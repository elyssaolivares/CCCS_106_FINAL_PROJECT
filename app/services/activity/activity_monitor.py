"""User activity monitoring with SQLite test mode and Supabase REST runtime mode."""

from __future__ import annotations

import os
import socket
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ActivityMonitor:
    def __init__(self, db_path="app_database.db"):
        self.db_path = db_path
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.use_sqlite = bool(db_path and db_path != "app_database.db") or not (self.supabase_url and self.supabase_key)
        if self.use_sqlite:
            self._init_activity_table()

    def _headers(self, prefer="return=representation"):
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        }

    def _base_url(self) -> str:
        return f"{self.supabase_url.rstrip('/')}/rest/v1"

    def _init_activity_table(self):
        """Initialize user_activity table if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

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

    def _sqlite_log_login_attempt(self, email, name, success=True, details=None):
        ip = self.get_ip_address()
        geo = self.get_geolocation(ip)
        device = self.get_device_info()
        status = "success" if success else "failed"

        self._init_activity_table()
        conn = self._sqlite_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_activity (user_email, user_name, activity_type, ip_address,
                                      location_country, location_city, location_isp,
                                      device_info, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (email, name, 'login', ip, geo['country'], geo['city'], geo['isp'],
              device, status, details))

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

        if not success:
            cursor.execute('''
                INSERT INTO failed_login_attempts (email, ip_address, location, reason)
                VALUES (?, ?, ?, ?)
            ''', (email, ip, f"{geo['city']}, {geo['country']}", details or 'Unknown reason'))

        conn.commit()
        conn.close()

    def get_device_info(self):
        """Get device information (OS, hostname, etc.)"""
        try:
            hostname = socket.gethostname()
            os_name = os.name
            return f"{os_name}:{hostname}"
        except Exception:
            return "Unknown"

    def get_ip_address(self):
        """Get client IP address"""
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception:
            return "127.0.0.1"

    def get_geolocation(self, ip_address):
        """Fetch geolocation data for IP address (mocked for demo)"""
        if ip_address.startswith("192.168") or ip_address.startswith("10."):
            return {"country": "Local", "city": "Private Network", "isp": "Private"}
        return {"country": "Philippines", "city": "Cebu City", "isp": "ISP Provider"}

    def _sqlite_conn(self):
        return sqlite3.connect(self.db_path)

    def _api_get(self, table: str, params: Dict[str, Any]):
        response = requests.get(
            f"{self._base_url()}/{table}",
            headers=self._headers(prefer="return=representation"),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def _api_post(self, table: str, payload: Dict[str, Any]):
        response = requests.post(
            f"{self._base_url()}/{table}",
            headers=self._headers(prefer="return=representation"),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data[0] if data else {}
        return data

    def _api_patch(self, table: str, filters: Dict[str, str], payload: Dict[str, Any]):
        response = requests.patch(
            f"{self._base_url()}/{table}",
            headers=self._headers(prefer="return=representation"),
            params=filters,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json() if response.text else []

    def _api_select_rows(self, table: str, columns: str, filters: Optional[Dict[str, str]] = None, order: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None):
        params: Dict[str, str] = {"select": columns}
        if filters:
            params.update(filters)
        if order:
            params["order"] = order
        if limit is not None:
            params["limit"] = str(int(limit))
        if offset is not None:
            params["offset"] = str(int(offset))
        return self._api_get(table, params)

    def log_login_attempt(self, email, name, success=True, details=None):
        """Log a login attempt with IP and location info"""
        if self.use_sqlite:
            self._sqlite_log_login_attempt(email, name, success=success, details=details)
            return

        ip = self.get_ip_address()
        geo = self.get_geolocation(ip)
        device = self.get_device_info()
        status = "success" if success else "failed"

        if self.use_sqlite:
            conn = self._sqlite_conn()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_activity (user_email, user_name, activity_type, ip_address,
                                          location_country, location_city, location_isp,
                                          device_info, status, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, name, 'login', ip, geo['country'], geo['city'], geo['isp'],
                  device, status, details))

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

            if not success:
                cursor.execute('''
                    INSERT INTO failed_login_attempts (email, ip_address, location, reason)
                    VALUES (?, ?, ?, ?)
                ''', (email, ip, f"{geo['city']}, {geo['country']}", details or 'Unknown reason'))

            conn.commit()
            conn.close()
            return

        activity_payload = {
            "user_email": email,
            "user_name": name,
            "activity_type": "login",
            "ip_address": ip,
            "location_country": geo["country"],
            "location_city": geo["city"],
            "location_isp": geo["isp"],
            "device_info": device,
            "status": status,
            "details": details,
            "timestamp": _now_iso(),
        }
        location = f"{geo['city']}, {geo['country']}"
        self._api_post("user_activity", activity_payload)

        stats = self._api_select_rows("user_login_stats", "id,user_email,total_logins,total_failed_attempts", {"user_email": f"eq.{email}"})
        if stats:
            if success:
                self._api_patch(
                    "user_login_stats",
                    {"user_email": f"eq.{email}"},
                    {
                        "last_login": _now_iso(),
                        "last_login_ip": ip,
                        "last_login_location": location,
                        "total_logins": int(stats[0].get("total_logins") or 0) + 1,
                    },
                )
            else:
                self._api_patch(
                    "user_login_stats",
                    {"user_email": f"eq.{email}"},
                    {
                        "total_failed_attempts": int(stats[0].get("total_failed_attempts") or 0) + 1,
                        "last_failed_attempt": _now_iso(),
                    },
                )
        else:
            if success:
                self._api_post(
                    "user_login_stats",
                    {
                        "user_email": email,
                        "last_login": _now_iso(),
                        "last_login_ip": ip,
                        "last_login_location": location,
                        "total_logins": 1,
                        "total_failed_attempts": 0,
                    },
                )
            else:
                self._api_post(
                    "user_login_stats",
                    {
                        "user_email": email,
                        "total_failed_attempts": 1,
                        "last_failed_attempt": _now_iso(),
                    },
                )

        if not success:
            self._api_post(
                "failed_login_attempts",
                {
                    "email": email,
                    "ip_address": ip,
                    "location": location,
                    "reason": details or "Unknown reason",
                    "timestamp": _now_iso(),
                },
            )

    def get_user_activity(self, email, limit=50, offset=0):
        """Get user's activity history"""
        if self.use_sqlite:
            conn = self._sqlite_conn()
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

        rows = self._api_select_rows(
            "user_activity",
            "id,user_email,user_name,activity_type,ip_address,location_country,location_city,location_isp,device_info,status,details,timestamp",
            {"user_email": f"eq.{email}"},
            order="timestamp.desc",
            limit=limit,
            offset=offset,
        )
        return [
            {
                'id': row.get('id'),
                'email': row.get('user_email'),
                'name': row.get('user_name'),
                'type': row.get('activity_type'),
                'ip': row.get('ip_address'),
                'country': row.get('location_country'),
                'city': row.get('location_city'),
                'isp': row.get('location_isp'),
                'device': row.get('device_info'),
                'status': row.get('status'),
                'details': row.get('details'),
                'timestamp': row.get('timestamp')
            }
            for row in rows
        ]

    def get_user_stats(self, email):
        """Get user login statistics"""
        if self.use_sqlite:
            conn = self._sqlite_conn()
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

        rows = self._api_select_rows(
            "user_login_stats",
            "user_email,last_login,last_login_ip,last_login_location,total_logins,total_failed_attempts,last_failed_attempt,account_locked",
            {"user_email": f"eq.{email}"},
            limit=1,
        )
        if not rows:
            return None
        stats = rows[0]
        return {
            'email': stats.get('user_email'),
            'last_login': stats.get('last_login'),
            'last_login_ip': stats.get('last_login_ip'),
            'last_login_location': stats.get('last_login_location'),
            'total_logins': stats.get('total_logins', 0),
            'total_failed_attempts': stats.get('total_failed_attempts', 0),
            'last_failed_attempt': stats.get('last_failed_attempt'),
            'account_locked': stats.get('account_locked', 0)
        }

    def get_failed_attempts(self, email, limit=20):
        """Get recent failed login attempts for a user"""
        if self.use_sqlite:
            conn = self._sqlite_conn()
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

        rows = self._api_select_rows(
            "failed_login_attempts",
            "id,email,ip_address,location,reason,timestamp",
            {"email": f"eq.{email}"},
            order="timestamp.desc",
            limit=limit,
        )
        return [
            {
                'id': row.get('id'),
                'email': row.get('email'),
                'ip': row.get('ip_address'),
                'location': row.get('location'),
                'reason': row.get('reason'),
                'timestamp': row.get('timestamp')
            }
            for row in rows
        ]

    def get_all_user_stats(self, limit=100):
        """Get login stats for all users (for admin dashboard)"""
        if self.use_sqlite:
            conn = self._sqlite_conn()
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

        rows = self._api_select_rows(
            "user_login_stats",
            "user_email,last_login,last_login_ip,last_login_location,total_logins,total_failed_attempts,last_failed_attempt,account_locked",
            order="last_login.desc",
            limit=limit,
        )
        return [
            {
                'email': row.get('user_email'),
                'last_login': row.get('last_login'),
                'last_login_ip': row.get('last_login_ip'),
                'last_login_location': row.get('last_login_location'),
                'total_logins': row.get('total_logins', 0),
                'total_failed_attempts': row.get('total_failed_attempts', 0),
                'last_failed_attempt': row.get('last_failed_attempt'),
                'account_locked': row.get('account_locked', 0)
            }
            for row in rows
        ]

    def log_logout(self, email, name):
        """Log user logout"""
        ip = self.get_ip_address()
        device = self.get_device_info()

        if self.use_sqlite:
            conn = self._sqlite_conn()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_activity (user_email, user_name, activity_type, ip_address,
                                          device_info, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, name, 'logout', ip, device, 'success'))
            conn.commit()
            conn.close()
            return

        self._api_post(
            "user_activity",
            {
                "user_email": email,
                "user_name": name,
                "activity_type": "logout",
                "ip_address": ip,
                "device_info": device,
                "status": "success",
                "timestamp": _now_iso(),
            },
        )

    def log_profile_update(self, email, name, details):
        """Log profile update activity"""
        ip = self.get_ip_address()
        device = self.get_device_info()

        if self.use_sqlite:
            conn = self._sqlite_conn()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_activity (user_email, user_name, activity_type, ip_address,
                                          device_info, status, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (email, name, 'profile_update', ip, device, 'success', details))
            conn.commit()
            conn.close()
            return

        self._api_post(
            "user_activity",
            {
                "user_email": email,
                "user_name": name,
                "activity_type": "profile_update",
                "ip_address": ip,
                "device_info": device,
                "status": "success",
                "details": details,
                "timestamp": _now_iso(),
            },
        )


activity_monitor = ActivityMonitor()
