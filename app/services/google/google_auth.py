import requests
import webbrowser
from google_auth_oauthlib.flow import Flow
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

CLIENT_SECRETS_FILE = r"C:\Users\user\Documents\CCCS_106_FINAL_PROJECT\app\services\google\client_secret.json"
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]
REDIRECT_URI = "http://localhost:8550/api/oauth/redirect"


_SUCCESS_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FIXIT &mdash; Login</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Poppins', sans-serif;
    background: #0A1628;
    color: #fff;
    height: 100vh;
    overflow: hidden;
    position: relative;
  }
  /* Subtle radial glow behind card */
  body::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    width: 600px; height: 600px;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(79,195,247,0.08) 0%, transparent 70%);
    pointer-events: none;
  }
  .page {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    position: relative;
    z-index: 1;
  }
  .card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 56px 64px;
    text-align: center;
    max-width: 420px;
    width: 90%;
    animation: fadeUp 0.5s ease-out;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  /* Animated check circle */
  .icon-wrap {
    width: 72px; height: 72px;
    border-radius: 50%;
    background: rgba(79,195,247,0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 28px;
    position: relative;
  }
  .icon-wrap svg {
    width: 36px; height: 36px;
    stroke: #4FC3F7;
    stroke-width: 2.5;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .icon-wrap svg .check-path {
    stroke-dasharray: 36;
    stroke-dashoffset: 36;
    animation: drawCheck 0.45s 0.35s ease-out forwards;
  }
  @keyframes drawCheck {
    to { stroke-dashoffset: 0; }
  }
  .brand {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    margin-bottom: 24px;
  }
  h2 {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #fff;
  }
  .sub {
    font-size: 14px;
    font-weight: 400;
    color: rgba(255,255,255,0.5);
    line-height: 1.6;
    margin-bottom: 32px;
  }
  .divider {
    width: 40px;
    height: 3px;
    background: #4FC3F7;
    border-radius: 3px;
    margin: 0 auto 32px;
  }
  .hint {
    font-size: 12px;
    font-weight: 300;
    color: rgba(255,255,255,0.3);
  }
</style>
<script>
  window.onload = function() {
    try { window.open('', '_self', ''); window.close(); } catch(e) {}
    try { window.close(); } catch(e) {}
  };
</script>
</head>
<body>
  <div class="page">
    <div class="card">
      <div class="brand">F I X I T</div>
      <div class="icon-wrap">
        <svg viewBox="0 0 24 24">
          <path class="check-path" d="M5 13l4 4L19 7"/>
        </svg>
      </div>
      <h2>You're all set</h2>
      <p class="sub">Authentication successful.<br>Heading back to your dashboard.</p>
      <div class="divider"></div>
      <p class="hint">You may safely close this tab.</p>
    </div>
  </div>
</body>
</html>"""

_FAIL_HTML = b"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FIXIT &mdash; Login</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Poppins', sans-serif;
    background: #0A1628;
    color: #fff;
    height: 100vh;
    overflow: hidden;
    position: relative;
  }
  body::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    width: 600px; height: 600px;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(239,83,80,0.08) 0%, transparent 70%);
    pointer-events: none;
  }
  .page {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    position: relative;
    z-index: 1;
  }
  .card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 56px 64px;
    text-align: center;
    max-width: 420px;
    width: 90%;
    animation: fadeUp 0.5s ease-out;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .icon-wrap {
    width: 72px; height: 72px;
    border-radius: 50%;
    background: rgba(239,83,80,0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 28px;
  }
  .icon-wrap svg {
    width: 32px; height: 32px;
    stroke: #ef5350;
    stroke-width: 2.5;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .icon-wrap svg .x-path {
    stroke-dasharray: 22;
    stroke-dashoffset: 22;
    animation: drawX 0.4s 0.35s ease-out forwards;
  }
  @keyframes drawX {
    to { stroke-dashoffset: 0; }
  }
  .brand {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.3);
    margin-bottom: 24px;
  }
  h2 {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #fff;
  }
  .sub {
    font-size: 14px;
    font-weight: 400;
    color: rgba(255,255,255,0.5);
    line-height: 1.6;
    margin-bottom: 32px;
  }
  .divider {
    width: 40px;
    height: 3px;
    background: #ef5350;
    border-radius: 3px;
    margin: 0 auto 32px;
  }
  .hint {
    font-size: 12px;
    font-weight: 300;
    color: rgba(255,255,255,0.3);
  }
</style>
</head>
<body>
  <div class="page">
    <div class="card">
      <div class="brand">F I X I T</div>
      <div class="icon-wrap">
        <svg viewBox="0 0 24 24">
          <path class="x-path" d="M7 7l10 10"/>
          <path class="x-path" d="M17 7L7 17"/>
        </svg>
      </div>
      <h2>Something went wrong</h2>
      <p class="sub">Authentication could not be completed.<br>Please close this tab and try again.</p>
      <div class="divider"></div>
      <p class="hint">If the issue persists, contact support.</p>
    </div>
  </div>
</body>
</html>"""


class OAuthRedirectHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        query = urlparse(self.path).query
        params = parse_qs(query)
        if "code" in params:
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(_SUCCESS_HTML)
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(_FAIL_HTML)

    def log_message(self, format, *args):
        pass


def google_oauth_login(page=None):
  
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
            return {"name": name, "email": email, "picture": user_info.get("picture")}
        else:
            raise Exception("Use your CSPC school email!")

    except Exception as e:
        raise Exception(f"Google login failed: {str(e)}")


if __name__ == "__main__":
    user = google_oauth_login()
    print("Logged in user:", user)
