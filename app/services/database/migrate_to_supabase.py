"""SQLite to Supabase migration script.

This is the organized source-of-truth location for the migration script.
"""

import os
import sqlite3
from typing import Iterable

import requests
from dotenv import load_dotenv

load_dotenv()

sqlite_db = "app_database.db"
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_rest_url = f"{supabase_url.rstrip('/')}" if supabase_url else None
if supabase_rest_url:
    supabase_rest_url = f"{supabase_rest_url}/rest/v1"


def _headers(prefer: str = "return=minimal"):
    return {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def _chunks(items: list[dict], size: int = 100) -> Iterable[list[dict]]:
    for start in range(0, len(items), size):
        yield items[start:start + size]


def migrate_reports():
    """Migrate reports from SQLite to Supabase"""
    print("Starting reports migration...")

    if not supabase_rest_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    try:
        sqlite_conn = sqlite3.connect(sqlite_db)
        sqlite_cursor = sqlite_conn.cursor()

        sqlite_cursor.execute('''
            SELECT id, user_email, user_name, user_type, issue_description, location,
                   report_image, category, status, admin_remarks, status_updated_at,
                   status_updated_by, created_at, expires_at
            FROM reports
        ''')
        reports = sqlite_cursor.fetchall()
        sqlite_conn.close()

        if not reports:
            print("[OK] No reports to migrate")
            return 0

        values = []
        for report in reports:
            values.append({
                "id": report[0],
                "user_email": report[1],
                "user_name": report[2],
                "user_type": report[3],
                "issue_description": report[4],
                "location": report[5],
                "report_image": report[6],
                "category": report[7],
                "status": report[8],
                "admin_remarks": report[9],
                "status_updated_at": report[10],
                "status_updated_by": report[11],
                "created_at": report[12],
                "expires_at": report[13],
            })

        migrated = 0
        for batch in _chunks(values):
            response = requests.post(
                f"{supabase_rest_url}/reports?on_conflict=id",
                headers=_headers(prefer="resolution=merge-duplicates,return=minimal"),
                json=batch,
                timeout=30,
            )
            if not response.ok:
                raise RuntimeError(f"Reports insert failed: {response.status_code} {response.text}")
            migrated += len(batch)

        print(f"[OK] Migrated {migrated} reports")
        return migrated

    except Exception as e:
        print(f"[ERROR] Error migrating reports: {e}")
        return 0


def migrate_users():
    """Migrate users from SQLite to Supabase"""
    print("Starting users migration...")

    if not supabase_rest_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

    try:
        sqlite_conn = sqlite3.connect(sqlite_db)
        sqlite_cursor = sqlite_conn.cursor()

        sqlite_cursor.execute('''
            SELECT id, email, name, role, profile_picture, password_hash, created_at, updated_at
            FROM users
        ''')
        users = sqlite_cursor.fetchall()
        sqlite_conn.close()

        if not users:
            print("[OK] No users to migrate")
            return 0

        values = []
        for user in users:
            values.append({
                "email": user[1],
                "name": user[2],
                "role": user[3],
                "profile_picture": user[4],
                "password_hash": user[5],
                "created_at": user[6],
                "updated_at": user[7],
            })

        migrated = 0
        for batch in _chunks(values):
            response = requests.post(
                f"{supabase_rest_url}/users?on_conflict=email",
                headers=_headers(prefer="resolution=merge-duplicates,return=minimal"),
                json=batch,
                timeout=30,
            )
            if not response.ok:
                raise RuntimeError(f"Users upsert failed: {response.status_code} {response.text}")
            migrated += len(batch)

        print(f"[OK] Migrated {migrated} users")
        return migrated

    except Exception as e:
        print(f"[ERROR] Error migrating users: {e}")
        return 0


def verify_migration():
    """Verify that migration was successful"""
    print("\nVerifying migration...")

    try:
        report_resp = requests.get(
            f"{supabase_rest_url}/reports?select=id",
            headers=_headers(),
            timeout=30,
        )
        if not report_resp.ok:
            raise RuntimeError(f"Reports verification failed: {report_resp.status_code} {report_resp.text}")

        user_resp = requests.get(
            f"{supabase_rest_url}/users?select=id",
            headers=_headers(),
            timeout=30,
        )
        if not user_resp.ok:
            raise RuntimeError(f"Users verification failed: {user_resp.status_code} {user_resp.text}")

        report_count = len(report_resp.json() or [])
        user_count = len(user_resp.json() or [])

        print(f"[OK] Reports in Supabase: {report_count}")
        print(f"[OK] Users in Supabase: {user_count}")

        return report_count, user_count

    except Exception as e:
        print(f"[ERROR] Error verifying migration: {e}")
        return 0, 0


def main():
    print("=" * 50)
    print("SQLite to Supabase Migration")
    print("=" * 50)

    if not os.path.exists(sqlite_db):
        print(f"[ERROR] SQLite database not found: {sqlite_db}")
        return

    if not supabase_rest_url or not supabase_key:
        print("[ERROR] Supabase credentials not found in .env file")
        return

    print(f"Source: SQLite ({sqlite_db})")
    print(f"Target: Supabase API ({supabase_url})")
    print()

    reports_migrated = migrate_reports()
    users_migrated = migrate_users()
    reports_count, users_count = verify_migration()

    print("\n" + "=" * 50)
    print("Migration Complete!")
    print(f"Reports: {reports_migrated} migrated, {reports_count} total in Supabase")
    print(f"Users: {users_migrated} migrated, {users_count} total in Supabase")
    print("=" * 50)


if __name__ == "__main__":
    main()
