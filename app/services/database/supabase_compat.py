"""Database access layer with SQLite test mode and Supabase REST mode."""

from __future__ import annotations

import hashlib
import os
import sqlite3
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc).isoformat(timespec="seconds")
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _canon_status_display(value: Any) -> str:
    if not value:
        return "Pending"
    text = str(value).strip().lower()
    if "pending" in text:
        return "Pending"
    if "on going" in text or "ongoing" in text or "in progress" in text:
        return "In Progress"
    if "fixed" in text or "resolved" in text:
        return "Resolved"
    if "reject" in text or "rejected" in text:
        return "Rejected"
    return str(value).strip().title()


def _normalize_status_db(value: Any) -> str:
    text = (value or "").strip().lower()
    if "pending" in text:
        return "pending"
    if "on going" in text or "ongoing" in text or "in progress" in text:
        return "in progress"
    if "fixed" in text or "resolved" in text:
        return "resolved"
    if "reject" in text or "rejected" in text:
        return "rejected"
    return text


def _report_dict_from_api(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row.get("id"),
        "user_email": row.get("user_email"),
        "user_name": row.get("user_name"),
        "user_type": row.get("user_type"),
        "issue_description": row.get("issue_description"),
        "location": row.get("location"),
        "report_image": row.get("report_image"),
        "category": row.get("category") or "Uncategorized",
        "status": _canon_status_display(row.get("status")),
        "admin_remarks": row.get("admin_remarks"),
        "status_updated_at": row.get("status_updated_at"),
        "status_updated_by": row.get("status_updated_by"),
        "created_at": row.get("created_at"),
        "expires_at": row.get("expires_at"),
    }


def _report_dict_from_sqlite_row(row: tuple) -> Dict[str, Any]:
    return {
        "id": row[0],
        "user_email": row[1],
        "user_name": row[2],
        "user_type": row[3],
        "issue_description": row[4],
        "location": row[5],
        "report_image": row[6] if len(row) > 6 else None,
        "category": row[7] if len(row) > 7 else "Uncategorized",
        "status": _canon_status_display(row[8] if len(row) > 8 else "pending"),
        "admin_remarks": row[9] if len(row) > 9 else None,
        "status_updated_at": row[10] if len(row) > 10 else None,
        "status_updated_by": row[11] if len(row) > 11 else None,
        "created_at": row[12] if len(row) > 12 else None,
        "expires_at": row[13] if len(row) > 13 else None,
    }


