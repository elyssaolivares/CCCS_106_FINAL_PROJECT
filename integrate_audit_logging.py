import os
import re

def patch_loginpage():
    """Patch loginpage.py to add audit logging."""
    
    loginpage_path = "app/views/loginpage.py"
    
    if not os.path.exists(loginpage_path):
        return False
    
    with open(loginpage_path, 'r') as f:
        content = f.read()
    
    # Step 1: Add audit_logger import if not already present
    if "from app.services.audit.audit_logger import audit_logger" not in content:
        # Find the import section
        import_pattern = r'(from app\.services\.database\.database import db\n)'
        replacement = r'\1from app.services.audit.audit_logger import audit_logger\n'
        content = re.sub(import_pattern, replacement, content)
    
    # Step 2: Add logging for failed role check in login_clicked
    if 'audit_logger.log_action(email, email, "login_attempt"' not in content:
        # Find the "Account not existed" section and add logging
        pattern = r'(if role\.lower\(\) in \["student", "faculty"\]:\s+show_snackbar\("Account not existed"\)\s+)'
        replacement = r'\1# Log failed login attempt\n            audit_logger.log_action(email, email, "login_attempt", status="failed", details="Account not existed")\n            '
        content = re.sub(pattern, replacement, content)
    
    # Step 3: Add logging for invalid admin credentials
    pattern = r'(if not admin_account:\s+show_snackbar\("Invalid admin credentials"\)\s+)'
    if not re.search(r'audit_logger\.log_action\(email, email, "login_attempt".*Invalid credentials', content):
        replacement = r'\1# Log failed login\n            audit_logger.log_action(email, email, "login_attempt", status="failed", details="Invalid credentials")\n            '
        content = re.sub(pattern, replacement, content)
        
    # Step 4: Add logging for successful admin login (before admin_dashboard call)
    pattern = r'(# Create or update user in database using preserved name\s+db\.create_or_update_user\(admin_account\["email"\], preserved_name, "admin"\)\s+)'
    if not re.search(r'audit_logger\.log_action.*"login".*admin', content):
        replacement = r'\1\n        # Log successful admin login\n        audit_logger.log_action(admin_account["email"], preserved_name, "login", status="success", details="Admin login successful")\n        '
        content = re.sub(pattern, replacement, content)
        
    # Step 5: Add logging for OAuth login
    pattern = r'(# Create/update user in database using preserved name\s+db\.create_or_update_user\(email, preserved_name, role\.lower\(\)\)\s+)'
    if not re.search(r'audit_logger\.log_action.*oauth.*success', content):
        replacement = r'\1\n            # Log successful OAuth login\n            audit_logger.log_action(email, preserved_name, "login", resource_type="oauth", status="success", details=f"OAuth login as {role}")\n            '
        content = re.sub(pattern, replacement, content)
        
    # Step 6: Add logging for OAuth failure
    pattern = r'(except Exception as ex:\s+show_snackbar\(str\(ex\)\)\s+)'
    if not re.search(r'audit_logger\.log_action.*oauth.*failed', content):
        replacement = r'\1# Log failed OAuth attempt\n            audit_logger.log_action("unknown", "unknown", "login_attempt", resource_type="oauth", status="failed", details=str(ex))\n            '
        content = re.sub(pattern, replacement, content)
        
    # Write the patched content back
    with open(loginpage_path, 'w') as f:
        f.write(content)
    return True

if __name__ == "__main__":
    patch_loginpage()
