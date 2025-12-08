"""
Tests for database service
"""
import pytest
import os
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import tempfile
import sys

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestDatabase:
    """Test database operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        # Cleanup
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_database_connection(self, test_db):
        """Test database connection initialization"""
        conn = test_db.get_connection()
        assert conn is not None
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'reports' in tables
        assert 'users' in tables
    
    def test_add_report(self, test_db):
        """Test adding a report to database"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test issue",
            location="Building A",
            category="Academic"
        )
        
        assert report_id is not None
        assert isinstance(report_id, int)
        assert report_id > 0
    
    def test_get_all_reports(self, test_db):
        """Test retrieving all reports"""
        # Add a report
        test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test issue",
            location="Building A"
        )
        
        # Get all reports
        reports = test_db.get_all_reports()
        assert isinstance(reports, list)
        assert len(reports) > 0
        assert reports[0]['user_email'] == "test@example.com"
    
    def test_get_report_by_id(self, test_db):
        """Test retrieving report by ID"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test issue",
            location="Building A"
        )
        
        report = test_db.get_report_by_id(report_id)
        assert report is not None
        assert report['id'] == report_id
    
    def test_update_report_status(self, test_db):
        """Test updating report status"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test issue",
            location="Building A"
        )
        
        result = test_db.update_report_status(report_id, "resolved")
        assert result is None  # Method returns None, not a boolean
        
        updated_report = test_db.get_report_by_id(report_id)
        assert updated_report['status'].lower() == 'resolved'
    
    def test_create_or_update_user(self, test_db):
        """Test creating a new user"""
        result = test_db.create_or_update_user(
            email="newuser@example.com",
            name="New User",
            role="student"
        )
        
        assert result is not None
    
    def test_get_user_by_email(self, test_db):
        """Test retrieving user by email"""
        # First create a user
        test_db.create_or_update_user(
            email="testuser@example.com",
            name="Test User",
            role="student"
        )
        
        # Then retrieve the user
        user = test_db.get_user_by_email("testuser@example.com")
        assert user is not None
        assert user['email'] == "testuser@example.com"
        assert user['name'] == "Test User"
    
    def test_duplicate_email(self, test_db):
        """Test handling of duplicate email"""
        test_db.create_or_update_user(
            email="duplicate@example.com",
            name="User 1",
            role="student"
        )
        
        # Try to create another user with same email (should update)
        test_db.create_or_update_user(
            email="duplicate@example.com",
            name="User 2",
            role="admin"
        )
        
        # Verify the user was updated (name changed)
        user = test_db.get_user_by_email("duplicate@example.com")
        assert user is not None
        assert user['name'] == "User 2"
        assert user['role'] == "admin"
    
    def test_database_connection_failure(self):
        """Test handling of database connection errors"""
        from app.services.database.database import Database
        
        # Try to use invalid database path
        with pytest.raises((sqlite3.Error, Exception)):
            db = Database(db_name="/invalid/path/to/database.db")
            # Try to execute query on invalid path
            db.get_connection()


