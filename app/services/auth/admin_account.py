ADMIN_ACCOUNT = {
    "email": "admin@example.com",
    "password": "admin123",
    "name": "Admin"
}

def validate_admin_credentials(email, password):
    if email == ADMIN_ACCOUNT["email"] and password == ADMIN_ACCOUNT["password"]:
        return ADMIN_ACCOUNT
    return None