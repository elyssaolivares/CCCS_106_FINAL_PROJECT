import os
from urllib.parse import urlparse, parse_qs, urlencode
import flet as ft
from app.views.homepage import homepage
from app.views.loginpage import loginpage
from app.services.session import get_session_manager
from app.services.google.oauth_server import exchange_code_for_token


def _read_oauth_params(page: ft.Page) -> tuple[str | None, str | None]:
    code = None
    state = None

    query = getattr(page, "query", None)
    if query:
        try:
            code = query.get("code")
            state = query.get("state")
        except Exception:
            pass

    route = getattr(page, "route", "") or ""
    if (not code or not state) and "?" in route:
        parsed = parse_qs(urlparse(route).query)
        code = code or parsed.get("code", [None])[0]
        state = state or parsed.get("state", [None])[0]

    # Some web deployments expose full callback in page.url.
    page_url = getattr(page, "url", "") or ""
    if (not code or not state) and "?" in page_url:
        parsed = parse_qs(urlparse(page_url).query)
        code = code or parsed.get("code", [None])[0]
        state = state or parsed.get("state", [None])[0]

    return code, state


def _resolve_redirect_uri(page: ft.Page) -> str:
    env_redirect_uri = os.environ.get("REDIRECT_URI")
    if env_redirect_uri:
        return env_redirect_uri

    return "http://localhost:8550/api/oauth/redirect"


def main(page: ft.Page):    
    page.title = "FIXIT"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0 
    page.bgcolor = ft.Colors.WHITE
    
    # set Poppins as default font
    page.fonts = {
        "Poppins": "fonts/Poppins-Regular.ttf",
        "Poppins-Bold": "fonts/Poppins-Bold.ttf",
        "Poppins-SemiBold": "fonts/Poppins-SemiBold.ttf",
        "Poppins-Medium": "fonts/Poppins-Medium.ttf",
        "Poppins-Light": "fonts/Poppins-Light.ttf",
    }
    
    # apply Poppins to theme
    page.theme = ft.Theme(
        font_family="Poppins",
    )

    # Start session monitoring
    session_manager = get_session_manager()
    session_manager.start_monitoring()

    # Restore active local session first.
    existing_user = page.session.get("user_data")
    if existing_user:
        user_type = str(existing_user.get("type", "")).lower()
        if user_type == "admin":
            from app.views.dashboard.admin.admin_dashboard import admin_dashboard

            admin_dashboard(page, existing_user)
        else:
            from app.views.dashboard.user_dashboard import user_dashboard

            user_dashboard(page, existing_user)
        return

    code, state = _read_oauth_params(page)
    if code:
        try:
            expected_state = page.session.get("oauth_state")
            if expected_state and state != expected_state:
                raise ValueError("OAuth state mismatch. Please sign in again.")

            role = (page.session.get("oauth_role") or "Student").strip().lower()
            user_type = "faculty" if role == "faculty" else "student"

            oauth_user = exchange_code_for_token(code, _resolve_redirect_uri(page))
            user_data = {
                "name": oauth_user.get("name") or "User",
                "email": oauth_user["email"],
                "type": user_type,
            }
            if oauth_user.get("picture"):
                user_data["picture"] = oauth_user["picture"]

            from app.services.database.database import db
            from app.services.audit.audit_logger import audit_logger
            from app.services.activity.activity_monitor import activity_monitor
            from app.views.dashboard.user_dashboard import user_dashboard

            db.create_or_update_user(
                user_data["email"],
                user_data["name"],
                user_data["type"],
                user_data.get("picture"),
            )
            session_manager.create_session(
                user_data["email"],
                user_data["name"],
                user_data["type"],
            )
            page.session.set("user_data", user_data)
            page.session.set("oauth_state", None)
            page.session.set("oauth_role", None)

            audit_logger.log_action(
                user_data["email"],
                user_data["name"],
                "login",
                status="success",
                details="CSPC OAuth login successful",
            )
            activity_monitor.log_login_attempt(
                user_data["email"],
                user_data["name"],
                success=True,
                details="CSPC OAuth login successful",
            )

            # Remove callback query/path from browser URL after successful auth.
            page.route = "/"
            page.update()
            user_dashboard(page, user_data)
            return
        except Exception as ex:
            print(f"OAuth callback handling failed: {ex}")
            # Fall through to homepage/login flow if callback processing fails.
            pass

    def go_to_login(e):
        page.clean()
        loginpage(page)

    homepage(page, go_to_login)

import secrets as _secrets
os.environ.setdefault("FLET_SECRET_KEY", _secrets.token_hex(16))

APP_KWARGS = {
    "target": main,
    "assets_dir": os.path.join(os.path.dirname(__file__), "assets"),
    "upload_dir": "storage/temp",
    "view": ft.AppView.WEB_BROWSER,
    "host": "0.0.0.0",
    "port": int(os.environ.get("PORT", 8550)),
}

# ASGI export for production servers
app = ft.app(export_asgi_app=True, **APP_KWARGS)

# Normalize Google callback path to root so Flet session handling can complete login.
if hasattr(app, "get"):
    @app.get("/api/oauth/redirect")
    async def oauth_redirect(code: str | None = None, state: str | None = None):
        params = {k: v for k, v in {"code": code, "state": state}.items() if v}
        target = "/"
        if params:
            target = f"/?{urlencode(params)}"

        from fastapi.responses import RedirectResponse

        return RedirectResponse(url=target, status_code=302)

if __name__ == "__main__":
    ft.app(**APP_KWARGS)