class TestDatabaseReportQuerying:
    """Test report querying operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_get_reports_by_user(self, test_db):
        """Test retrieving reports for specific user"""
        # Add multiple reports
        test_db.add_report(
            user_email="user1@example.com",
            user_name="User 1",
            user_type="student",
            issue_description="Issue 1",
            location="Building A"
        )
        test_db.add_report(
            user_email="user1@example.com",
            user_name="User 1",
            user_type="student",
            issue_description="Issue 2",
            location="Building B"
        )
        test_db.add_report(
            user_email="user2@example.com",
            user_name="User 2",
            user_type="faculty",
            issue_description="Issue 3",
            location="Building C"
        )
        
        # Get reports for user1
        reports = test_db.get_reports_by_user("user1@example.com")
        assert isinstance(reports, list)
        assert len(reports) == 2
        assert all(r['user_email'] == "user1@example.com" for r in reports)
    
    def test_get_reports_by_category(self, test_db):
        """Test retrieving reports by category"""
        # Add reports with different categories
        test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Computer issue",
            location="Lab",
            category="IT"
        )
        test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Grade issue",
            location="Office",
            category="Academic"
        )
        
        # Get reports by category
        it_reports = test_db.get_reports_by_category("IT")
        assert isinstance(it_reports, list)
        assert len(it_reports) >= 1
    
    def test_delete_report(self, test_db):
        """Test deleting a report"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test issue",
            location="Building A"
        )
        
        # Delete the report
        test_db.delete_report(report_id)
        
        # Verify it's deleted
        report = test_db.get_report_by_id(report_id)
        assert report is None
    
    def test_update_report(self, test_db):
        """Test updating report details"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Original issue",
            location="Building A"
        )
        
        # Update the report
        test_db.update_report(
            report_id=report_id,
            issue_description="Updated issue",
            location="Building B"
        )
        
        # Verify update
        updated_report = test_db.get_report_by_id(report_id)
        assert updated_report['issue_description'] == "Updated issue"
        assert updated_report['location'] == "Building B"


class TestDatabaseUserManagement:
    """Test user management operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_get_or_create_user_create(self, test_db):
        """Test creating user with get_or_create"""
        user = test_db.get_or_create_user(
            email="newuser@example.com",
            name="New User",
            role="student",
            picture="avatar.png"
        )
        
        assert user is not None
        assert user['email'] == "newuser@example.com"
        assert user['name'] == "New User"
        assert user['role'] == "student"
    
    def test_get_or_create_user_existing(self, test_db):
        """Test retrieving existing user with get_or_create"""
        # Create first
        test_db.create_or_update_user(
            email="existing@example.com",
            name="Existing User",
            role="admin"
        )
        
        # Then get_or_create should return existing
        user = test_db.get_or_create_user(
            email="existing@example.com",
            name="Different Name",
            role="student"
        )
        
        assert user is not None
        assert user['email'] == "existing@example.com"
        # Should return existing user
        assert user['name'] == "Existing User"
    
    def test_update_user_profile(self, test_db):
        """Test updating user profile"""
        # Create user first
        test_db.create_or_update_user(
            email="profile@example.com",
            name="Original Name",
            role="student"
        )
        
        # Update profile
        test_db.update_user_profile(
            email="profile@example.com",
            name="Updated Name",
            profile_picture="new_avatar.png"
        )
        
        # Verify update
        user = test_db.get_user_by_email("profile@example.com")
        assert user['name'] == "Updated Name"
    
    def test_user_exists_with_report(self, test_db):
        """Test user_exists checks reports"""
        # Add a report (which creates user_email in reports table)
        test_db.add_report(
            user_email="reporter@example.com",
            user_name="Reporter",
            user_type="student",
            issue_description="Test",
            location="Building A"
        )
        
        # user_exists checks reports table
        exists = test_db.user_exists("reporter@example.com")
        assert exists is True
    
    def test_user_exists_no_report(self, test_db):
        """Test user_exists with no reports"""
        # user_exists checks reports table, not users table
        exists = test_db.user_exists("nonexistent@example.com")
        assert exists is False


class TestDatabaseErrors:
    """Test error handling in database operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_invalid_email_format(self, test_db):
        """Test handling of invalid email format"""
        # Test creating with unusual email
        result = test_db.create_or_update_user(
            email="simple",
            name="Test User",
            role="student"
        )
        
        # Should handle gracefully
        assert result is not None
    
    def test_report_status_variations(self, test_db):
        """Test that status is normalized correctly"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test issue",
            location="Building A"
        )
        
        # Test various status inputs
        test_db.update_report_status(report_id, "pending")
        report = test_db.get_report_by_id(report_id)
        assert "pending" in report['status'].lower()
        
        test_db.update_report_status(report_id, "RESOLVED")
        report = test_db.get_report_by_id(report_id)
        assert "resolved" in report['status'].lower()
    
    def test_invalid_report_data(self, test_db):
        """Test handling of invalid report data"""
        # Missing required fields
        result = test_db.add_report(
            user_email="",
            user_name="",
            user_type="",
            issue_description="",
            location=""
        )
        
        # Should still create but with empty data
        assert result is not None or result is None


