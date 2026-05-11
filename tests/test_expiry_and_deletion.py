"""Tests for expiry classification and automatic deletion of expired unresolved reports."""
import os
import tempfile

from app.services.database.database import Database


def setup_test_db():
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    db = Database(db_name=db_path)
    return db, db_path


def teardown_test_db(db_path):
    try:
        os.unlink(db_path)
    except Exception:
        pass


def test_delete_expired_unresolved_reports_removes_pending():
    db, path = setup_test_db()
    try:
        rid = db.add_report(
            user_email="a@example.com",
            user_name="A",
            user_type="student",
            issue_description="Will expire",
            location="Lab",
            expires_days=30,
        )

        # Set expires_at to well past the 7-day grace window
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE reports SET expires_at = datetime('now','-8 days') WHERE id = ?", (rid,))
        conn.commit()
        conn.close()

        # Ensure row exists on raw query
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT id FROM reports WHERE id = ?', (rid,))
        assert cur.fetchone() is not None
        conn.close()

        # Perform deletion
        db.delete_expired_unresolved_reports()

        # Now get_report_by_id should return None
        assert db.get_report_by_id(rid) is None
    finally:
        teardown_test_db(path)


def test_do_not_delete_expired_but_resolved():
    db, path = setup_test_db()
    try:
        rid = db.add_report(
            user_email="b@example.com",
            user_name="B",
            user_type="student",
            issue_description="Resolved but expired",
            location="Office",
            expires_days=30,
        )

        # Set expires_at to past
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE reports SET expires_at = datetime('now','-2 days') WHERE id = ?", (rid,))
        conn.commit()
        conn.close()

        # Mark resolved
        db.update_report_status(rid, 'resolved')

        # Run deletion
        db.delete_expired_unresolved_reports()

        # Report should still exist and be resolved
        rep = db.get_report_by_id(rid)
        assert rep is not None
        assert 'resolved' in rep['status'].lower()
    finally:
        teardown_test_db(path)


def test_do_not_delete_within_grace_window():
    db, path = setup_test_db()
    try:
        rid = db.add_report(
            user_email="c@example.com",
            user_name="C",
            user_type="student",
            issue_description="Within grace",
            location="Hall",
            expires_days=30,
        )

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE reports SET expires_at = datetime('now','-2 days') WHERE id = ?", (rid,))
        conn.commit()
        conn.close()

        db.delete_expired_unresolved_reports()

        rep = db.get_report_by_id(rid)
        assert rep is not None
    finally:
        teardown_test_db(path)


def test_extend_report_expiration_pushes_date_forward():
    db, path = setup_test_db()
    try:
        rid = db.add_report(
            user_email="d@example.com",
            user_name="D",
            user_type="student",
            issue_description="Needs extension",
            location="Library",
            expires_days=30,
        )

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE reports SET expires_at = datetime('now','-2 days') WHERE id = ?", (rid,))
        conn.commit()
        conn.close()

        before = db.get_report_by_id(rid)
        assert before is not None
        assert before['expires_at'] is not None

        db.extend_report_expiration(rid, days=7)

        after = db.get_report_by_id(rid)
        assert after is not None
        assert after['expires_at'] is not None
        assert after['expires_at'] != before['expires_at']
    finally:
        teardown_test_db(path)

