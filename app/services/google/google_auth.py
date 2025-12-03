import requests
import webbrowser
from google_auth_oauthlib.flow import Flow
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

CLIENT_SECRETS_FILE = r"C:\Users\user\Documents\FIXIT\app\services\google\client_secret.json"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]
REDIRECT_URI = "http://localhost:8550/api/oauth/redirect"


class OAuthRedirectHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        if "code" in params:
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h3>Login successful! You can close this tab.</h3>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h3>Login failed.</h3>")


def google_oauth_login():
  
    try:
        
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )

        auth_url, _ = flow.authorization_url(prompt="consent")

        webbrowser.open(auth_url)

        server_address = ("", 8550)
        httpd = HTTPServer(server_address, OAuthRedirectHandler)
        httpd.auth_code = None
        print("Waiting for OAuth redirect...")
        httpd.handle_request()  

        if not httpd.auth_code:
            raise Exception("No authorization code received.")

        flow.fetch_token(code=httpd.auth_code)
        creds = flow.credentials

        resp = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {creds.token}"}
        )
        user_info = resp.json()
        email = user_info.get("email")
        name = user_info.get("name")


        if email.endswith("@my.cspc.edu.ph"):
            return {"name": name, "email": email}
        else:
            raise Exception("Use your CSPC school email!")

    except Exception as e:
        raise Exception(f"Google login failed: {str(e)}")


if __name__ == "__main__":
    user = google_oauth_login()
    print("Logged in user:", user)
