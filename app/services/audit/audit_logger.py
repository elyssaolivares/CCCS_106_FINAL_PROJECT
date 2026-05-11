"""Audit logging with SQLite test mode and Supabase REST runtime mode."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class AuditLogger:
    def __init__(self, db_path: str = "app_database.db"):
        self.db_path = db_path
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.use_sqlite = bool(db_path and db_path != "app_database.db") or not (self.supabase_url and self.supabase_key)
        if self.use_sqlite:
            self._init_audit_table()

    def _base_url(self) -> str:
        if not self.supabase_url:
            raise RuntimeError("SUPABASE_URL is not configured")
        return f"{self.supabase_url.rstrip('/')}/rest/v1"

    def _headers(self, prefer: str = "return=representation") -> Dict[str, str]:
        if not self.supabase_key:
            raise RuntimeError("SUPABASE_KEY is not configured")
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        }

    def _init_audit_table(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
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
            """
        )
        conn.commit()
        conn.close()

    def _sqlite_log_action(self, actor_email, actor_name, action_type, resource_type=None, resource_id=None, details=None, status="success"):
        if not self.db_path:
            return None
        self._init_audit_table()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs (actor_email, actor_name, action_type, resource_type, resource_id, details, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (actor_email, actor_name, action_type, resource_type, resource_id, details, status),
        )
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return log_id

    def log_action(self, actor_email, actor_name, action_type, resource_type=None, resource_id=None, details=None, status="success"):
        """Log an audit entry."""
        if self.use_sqlite:
            return self._sqlite_log_action(actor_email, actor_name, action_type, resource_type, resource_id, details, status)

        payload = {
            "actor_email": actor_email,
            "actor_name": actor_name,
            "action_type": action_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
            "timestamp": _now_iso(),
            "status": status,
        }
        response = requests.post(
            f"{self._base_url()}/audit_logs",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            data = data[0] if data else {}
        return data.get("id")

    def get_audit_logs(self, actor_email=None, action_type=None, resource_type=None, start_date=None, end_date=None, limit=100, offset=0):
        """Retrieve audit logs with optional filters."""
        if self.use_sqlite:
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
            rows = cursor.fetchall()
            conn.close()
            return [
                {
                    "id": row[0],
                    "actor_email": row[1],
                    "actor_name": row[2],
                    "action_type": row[3],
                    "resource_type": row[4],
                    "resource_id": row[5],
                    "details": row[6],
                    "timestamp": row[7],
                    "status": row[8],
                }
                for row in rows
            ]

        params: Dict[str, str] = {
            "select": "id,actor_email,actor_name,action_type,resource_type,resource_id,details,timestamp,status",
            "order": "timestamp.desc",
            "limit": str(int(limit)),
            "offset": str(int(offset)),
        }
        if actor_email:
            params["actor_email"] = f"eq.{actor_email}"
        if action_type:
            params["action_type"] = f"eq.{action_type}"
        if resource_type:
            params["resource_type"] = f"eq.{resource_type}"
        if start_date:
            params["timestamp"] = f"gte.{start_date}"
        if end_date:
            params["timestamp"] = f"lte.{end_date}"

        response = requests.get(
            f"{self._base_url()}/audit_logs",
            headers=self._headers(),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_audit_logs_count(self, actor_email=None, action_type=None, resource_type=None, start_date=None, end_date=None):
        """Get total count of audit logs matching filters."""
        if self.use_sqlite:
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

        params: Dict[str, str] = {"select": "id"}
        if actor_email:
            params["actor_email"] = f"eq.{actor_email}"
        if action_type:
            params["action_type"] = f"eq.{action_type}"
        if resource_type:
            params["resource_type"] = f"eq.{resource_type}"
        if start_date:
            params["timestamp"] = f"gte.{start_date}"
        if end_date:
            params["timestamp"] = f"lte.{end_date}"

        response = requests.get(
            f"{self._base_url()}/audit_logs",
            headers=self._headers(prefer="count=exact"),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        content_range = response.headers.get("Content-Range", "0-0/0")
        return int(content_range.split("/")[-1])


audit_logger = AuditLogger()
