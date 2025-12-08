import flet as ft
import os
import base64
from .session_manager import SessionManager
from .navigation_drawer import NavigationDrawerComponent
from app.services.database.database import db

def account_page(page: ft.Page, user_data=None):
    page.controls.clear()
    
    if not user_data:
        user_data = page.session.get("user_data")
    
    # Try to load profile from database
    email = user_data.get("email") if user_data else None
    if email:
        db_user = db.get_user_by_email(email)
        print(f"[DEBUG] Loaded user from DB: {db_user}")
        if db_user:
            # Update user_data with database values
            user_data["name"] = db_user.get("name", user_data.get("name", "User"))
            user_data["picture"] = db_user.get("picture", user_data.get("picture"))
    else:
        print(f"[DEBUG] No email found in user_data")
    
    full_name = user_data.get("name", "User") if user_data else "User"
    raw_role = None
    if user_data:
        raw_role = user_data.get("role") or user_data.get("type")
    role = str(raw_role).title() if raw_role else "Student"
    email = user_data.get("email", "user@example.com") if user_data else "user@example.com"
    picture = user_data.get("picture") if user_data else None
    is_admin = role.lower() == "admin"
    
    is_dark = page.session.get("is_dark_theme") or False
    
    # State for edit mode and profile picture
    edit_mode = {"active": False}
    current_picture = {"path": picture}
    
    def toggle_dark_theme(e):
        SessionManager.set_theme_preference(page, not is_dark)
        # Reload fresh user data from database before refreshing
        fresh_user_data = db.get_user_by_email(email)
        if fresh_user_data:
            user_data.update(fresh_user_data)
        account_page(page, user_data)
    
    nav_drawer = NavigationDrawerComponent(page, user_data, toggle_dark_theme)
    drawer = nav_drawer.create_drawer(is_dark)
    
    header = ft.Container(
        content=ft.Row(
            [
                ft.Text(
                    "Account",
                    size=20,
                    font_family="Poppins-Bold",
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                ),
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    icon_color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                    on_click=nav_drawer.open_drawer,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )
    
    # Text fields for editing
    name_field = ft.TextField(
        value=full_name,
        label="Full Name",
        border_color="#062C80",
        focused_border_color="#093AA5",
        text_size=14,
    )
    
    email_field = ft.TextField(
        value=email,
        label="Email",
        border_color="#062C80",
        focused_border_color="#093AA5",
        text_size=14,
        read_only=True,
        hint_text="Email cannot be changed",
    )
    
    # Password change fields (only for admin)
    current_password_field = ft.TextField(
        label="Current Password",
        password=True,
        can_reveal_password=True,
        border_color="#062C80",
        focused_border_color="#093AA5",
        text_size=14,
    )
    
    new_password_field = ft.TextField(
        label="New Password",
        password=True,
        can_reveal_password=True,
        border_color="#062C80",
        focused_border_color="#093AA5",
        text_size=14,
    )
    
    confirm_password_field = ft.TextField(
        label="Confirm New Password",
        password=True,
        can_reveal_password=True,
        border_color="#062C80",
        focused_border_color="#093AA5",
        text_size=14,
    )
    
    status_text = ft.Text("", size=12, color=ft.Colors.GREEN)
    error_text = ft.Text("", size=12, color=ft.Colors.RED)
    
    # Profile image container that will be updated
    profile_image_content = ft.Container()
    
    def update_profile_image():
        if current_picture["path"]:
            # Check if it's a base64 encoded image
            if current_picture["path"].startswith("data:image"):
                # It's a base64 encoded image (web compatible)
                profile_image_content.content = ft.Image(
                    src_base64=current_picture["path"].split(",")[1] if "," in current_picture["path"] else current_picture["path"],
                    width=120,
                    height=120,
                    fit=ft.ImageFit.COVER,
                    border_radius=60,
                )
            else:
                # It's a file path
                # Check if we're in web mode - if so, we can't load desktop file paths
                try:
                    # Try to load the file and convert to base64 for web compatibility
                    if os.path.exists(current_picture["path"]):
                        import base64
                        with open(current_picture["path"], 'rb') as f:
                            image_data = f.read()
                            base64_image = base64.b64encode(image_data).decode('utf-8')
                            ext = current_picture["path"].lower().split('.')[-1]
                            mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                            # Update with base64 for future use
                            current_picture["path"] = f"data:{mime_type};base64,{base64_image}"
                            profile_image_content.content = ft.Image(
                                src_base64=base64_image,
                                width=120,
                                height=120,
                                fit=ft.ImageFit.COVER,
                                border_radius=60,
                            )
                    else:
                        # File doesn't exist (e.g., web mode) - show default icon
                        profile_image_content.content = ft.Icon(
                            ft.Icons.ACCOUNT_CIRCLE,
                            size=120,
                            color="#062C80",
                        )
                except Exception as ex:
                    print(f"[DEBUG] Could not load image: {ex}")
                    # Fallback to file path for desktop, or icon if not available
                    if page.web and not os.path.exists(current_picture["path"]):
                        profile_image_content.content = ft.Icon(
                            ft.Icons.ACCOUNT_CIRCLE,
                            size=120,
                            color="#062C80",
                        )
                    else:
                        profile_image_content.content = ft.Image(
                            src=current_picture["path"],
                            width=120,
                            height=120,
                            fit=ft.ImageFit.COVER,
                            border_radius=60,
                        )
        else:
            profile_image_content.content = ft.Icon(
                ft.Icons.ACCOUNT_CIRCLE,
                size=120,
                color="#062C80",
            )
        profile_image_content.update()
    
    # Profile picture upload
    def handle_file_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            # Validate file type
            valid_types = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(file.name.lower().endswith(ext) for ext in valid_types):
                error_text.value = "Invalid file type. Please upload JPG, PNG, or GIF."
                status_text.value = ""
                page.update()
                return
            
            # Validate file size (5MB max)
            if file.size > 5 * 1024 * 1024:
                error_text.value = "File too large. Maximum size is 5MB."
                status_text.value = ""
                page.update()
                return
            
            # For web compatibility, convert image to base64
            try:
                import base64
                # In web mode, file.path is None, use the bytes from the picked file
                # In desktop mode, we need to read the file
                if hasattr(file, 'path') and file.path:
                    with open(file.path, 'rb') as f:
                        image_data = f.read()
                else:
                    # Web mode: file bytes are available differently
                    # For now, we'll store the filename and let desktop handle it
                    image_data = None
                
                if image_data:
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                # Determine MIME type
                    ext = file.name.lower().split('.')[-1]
                    mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                    current_picture["path"] = f"data:{mime_type};base64,{base64_image}"
                else:
                    error_text.value = "Note: Profile picture upload works best in desktop mode. Web mode has file access limitations."
                    status_text.value = ""
                    page.update()
                    return
            except Exception as ex:
                print(f"Error converting image to base64: {ex}")
                if hasattr(file, 'path') and file.path:
                    current_picture["path"] = file.path
                else:
                    error_text.value = "Unable to process image. Please try in desktop mode."
                    status_text.value = ""
                    page.update()
                    return
            
            update_profile_image()
            
            error_text.value = ""
            status_text.value = f"Profile picture selected. Click 'Save Changes' to apply."
            page.update()
    
    file_picker = ft.FilePicker(on_result=handle_file_picker_result)
    page.overlay.append(file_picker)
    
    # Initial profile image
    profile_image = ft.Container(
        content=profile_image_content,
        width=120,
        height=120,
        border_radius=60,
        alignment=ft.alignment.center,
    )
    
    upload_button = ft.IconButton(
        icon=ft.Icons.CAMERA_ALT,
        icon_color=ft.Colors.WHITE,
        bgcolor="#062C80",
        on_click=lambda e: file_picker.pick_files(
            allowed_extensions=["jpg", "jpeg", "png", "gif"],
            dialog_title="Select Profile Picture"
        ),
        tooltip="Upload Profile Picture",
    )
    
    profile_picture_stack = ft.Stack(
        [
            profile_image,
            ft.Container(
                content=upload_button,
                right=0,
                bottom=0,
            ),
        ],
        width=120,
        height=120,
    )
    
    # Display mode content
    display_name = ft.Text(
        full_name.upper(),
        size=26,
        font_family="Poppins-SemiBold",
        color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
        text_align=ft.TextAlign.CENTER,
    )
    
    display_email = ft.Row(
        [
            ft.Icon(ft.Icons.EMAIL, color=ft.Colors.GREY, size=20),
            ft.Container(width=10),
            ft.Text(
                email,
                size=14,
                color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    # Edit profile section
    edit_profile_section = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Edit Profile",
                    size=18,
                    font_family="Poppins-SemiBold",
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                ),
                ft.Container(height=15),
                name_field,
                ft.Container(height=10),
                email_field,
                ft.Container(height=20),
            ],
            spacing=0,
        ),
        visible=False,
    )
    
    # Change password section (only for admin)
    change_password_section = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Change Password",
                    size=18,
                    font_family="Poppins-SemiBold",
                    color=ft.Colors.WHITE if is_dark else ft.Colors.BLACK,
                ),
                ft.Container(height=15),
                current_password_field,
                ft.Container(height=10),
                new_password_field,
                ft.Container(height=10),
                confirm_password_field,
                ft.Container(height=15),
            ],
            spacing=0,
        ),
        visible=False,
    )
    
    def update_env_password(new_password):
        """Update ADMIN_PASSWORD in .env file"""
        try:
            env_path = ".env"
            
            # Read existing .env content
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Update or add ADMIN_PASSWORD
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('ADMIN_PASSWORD='):
                    lines[i] = f'ADMIN_PASSWORD={new_password}\n'
                    updated = True
                    break
            
            if not updated:
                lines.append(f'ADMIN_PASSWORD={new_password}\n')
            
            # Write back to .env
            with open(env_path, 'w') as f:
                f.writelines(lines)
            
            return True
        except Exception as e:
            print(f"Error updating .env: {e}")
            return False
    
    def toggle_edit_mode(e):
        edit_mode["active"] = not edit_mode["active"]
        
        # Toggle visibility
        display_name.visible = not edit_mode["active"]
        display_email.visible = not edit_mode["active"]
        edit_profile_section.visible = edit_mode["active"]
        
        # Show password section only for admin
        if is_admin:
            change_password_section.visible = edit_mode["active"]
        
        # Update button text
        edit_button.text = "Cancel" if edit_mode["active"] else "Edit Profile"
        edit_button.icon = ft.Icons.CLOSE if edit_mode["active"] else ft.Icons.EDIT
        save_button.visible = edit_mode["active"]
        
        # Clear messages
        status_text.value = ""
        error_text.value = ""
        
        # Reset picture preview if canceling
        if not edit_mode["active"]:
            current_picture["path"] = user_data.get("picture")
            update_profile_image()
        
        page.update()
    
    def save_profile(e):
        error_text.value = ""
        status_text.value = ""
        
        # Validate name
        if not name_field.value or len(name_field.value.strip()) < 2:
            error_text.value = "Name must be at least 2 characters"
            page.update()
            return
        
        # Validate password if admin is attempting to change it
        if is_admin and (current_password_field.value or new_password_field.value or confirm_password_field.value):
            # Get current admin password from environment
            current_admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            if not current_password_field.value:
                error_text.value = "Current password is required"
                page.update()
                return
            
            # Verify current password
            if current_password_field.value != current_admin_password:
                error_text.value = "Current password is incorrect"
                page.update()
                return
            
            if len(new_password_field.value) < 6:
                error_text.value = "New password must be at least 6 characters"
                page.update()
                return
            
            if new_password_field.value != confirm_password_field.value:
                error_text.value = "New passwords do not match"
                page.update()
                return
            
            # Update .env file with new password
            if update_env_password(new_password_field.value):
                status_text.value = "Password changed successfully!"
            else:
                error_text.value = "Failed to update password in system"
                page.update()
                return
        
        # Prepare updated profile data
        new_name = name_field.value.strip()
        new_picture = current_picture["path"] if current_picture["path"] != user_data.get("picture") else None
        
        print(f"[DEBUG] Saving profile: email={email}, name={new_name}, picture={new_picture}")
        
        # Save to database
        try:
            result = db.create_or_update_user(email, new_name, role.lower(), new_picture)
            print(f"[DEBUG] Database save result: {result}")
        except Exception as db_error:
            print(f"[DEBUG] Database error: {str(db_error)}")
            error_text.value = f"Failed to save to database: {str(db_error)}"
            page.update()
            return
        
        # Update session data with new name and picture
        user_data["name"] = new_name
        if new_picture:
            user_data["picture"] = new_picture
        
        page.session.set("user_data", user_data)
        
        if not status_text.value:
            status_text.value = "Profile updated successfully!"
        
        # Clear password fields
        current_password_field.value = ""
        new_password_field.value = ""
        confirm_password_field.value = ""
        
        page.update()
        
        # Wait a moment then exit edit mode and refresh
        import time
        time.sleep(1)
        
        # Refresh the page with updated data
        account_page(page, user_data)
    
    edit_button = ft.ElevatedButton(
        "Edit Profile",
        icon=ft.Icons.EDIT,
        on_click=toggle_edit_mode,
        bgcolor="#062C80",
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )
    
    save_button = ft.ElevatedButton(
        "Save Changes",
        icon=ft.Icons.SAVE,
        on_click=save_profile,
        bgcolor="#4CAF50",
        color=ft.Colors.WHITE,
        visible=False,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )
    
    profile_card = ft.Container(
        content=ft.Column(
            [
                ft.Container(height=20),
                profile_picture_stack,
                ft.Container(height=25),
                display_name,
                ft.Container(height=8),
                ft.Container(
                    content=ft.Text(
                        role,
                        size=14,
                        font_family="Poppins-Medium",
                        color=ft.Colors.WHITE,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    bgcolor="#062C80" if is_dark else "#093AA5",
                    border_radius=20,
                ),
                ft.Container(height=20),
                ft.Divider(height=2, color=ft.Colors.GREY_600 if is_dark else ft.Colors.GREY_300),
                ft.Container(height=20),
                display_email,
                ft.Container(height=20),
                edit_profile_section,
                change_password_section if is_admin else ft.Container(),
                status_text,
                error_text,
                ft.Container(height=15),
                ft.Row(
                    [edit_button, save_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Container(height=30),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.all(30),
        width=500,
        bgcolor=ft.Colors.GREY_800 if is_dark else ft.Colors.WHITE,
        border_radius=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )
    
    def update_layout(e=None):
        is_mobile = page.width < 768
        main_container.width = None if is_mobile else 1500
        page.update()
    
    main_container = ft.Container(
        content=ft.Column(
            [profile_card],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        ),
        padding=ft.padding.symmetric(horizontal=25, vertical=20),
        width=None,
    )
    
    responsive_wrapper = ft.Column(
        [
            header,
            ft.Container(height=20),
            ft.Container(
                content=main_container,
                alignment=ft.alignment.top_center,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
    
    page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.GREY_900 if is_dark else ft.Colors.GREY_100
    page.overlay_color = ft.Colors.TRANSPARENT
    page.end_drawer = drawer
    page.on_resized = update_layout
    page.add(responsive_wrapper)

    update_profile_image()
    
    update_layout()
    page.update()