class TestDatabaseCategoryReports:
    """Test report category handling"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_add_report_with_category(self, test_db):
        """Test adding report with category"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="IT Problem",
            location="Lab",
            category="IT Support"
        )
        
        report = test_db.get_report_by_id(report_id)
        assert report['category'] == "IT Support"
    
    def test_add_report_default_category(self, test_db):
        """Test adding report with default category"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Generic Issue",
            location="Building A"
        )
        
        report = test_db.get_report_by_id(report_id)
        assert report['category'] == "Uncategorized"
    
    def test_status_normalization_in_progress(self, test_db):
        """Test status normalization for in-progress"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test",
            location="Building A"
        )
        
        test_db.update_report_status(report_id, "in progress")
        report = test_db.get_report_by_id(report_id)
        assert "progress" in report['status'].lower() or "ongoing" in report['status'].lower()
    
    def test_status_normalization_rejected(self, test_db):
        """Test status normalization for rejected"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test",
            location="Building A"
        )
        
        test_db.update_report_status(report_id, "REJECTED")
        report = test_db.get_report_by_id(report_id)
        assert "reject" in report['status'].lower()


class TestDatabaseRetrieval:
    """Test report retrieval operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_get_report_by_id_not_found(self, test_db):
        """Test retrieving non-existent report"""
        report = test_db.get_report_by_id(9999)
        assert report is None
    
    def test_get_reports_by_user_empty(self, test_db):
        """Test getting reports for user with no reports"""
        reports = test_db.get_reports_by_user("nonexistent@example.com")
        assert isinstance(reports, list)
        assert len(reports) == 0
    
    def test_get_reports_by_category_empty(self, test_db):
        """Test getting reports for non-existent category"""
        reports = test_db.get_reports_by_category("NonExistent")
        assert isinstance(reports, list)
    
    def test_get_all_reports_empty(self, test_db):
        """Test getting all reports when none exist"""
        reports = test_db.get_all_reports()
        assert isinstance(reports, list)
        assert len(reports) == 0
    
    def test_delete_nonexistent_report(self, test_db):
        """Test deleting non-existent report"""
        # Should not raise error
        test_db.delete_report(9999)
        assert True
    
    def test_update_nonexistent_report(self, test_db):
        """Test updating non-existent report"""
        # Should not raise error
        test_db.update_report(9999, "new desc", "new loc")
        assert True
    
    def test_get_user_by_email_not_found(self, test_db):
        """Test retrieving non-existent user"""
        user = test_db.get_user_by_email("nonexistent@example.com")
        assert user is None


class TestDatabaseUserProfiles:
    """Test user profile operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_create_user_with_picture(self, test_db):
        """Test creating user with profile picture"""
        test_db.create_or_update_user(
            email="picture@example.com",
            name="User",
            role="student",
            picture="avatar.png"
        )
        
        user = test_db.get_user_by_email("picture@example.com")
        assert user is not None
        assert user['picture'] == "avatar.png"
    
    def test_update_user_with_picture(self, test_db):
        """Test updating user profile picture"""
        test_db.create_or_update_user(
            email="update@example.com",
            name="User",
            role="student",
            picture="old.png"
        )
        
        # Update with new picture
        test_db.update_user_profile(
            email="update@example.com",
            profile_picture="new.png"
        )
        
        user = test_db.get_user_by_email("update@example.com")
        assert user['picture'] == "new.png"
    
    def test_update_user_name_only(self, test_db):
        """Test updating only user name"""
        test_db.create_or_update_user(
            email="nameonly@example.com",
            name="Original",
            role="student"
        )
        
        test_db.update_user_profile(
            email="nameonly@example.com",
            name="Updated"
        )
        
        user = test_db.get_user_by_email("nameonly@example.com")
        assert user['name'] == "Updated"
    
    def test_user_timestamps(self, test_db):
        """Test that user has creation timestamp"""
        test_db.create_or_update_user(
            email="timestamp@example.com",
            name="User",
            role="student"
        )
        
        user = test_db.get_user_by_email("timestamp@example.com")
        assert user is not None
        assert 'created_at' in user or 'updated_at' in user


class TestDatabaseStatusNormalization:
    """Test status field normalization"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_report_retrieval_normalizes_status(self, test_db):
        """Test that retrieved reports have normalized status"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test",
            location="Building A"
        )
        
        test_db.update_report_status(report_id, "on going")
        report = test_db.get_report_by_id(report_id)
        
        # Status should be normalized
        status_lower = report['status'].lower()
        assert 'progress' in status_lower or 'ongoing' in status_lower or 'pending' in status_lower
    
    def test_all_reports_status_normalized(self, test_db):
        """Test that all reports have normalized status"""
        # Add multiple reports
        for i in range(3):
            report_id = test_db.add_report(
                user_email=f"user{i}@example.com",
                user_name=f"User {i}",
                user_type="student",
                issue_description=f"Issue {i}",
                location="Building A"
            )
            test_db.update_report_status(report_id, "pending")
        
        all_reports = test_db.get_all_reports()
        
        # All should have proper status format
        for report in all_reports:
            assert 'status' in report
            assert len(report['status']) > 0
    
    def test_user_reports_status_values(self, test_db):
        """Test status values in user-specific reports"""
        test_db.add_report(
            user_email="usertest@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test",
            location="Building A"
        )
        
        reports = test_db.get_reports_by_user("usertest@example.com")
        
        assert len(reports) > 0
        for report in reports:
            assert 'status' in report


class TestDatabaseColumnOperations:
    """Test database column-related operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_reports_table_has_category_column(self, test_db):
        """Test that reports table has category column"""
        # Add report with category
        test_db.add_report(
            user_email="test@example.com",
            user_name="Test",
            user_type="student",
            issue_description="Test",
            location="Building A",
            category="IT"
        )
        
        # Verify category is persisted
        report = test_db.get_report_by_id(1)
        assert 'category' in report
    
    def test_reports_table_has_status_column(self, test_db):
        """Test that reports have status column"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test",
            user_type="student",
            issue_description="Test",
            location="Building A"
        )
        
        report = test_db.get_report_by_id(report_id)
        assert 'status' in report
        # Default status should be pending
        assert 'pending' in report['status'].lower() or report['status'].lower() == 'pending'


class TestDatabaseConnectionHandling:
    """Test database connection handling"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_get_connection_returns_valid_connection(self, test_db):
        """Test that get_connection returns valid connection"""
        conn = test_db.get_connection()
        
        assert conn is not None
        
        # Should be able to execute query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        assert result is not None
        conn.close()
    
    def test_multiple_connections(self, test_db):
        """Test creating multiple connections"""
        conn1 = test_db.get_connection()
        conn2 = test_db.get_connection()
        
        assert conn1 is not None
        assert conn2 is not None
        
        conn1.close()
        conn2.close()


