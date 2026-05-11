DB objects and organization
===========================

This folder contains SQL used to create and expose audit/activity tables in Supabase.

How to use
-----------
- Open Supabase → SQL Editor
- Paste the contents of `db/create_supabase_tables.sql` and run it (or run the file via psql)
- If PostgREST returns `PGRST205` (`Could not find the table ... in the schema cache`), run:

```sql
notify pgrst, 'reload';
```

Project locations
-----------------
- Migration script: `scripts/migrations/migrate_to_supabase.py` (callable `main()`)
- Verification check: `scripts/checks/test_supabase_connection.py`

Notes
-----
- The repo root contains small shims (`migrate_to_supabase.py`, `test_supabase_connection.py`) that delegate to the organized scripts directory.
- After confirming the Supabase tables are visible, consider removing the local SQLite fallback in `app/services/audit/audit_logger.py` and `app/services/activity/activity_monitor.py` once you're confident in production.
