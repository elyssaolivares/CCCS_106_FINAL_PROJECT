import os
import json
import tempfile
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

CLIENT_SECRET_JSON = os.environ.get("GOOGLE_CLIENT_SECRET")
if CLIENT_SECRET_JSON:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(CLIENT_SECRET_JSON)
        CLIENT_SECRETS_FILE = f.name
else:
    CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def get_oauth_flow(redirect_uri):
    """Create OAuth flow for server-side auth"""
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_auth_url(redirect_uri):
    """Get the Google OAuth authorization URL"""
    flow = get_oauth_flow(redirect_uri)
    auth_url, state = flow.authorization_url(prompt="consent")
    return auth_url, state

def exchange_code_for_token(code, redirect_uri):
    """Exchange authorization code for access token"""
    flow = get_oauth_flow(redirect_uri)
    flow.fetch_token(code=code)
    creds = flow.credentials
    
    # Get user info
    import requests
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        params={"alt": "json"},
        headers={"Authorization": f"Bearer {creds.token}"}
    )
    user_info = resp.json()
    
    email = user_info.get("email")
    if not email.endswith("@my.cspc.edu.ph"):
        raise Exception("Use your CSPC school email!")
    
    return {
        "name": user_info.get("name"),
        "email": email,
        "picture": user_info.get("picture")
    }