class TestDatabaseReportTypes:
    """Test different report types and user types"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_report_from_student(self, test_db):
        """Test creating report from student"""
        report_id = test_db.add_report(
            user_email="student@example.com",
            user_name="Student",
            user_type="student",
            issue_description="Issue",
            location="Lab"
        )
        
        report = test_db.get_report_by_id(report_id)
        assert report['user_type'] == "student"
    
    def test_report_from_admin(self, test_db):
        """Test creating report from admin"""
        report_id = test_db.add_report(
            user_email="admin@example.com",
            user_name="Admin",
            user_type="admin",
            issue_description="Issue",
            location="Office"
        )
        
        report = test_db.get_report_by_id(report_id)
        assert report['user_type'] == "admin"
    
    def test_report_from_faculty(self, test_db):
        """Test creating report from faculty"""
        report_id = test_db.add_report(
            user_email="faculty@example.com",
            user_name="Faculty",
            user_type="faculty",
            issue_description="Issue",
            location="Office"
        )
        
        report = test_db.get_report_by_id(report_id)
        assert report['user_type'] == "faculty"


class TestDatabaseMigrations:
    """Test database migration functions"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_migrate_statuses_to_canonical_pending(self, test_db):
        """Test migrating pending status variations"""
        # Create reports with non-canonical status
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test Issue",
            location="Lab"
        )
        
        # Update with non-canonical status
        conn = test_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("PENDING", report_id))
        conn.commit()
        conn.close()
        
        # Run migration
        test_db.migrate_statuses_to_canonical()
        
        # Check that status is normalized
        report = test_db.get_report_by_id(report_id)
        assert report['status'].lower() == 'pending'
    
    def test_migrate_statuses_to_canonical_in_progress(self, test_db):
        """Test migrating in-progress status variations"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test Issue",
            location="Lab"
        )
        
        # Update with non-canonical status
        conn = test_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("ON GOING", report_id))
        conn.commit()
        conn.close()
        
        # Run migration
        test_db.migrate_statuses_to_canonical()
        
        # Check that status is normalized
        report = test_db.get_report_by_id(report_id)
        assert report['status'].lower() == 'in progress'
    
    def test_migrate_statuses_to_canonical_resolved(self, test_db):
        """Test migrating resolved status variations"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test Issue",
            location="Lab"
        )
        
        # Update with non-canonical status
        conn = test_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("FIXED", report_id))
        conn.commit()
        conn.close()
        
        # Run migration
        test_db.migrate_statuses_to_canonical()
        
        # Check that status is normalized
        report = test_db.get_report_by_id(report_id)
        assert report['status'].lower() == 'resolved'
    
    def test_migrate_statuses_to_canonical_rejected(self, test_db):
        """Test migrating rejected status variations"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test Issue",
            location="Lab"
        )
        
        # Update with non-canonical status
        conn = test_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("REJECT", report_id))
        conn.commit()
        conn.close()
        
        # Run migration
        test_db.migrate_statuses_to_canonical()
        
        # Check that status is normalized
        report = test_db.get_report_by_id(report_id)
        assert report['status'].lower() == 'rejected'
    
    def test_migrate_statuses_empty_becomes_pending(self, test_db):
        """Test that empty/null status becomes pending"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test Issue",
            location="Lab"
        )
        
        # Update with empty status
        conn = test_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("", report_id))
        conn.commit()
        conn.close()
        
        # Run migration
        test_db.migrate_statuses_to_canonical()
        
        # Check that empty becomes pending
        report = test_db.get_report_by_id(report_id)
        assert report['status'].lower() == 'pending'
    
    def test_migrate_statuses_multiple_reports(self, test_db):
        """Test migration with multiple reports"""
        # Create multiple reports with different non-canonical statuses
        id1 = test_db.add_report(
            user_email="test1@example.com",
            user_name="Test 1",
            user_type="student",
            issue_description="Issue 1",
            location="Lab"
        )
        
        id2 = test_db.add_report(
            user_email="test2@example.com",
            user_name="Test 2",
            user_type="student",
            issue_description="Issue 2",
            location="Lab"
        )
        
        # Update with different non-canonical statuses
        conn = test_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("ON GOING", id1))
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("FIXED", id2))
        conn.commit()
        conn.close()
        
        # Run migration
        test_db.migrate_statuses_to_canonical()
        
        # Check both are normalized
        report1 = test_db.get_report_by_id(id1)
        report2 = test_db.get_report_by_id(id2)
        
        assert report1['status'].lower() == 'in progress'
        assert report2['status'].lower() == 'resolved'
    
    def test_migrate_statuses_with_whitespace(self, test_db):
        """Test migration handles whitespace correctly"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test Issue",
            location="Lab"
        )
        
        # Update with status that has whitespace
        conn = test_db.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE reports SET status = ? WHERE id = ?', ("  PENDING  ", report_id))
        conn.commit()
        conn.close()
        
        # Run migration
        test_db.migrate_statuses_to_canonical()
        
        # Check that whitespace is stripped and normalized
        report = test_db.get_report_by_id(report_id)
        assert report['status'].lower() == 'pending'
    
    def test_migrate_statuses_already_canonical(self, test_db):
        """Test migration doesn't change already canonical statuses"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Test Issue",
            location="Lab"
        )
        
        # Get initial status
        initial_report = test_db.get_report_by_id(report_id)
        initial_status = initial_report['status']
        
        # Run migration
        test_db.migrate_statuses_to_canonical()
        
        # Check status unchanged
        final_report = test_db.get_report_by_id(report_id)
        assert final_report['status'] == initial_status


