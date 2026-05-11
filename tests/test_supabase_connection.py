"""Supabase connection verification script.

This file lives under tests/ so it is organized with the other test assets,
but it is not a pytest test module. It can still be run manually.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.database.database import db

__test__ = False


def main() -> None:
    load_dotenv()

    print("=" * 60)
    print("SUPABASE VERIFICATION CHECK")
    print("=" * 60)

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    print("\n1. CHECKING ENVIRONMENT VARIABLES:")
    print(f"   SUPABASE_URL: {supabase_url if supabase_url else '❌ NOT FOUND'}")
    print(f"   SUPABASE_KEY: {supabase_key[:20]}... (hidden)" if supabase_key else "   SUPABASE_KEY: ❌ NOT FOUND")

    if not supabase_url or not supabase_key:
        print("\n   ⚠️  WARNING: Supabase credentials not found in .env!")
        print("   App will fall back to SQLite mode.")

    print("\n2. CHECKING ACTIVE DATABASE BACKEND:")
    try:
        backend_type = type(db.backend).__name__

        if "_SupabaseBackend" in backend_type:
            print("   ✅ USING SUPABASE (REST API)")
            print(f"   Supabase URL: {supabase_url}")
        elif "_SQLiteBackend" in backend_type:
            print("   ⚠️  USING SQLITE (Local Database)")
            print("   This means Supabase is NOT being used!")
        else:
            print(f"   ❓ Unknown backend: {backend_type}")

        print("\n3. CHECKING DATA IN DATABASE:")
        all_reports = db.get_all_reports()
        users_count = db.get_total_users_count()

        print(f"   Reports count: {len(all_reports)}")
        print(f"   Users count: {users_count}")

        if len(all_reports) == 4 and users_count == 4:
            print("   ✅ Data matches migrated Supabase data!")
        else:
            print("   ⚠️  Data count mismatch. Check if migration was successful.")

        print("\n" + "=" * 60)
        if "_SupabaseBackend" in backend_type:
            print("✅ SUCCESS: You are using Supabase!")
        else:
            print("❌ NOT USING SUPABASE: Still using SQLite fallback")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        print("\nTroubleshooting:")
        print("   • Verify .env file exists with Supabase credentials")
        print("   • Check Supabase project exists and is accessible")
        print("   • Verify network connectivity")


if __name__ == "__main__":
    main()
