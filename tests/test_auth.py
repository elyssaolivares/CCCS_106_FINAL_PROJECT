"""
Tests for authentication service
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestAuthentication:
    """Test authentication operations"""
    
    def test_validate_admin_credentials_valid(self):
        """Test login with valid admin credentials"""
        from app.services.auth.admin_account import validate_admin_credentials
        from app.services.auth.admin_account import ADMIN_EMAIL, _ADMIN_PASSWORD_RAW
        
        # Use environment credentials or defaults
        result = validate_admin_credentials(ADMIN_EMAIL, _ADMIN_PASSWORD_RAW)
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'email' in result
        assert 'name' in result
    
    def test_validate_admin_credentials_invalid_password(self):
        """Test login with invalid credentials"""
        from app.services.auth.admin_account import validate_admin_credentials, ADMIN_EMAIL
        
        result = validate_admin_credentials(ADMIN_EMAIL, "wrongpassword")
        
        assert result is None
    
    def test_validate_admin_credentials_invalid_email(self):
        """Test login with invalid email"""
        from app.services.auth.admin_account import validate_admin_credentials
        
        result = validate_admin_credentials("wrong@example.com", "password")
        
        assert result is None
    
    def test_validate_admin_credentials_empty_email(self):
        """Test login with empty email"""
        from app.services.auth.admin_account import validate_admin_credentials
        
        result = validate_admin_credentials("", "password")
        
        assert result is None
    
    def test_validate_admin_credentials_empty_password(self):
        """Test login with empty password"""
        from app.services.auth.admin_account import validate_admin_credentials
        from app.services.auth.admin_account import ADMIN_EMAIL
        
        result = validate_admin_credentials(ADMIN_EMAIL, "")
        
        assert result is None


class TestPasswordManagement:
    """Test password operations"""
    
    def test_hash_password_consistency(self):
        """Test that password hashing is consistent"""
        from app.services.auth.admin_account import _hash_password
        
        password = "testpassword"
        salt = "testsalt"
        
        hash1 = _hash_password(password, salt)
        hash2 = _hash_password(password, salt)
        
        assert hash1 == hash2
    
    def test_hash_password_different_passwords(self):
        """Test that different passwords produce different hashes"""
        from app.services.auth.admin_account import _hash_password
        
        salt = "testsalt"
        
        hash1 = _hash_password("password1", salt)
        hash2 = _hash_password("password2", salt)
        
        assert hash1 != hash2
    
    def test_hash_password_different_salts(self):
        """Test that different salts produce different hashes"""
        from app.services.auth.admin_account import _hash_password
        
        password = "testpassword"
        
        hash1 = _hash_password(password, "salt1")
        hash2 = _hash_password(password, "salt2")
        
        assert hash1 != hash2
    
    def test_hash_password_none_values(self):
        """Test hash password with None values"""
        from app.services.auth.admin_account import _hash_password
        
        # Should handle None gracefully by treating as empty string
        hash1 = _hash_password(None, None)
        hash2 = _hash_password("", "")
        
        assert hash1 == hash2
        assert isinstance(hash1, str)


class TestOAuthIntegration:
    """Test OAuth integration"""
    
    def test_admin_email_loaded_from_env(self):
        """Test that admin email is loaded from environment"""
        from app.services.auth.admin_account import ADMIN_EMAIL
        
        assert ADMIN_EMAIL is not None
        assert isinstance(ADMIN_EMAIL, str)
    
    def test_admin_name_loaded_from_env(self):
        """Test that admin name is loaded from environment"""
        from app.services.auth.admin_account import ADMIN_NAME
        
        assert ADMIN_NAME is not None
        assert isinstance(ADMIN_NAME, str)
    
    def test_admin_salt_loaded_from_env(self):
        """Test that admin salt is loaded from environment"""
        from app.services.auth.admin_account import ADMIN_SALT
        
        assert ADMIN_SALT is not None
        assert isinstance(ADMIN_SALT, str)
    
    def test_admin_password_hash_generated(self):
        """Test that admin password hash is properly generated"""
        from app.services.auth.admin_account import _STORED_PASSWORD_HASH
        
        assert _STORED_PASSWORD_HASH is not None
        assert isinstance(_STORED_PASSWORD_HASH, str)
        assert len(_STORED_PASSWORD_HASH) > 0