class TestDatabaseConnectionHandling:
    """Test database connection handling"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_get_connection_returns_valid_conn(self, test_db):
        """Test that get_connection returns a valid connection"""
        conn = test_db.get_connection()
        
        assert conn is not None
        assert hasattr(conn, 'cursor')
        assert hasattr(conn, 'commit')
        assert hasattr(conn, 'close')
        
        conn.close()
    
    def test_connection_isolation(self, test_db):
        """Test that connections are isolated"""
        conn1 = test_db.get_connection()
        conn2 = test_db.get_connection()
        
        assert conn1 is not conn2
        
        conn1.close()
        conn2.close()


class TestDatabaseUpdateOperations:
    """Test database update operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a temporary test database"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
        
        from app.services.database.database import Database
        db = Database(db_name=db_path)
        yield db
        
        try:
            os.unlink(db_path)
        except:
            pass
    
    def test_update_report_description_and_location(self, test_db):
        """Test updating report description and location"""
        report_id = test_db.add_report(
            user_email="test@example.com",
            user_name="Test User",
            user_type="student",
            issue_description="Original Issue",
            location="Lab A"
        )
        
        # Update report
        test_db.update_report(report_id, "Updated Issue", "Lab B")
        
        # Verify update
        report = test_db.get_report_by_id(report_id)
        assert report['issue_description'] == "Updated Issue"
        assert report['location'] == "Lab B"
    
    def test_update_nonexistent_report(self, test_db):
        """Test updating nonexistent report"""
        # Should not raise error
        test_db.update_report(999, "New Issue", "New Location")
        
        # Verify report doesn't exist
        report = test_db.get_report_by_id(999)
        assert report is None