class _SQLiteBackend:
    REPORT_COLS = (
        "id, user_email, user_name, user_type, issue_description,"
        " location, report_image, category, status, admin_remarks,"
        " status_updated_at, status_updated_by, created_at, expires_at"
    )

    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
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
            """
        )

        cursor.execute("PRAGMA table_info(reports)")
        columns = [column[1] for column in cursor.fetchall()]
        if "category" not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN category TEXT DEFAULT 'Uncategorized'")
        if "created_at" not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN created_at TIMESTAMP")
        if "expires_at" not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN expires_at TIMESTAMP")
        if "admin_remarks" not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN admin_remarks TEXT")
        if "status_updated_at" not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN status_updated_at TIMESTAMP")
        if "status_updated_by" not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN status_updated_by TEXT")
        if "report_image" not in columns:
            cursor.execute("ALTER TABLE reports ADD COLUMN report_image TEXT")

        cursor.execute(
            """
            UPDATE reports
            SET created_at = COALESCE(created_at, status_updated_at, CURRENT_TIMESTAMP)
            WHERE created_at IS NULL
            """
        )
        cursor.execute(
            """
            UPDATE reports
            SET expires_at = COALESCE(expires_at, datetime(COALESCE(created_at, status_updated_at, CURRENT_TIMESTAMP), '+30 days'))
            WHERE expires_at IS NULL
            """
        )

        cursor.execute(
            """
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
            """
        )

        conn.commit()
        conn.close()

    def _row_to_report(self, row: tuple) -> Dict[str, Any]:
        return _report_dict_from_sqlite_row(row)

    def add_report(self, user_email, user_name, user_type, issue_description, location, category="Uncategorized", report_image=None, expires_days: int = 30):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reports (
                user_email, user_name, user_type, issue_description, location,
                category, status, report_image, created_at, expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, datetime(CURRENT_TIMESTAMP, ?))
            """,
            (user_email, user_name, user_type, issue_description, location, category, "pending", report_image, f"+{int(expires_days)} days"),
        )
        conn.commit()
        report_id = cursor.lastrowid
        conn.close()
        return report_id

    def get_all_reports(self):
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {self.REPORT_COLS} FROM reports ORDER BY id DESC")
        reports = cursor.fetchall()
        conn.close()
        return [self._row_to_report(r) for r in reports]

    def get_reports_by_user(self, user_email):
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT {self.REPORT_COLS} FROM reports WHERE user_email = ? ORDER BY id DESC",
            (user_email,),
        )
        reports = cursor.fetchall()
        conn.close()
        return [self._row_to_report(r) for r in reports]

    def get_reports_by_category(self, category):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT {self.REPORT_COLS} FROM reports WHERE category = ? ORDER BY id DESC",
            (category,),
        )
        reports = cursor.fetchall()
        conn.close()
        return [self._row_to_report(r) for r in reports]

    def get_report_by_id(self, report_id):
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT {self.REPORT_COLS} FROM reports WHERE id = ? LIMIT 1",
            (report_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return self._row_to_report(row) if row else None

    def delete_expired_unresolved_reports(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                DELETE FROM reports
                WHERE expires_at IS NOT NULL
                  AND datetime(expires_at, '+7 days') <= datetime(CURRENT_TIMESTAMP)
                  AND LOWER(status) NOT IN ('resolved', 'rejected')
                """
            )
            conn.commit()
        finally:
            conn.close()

    def extend_report_expiration(self, report_id, days=7):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE reports
                SET expires_at = datetime(COALESCE(expires_at, CURRENT_TIMESTAMP), ?)
                WHERE id = ?
                """,
                (f"+{int(days)} days", report_id),
            )
            conn.commit()
        finally:
            conn.close()

    def _normalize_status(self, new_status):
        return _normalize_status_db(new_status)

    def update_report_status(self, report_id, new_status, remarks=None, updated_by=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        status = self._normalize_status(new_status)

        if remarks is not None:
            cursor.execute(
                """
                UPDATE reports
                SET status = ?, admin_remarks = ?, status_updated_at = CURRENT_TIMESTAMP,
                    status_updated_by = ?
                WHERE id = ?
                """,
                (status, remarks, updated_by, report_id),
            )
        else:
            cursor.execute(
                """
                UPDATE reports
                SET status = ?, status_updated_at = CURRENT_TIMESTAMP,
                    status_updated_by = ?
                WHERE id = ?
                """,
                (status, updated_by, report_id),
            )

        conn.commit()
        conn.close()

    def migrate_statuses_to_canonical(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, status FROM reports")
        rows = cursor.fetchall()

        for rid, value in rows:
            canon = _normalize_status_db(value)
            if canon != (value or "").strip().lower():
                cursor.execute("UPDATE reports SET status = ? WHERE id = ?", (canon, rid))

        conn.commit()
        conn.close()

    def update_report(self, report_id, issue_description, location):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE reports
            SET issue_description = ?, location = ?
            WHERE id = ?
            """,
            (issue_description, location, report_id),
        )
        conn.commit()
        conn.close()

    def delete_report(self, report_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        conn.close()

    def user_exists(self, user_email):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM reports WHERE user_email = ? LIMIT 1", (user_email,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def get_or_create_user(self, email, name, role, picture=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email, name, role, profile_picture FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            conn.close()
            return {"email": user[0], "name": user[1], "role": user[2], "picture": user[3]}

        cursor.execute(
            "INSERT INTO users (email, name, role, profile_picture) VALUES (?, ?, ?, ?)",
            (email, name, role, picture),
        )
        conn.commit()
        conn.close()
        return {"email": email, "name": name, "role": role, "picture": picture}

    def create_or_update_user(self, email, name, role, picture=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        exists = cursor.fetchone()

        if exists:
            if picture:
                cursor.execute(
                    """
                    UPDATE users
                    SET name = ?, role = ?, profile_picture = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE email = ?
                    """,
                    (name, role, picture, email),
                )
            else:
                cursor.execute(
                    """
                    UPDATE users
                    SET name = ?, role = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE email = ?
                    """,
                    (name, role, email),
                )
        else:
            cursor.execute(
                "INSERT INTO users (email, name, role, profile_picture) VALUES (?, ?, ?, ?)",
                (email, name, role, picture),
            )

        conn.commit()
        conn.close()
        return {"email": email, "name": name, "role": role, "picture": picture}

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
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT email, name, role, profile_picture, created_at, updated_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        )
        user = cursor.fetchone()
        conn.close()
        if not user:
            return None
        return {
            "email": user[0],
            "name": user[1],
            "role": user[2],
            "picture": user[3],
            "created_at": user[4],
            "updated_at": user[5],
        }

    def update_user_password(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            """
            UPDATE users
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
            """,
            (password_hash, email),
        )
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0

    def verify_user_password(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
        result = cursor.fetchone()
        conn.close()
        if not result or not result[0]:
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == result[0]

    def get_reports_per_day(self, days=7):
        conn = self.get_connection()
        cursor = conn.cursor()
        window_days = max(int(days) - 1, 0)
        cursor.execute(
            """
            SELECT DATE(COALESCE(created_at, status_updated_at)) as day, COUNT(*) as cnt
            FROM reports
            WHERE DATE(COALESCE(created_at, status_updated_at)) >= DATE('now', ?)
            GROUP BY DATE(COALESCE(created_at, status_updated_at))
            ORDER BY day ASC
            """,
            (f"-{window_days} days",),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"day": r[0], "count": r[1]} for r in rows if r[0]]

    def get_reports_per_category(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(category, 'Uncategorized') as cat, COUNT(*) as cnt
            FROM reports
            GROUP BY cat
            ORDER BY cnt DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"category": r[0], "count": r[1]} for r in rows]

    def get_reports_per_location(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(location, 'Unknown') as loc, COUNT(*) as cnt
            FROM reports
            GROUP BY loc
            ORDER BY cnt DESC
            LIMIT 10
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"location": r[0], "count": r[1]} for r in rows]

    def get_resolution_rate(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reports")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM reports WHERE LOWER(status) IN ('resolved', 'fixed')")
        resolved = cursor.fetchone()[0]
        conn.close()
        return {"total": total, "resolved": resolved, "rate": round(resolved / total * 100, 1) if total > 0 else 0}

    def get_total_users_count(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_top_reporters(self, limit=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT user_name, user_email, COUNT(*) as cnt
            FROM reports
            GROUP BY user_email, user_name
            ORDER BY cnt DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [{"name": r[0], "email": r[1], "count": r[2]} for r in rows]


class _SupabaseBackend:
    def __init__(self, supabase_url: str, supabase_key: str) -> None:
        self.supabase_url = supabase_url.rstrip("/")
        self.supabase_key = supabase_key
        self.base_url = f"{self.supabase_url}/rest/v1"

    def get_connection(self):
        raise RuntimeError("Direct database connections are not available in Supabase mode.")

    def _headers(self, prefer: str = "return=minimal"):
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": prefer,
        }

    def _request_json(self, method: str, path: str, *, params=None, payload=None, prefer: str = "return=minimal"):
        response = requests.request(
            method,
            f"{self.base_url}/{path.lstrip('/')}",
            headers=self._headers(prefer=prefer),
            params=params,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        if not response.text:
            return []
        try:
            return response.json()
        except ValueError:
            return []

    def _select(self, table: str, columns: str = "*", filters: Optional[Dict[str, str]] = None, order: Optional[str] = None):
        params: Dict[str, str] = {"select": columns}
        if filters:
            params.update(filters)
        if order:
            params["order"] = order
        return self._request_json("GET", table, params=params, prefer="return=representation")

    def _fetch_one(self, table: str, filters: Dict[str, str], columns: str = "*") -> Optional[Dict[str, Any]]:
        rows = self._select(table, columns=columns, filters=filters)
        return rows[0] if rows else None

    def _insert(self, table: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = self._request_json(
            "POST",
            table,
            payload=payload,
            prefer="return=representation",
        )
        if isinstance(data, list):
            return data[0] if data else {}
        return data if isinstance(data, dict) else {}

    def _upsert(self, table: str, payload: Dict[str, Any], conflict: str) -> Dict[str, Any]:
        data = self._request_json(
            "POST",
            table,
            params={"on_conflict": conflict},
            payload=payload,
            prefer="resolution=merge-duplicates,return=representation",
        )
        if isinstance(data, list):
            return data[0] if data else {}
        return data if isinstance(data, dict) else {}

    def _update(self, table: str, filters: Dict[str, str], payload: Dict[str, Any]):
        self._request_json("PATCH", table, params=filters, payload=payload)

    def _delete(self, table: str, filters: Dict[str, str]):
        self._request_json("DELETE", table, params=filters)

    def _report_from_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return _report_dict_from_api(row)

    def add_report(self, user_email, user_name, user_type, issue_description, location, category="Uncategorized", report_image=None, expires_days: int = 30):
        payload = {
            "user_email": user_email,
            "user_name": user_name,
            "user_type": user_type,
            "issue_description": issue_description,
            "location": location,
            "category": category,
            "status": "pending",
            "report_image": report_image,
            "created_at": _to_iso(_now_utc()),
            "expires_at": _to_iso(_now_utc() + timedelta(days=int(expires_days))),
        }
        row = self._insert("reports", payload)
        return row.get("id")

    def get_all_reports(self):
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        rows = self._select("reports", order="id.desc")
        return [self._report_from_row(row) for row in rows]

    def get_reports_by_user(self, user_email):
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        rows = self._select("reports", filters={"user_email": f"eq.{user_email}"}, order="id.desc")
        return [self._report_from_row(row) for row in rows]

    def get_reports_by_category(self, category):
        rows = self._select("reports", filters={"category": f"eq.{category}"}, order="id.desc")
        return [self._report_from_row(row) for row in rows]

    def get_report_by_id(self, report_id):
        try:
            self.delete_expired_unresolved_reports()
        except Exception:
            pass
        row = self._fetch_one("reports", {"id": f"eq.{report_id}"})
        return self._report_from_row(row) if row else None

    def delete_expired_unresolved_reports(self):
        rows = self._select("reports", columns="id, status, expires_at")
        now = _now_utc()
        for row in rows:
            expires_at = _parse_dt(row.get("expires_at"))
            status = (row.get("status") or "").strip().lower()
            if expires_at and expires_at + timedelta(days=7) <= now and status not in {"resolved", "rejected"}:
                self._delete("reports", {"id": f"eq.{row['id']}"})

    def extend_report_expiration(self, report_id, days=7):
        row = self._fetch_one("reports", {"id": f"eq.{report_id}"}, columns="id, expires_at")
        if not row:
            return
        expires_at = _parse_dt(row.get("expires_at")) or _now_utc()
        updated = expires_at + timedelta(days=int(days))
        self._update("reports", {"id": f"eq.{report_id}"}, {"expires_at": _to_iso(updated)})

    def _normalize_status(self, new_status):
        return _normalize_status_db(new_status)

    def update_report_status(self, report_id, new_status, remarks=None, updated_by=None):
        payload = {
            "status": self._normalize_status(new_status),
            "status_updated_at": _to_iso(_now_utc()),
            "status_updated_by": updated_by,
        }
        if remarks is not None:
            payload["admin_remarks"] = remarks
        self._update("reports", {"id": f"eq.{report_id}"}, payload)

    def migrate_statuses_to_canonical(self):
        rows = self._select("reports", columns="id, status")
        for row in rows:
            canon = self._normalize_status(row.get("status"))
            if canon != (row.get("status") or "").strip().lower():
                self._update("reports", {"id": f"eq.{row['id']}"}, {"status": canon})

    def update_report(self, report_id, issue_description, location):
        self._update("reports", {"id": f"eq.{report_id}"}, {"issue_description": issue_description, "location": location})

    def delete_report(self, report_id):
        self._delete("reports", {"id": f"eq.{report_id}"})

    def user_exists(self, user_email):
        row = self._fetch_one("reports", {"user_email": f"eq.{user_email}"}, columns="id")
        return row is not None

    def get_or_create_user(self, email, name, role, picture=None):
        row = self._fetch_one("users", {"email": f"eq.{email}"})
        if row:
            return {"email": row.get("email"), "name": row.get("name"), "role": row.get("role"), "picture": row.get("profile_picture")}
        return self.create_or_update_user(email, name, role, picture)

    def create_or_update_user(self, email, name, role, picture=None):
        payload = {"email": email, "name": name, "role": role, "profile_picture": picture}
        row = self._upsert("users", payload, conflict="email")
        if row:
            return {"email": row.get("email", email), "name": row.get("name", name), "role": row.get("role", role), "picture": row.get("profile_picture", picture)}
        return {"email": email, "name": name, "role": role, "picture": picture}

    def update_user_profile(self, email, name=None, profile_picture=None):
        updates: Dict[str, Any] = {}
        if name is not None:
            updates["name"] = name
        if profile_picture is not None:
            updates["profile_picture"] = profile_picture
        if not updates:
            return False
        updates["updated_at"] = _to_iso(_now_utc())
        self._update("users", {"email": f"eq.{email}"}, updates)
        return True

    def get_user_by_email(self, email):
        row = self._fetch_one("users", {"email": f"eq.{email}"})
        if not row:
            return None
        return {
            "email": row.get("email"),
            "name": row.get("name"),
            "role": row.get("role"),
            "picture": row.get("profile_picture"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    def update_user_password(self, email, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self._update("users", {"email": f"eq.{email}"}, {"password_hash": password_hash, "updated_at": _to_iso(_now_utc())})
        return True

    def verify_user_password(self, email, password):
        row = self._fetch_one("users", {"email": f"eq.{email}"}, columns="password_hash")
        if not row or not row.get("password_hash"):
            return False
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == row.get("password_hash")

    def get_reports_per_day(self, days=7):
        rows = self._select("reports", columns="created_at, status_updated_at")
        window_start = (_now_utc() - timedelta(days=max(int(days) - 1, 0))).date()
        counts = Counter()
        for row in rows:
            dt = _parse_dt(row.get("created_at")) or _parse_dt(row.get("status_updated_at"))
            if dt and dt.date() >= window_start:
                counts[str(dt.date())] += 1
        return [{"day": day, "count": count} for day, count in sorted(counts.items())]

    def get_reports_per_category(self):
        rows = self._select("reports", columns="category")
        counts = Counter((row.get("category") or "Uncategorized") for row in rows)
        return [{"category": category, "count": count} for category, count in counts.most_common()]

    def get_reports_per_location(self):
        rows = self._select("reports", columns="location")
        counts = Counter((row.get("location") or "Unknown") for row in rows)
        return [{"location": location, "count": count} for location, count in counts.most_common(10)]

    def get_resolution_rate(self):
        rows = self._select("reports", columns="status")
        total = len(rows)
        resolved = sum(1 for row in rows if (row.get("status") or "").strip().lower() in {"resolved", "fixed"})
        return {"total": total, "resolved": resolved, "rate": round(resolved / total * 100, 1) if total > 0 else 0}

    def get_total_users_count(self):
        rows = self._select("users", columns="id")
        return len(rows)

    def get_top_reporters(self, limit=5):
        rows = self._select("reports", columns="user_name, user_email")
        counts = Counter((row.get("user_name"), row.get("user_email")) for row in rows)
        top = counts.most_common(int(limit))
        return [{"name": name, "email": email, "count": count} for (name, email), count in top]

    def init_database(self):
        return None


class Database:
    def __init__(self, db_name="app_database.db"):
        self.db_name = db_name
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        use_sqlite = bool(db_name and db_name != "app_database.db") or not (self.supabase_url and self.supabase_key)
        if use_sqlite:
            self.backend = _SQLiteBackend(db_name)
        else:
            self.backend = _SupabaseBackend(self.supabase_url, self.supabase_key)

    def __getattr__(self, name):
        return getattr(self.backend, name)

    def get_connection(self):
        return self.backend.get_connection()


db = Database()
