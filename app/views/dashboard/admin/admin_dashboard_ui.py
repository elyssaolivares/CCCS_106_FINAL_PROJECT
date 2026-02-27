
import flet as ft

# ── Palette (matches app theme) ──
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_WHITE = "#FFFFFF"
_CARD = "#FFFFFF"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"

_PENDING_TEXT = "#B45309"
_PENDING_BG = "#FEF3C7"
_ONGOING_TEXT = "#1565C0"
_ONGOING_BG = "#DBEAFE"
_RESOLVED_TEXT = "#15803D"
_RESOLVED_BG = "#DCFCE7"
_REJECTED_TEXT = "#DC2626"
_REJECTED_BG = "#FEE2E2"

_STATUS_MAP = {
    "pending":     (_PENDING_TEXT,  _PENDING_BG),
    "in progress": (_ONGOING_TEXT,  _ONGOING_BG),
    "resolved":    (_RESOLVED_TEXT, _RESOLVED_BG),
    "rejected":    (_REJECTED_TEXT, _REJECTED_BG),
}


class UIComponents:

    # ── Stat card (clean tile) ──
    @staticmethod
    def create_stat_card(label, count, icon, accent, bg_tint):
        tile = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, size=18, color=accent),
                                width=36, height=36,
                                border_radius=10,
                                bgcolor=bg_tint,
                                alignment=ft.alignment.center,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Text(str(count), size=26, font_family="Poppins-Bold", color=_NAVY),
                    ft.Text(label, size=11, font_family="Poppins-Medium", color=_NAVY_MUTED,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
            bgcolor=_CARD,
            border_radius=14,
            border=ft.border.all(1, _BORDER),
        )
        tile.col = {"xs": 6, "sm": 6, "md": 6, "lg": 3}
        return tile

    # ── Filter tab button ──
    @staticmethod
    def create_tab_button(label, count, active):
        text = ft.Text(
            f"{label} ({count})", size=11, weight=ft.FontWeight.W_600,
            color=_WHITE if active else _NAVY_MUTED,
            font_family="Poppins-Medium",
        )
        return ft.Container(
            content=text,
            bgcolor=_NAVY if active else ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            border_radius=8,
            alignment=ft.alignment.center,
            border=ft.border.all(1, _NAVY if active else _BORDER),
        )

    # ── Status update dialog ──
    @staticmethod
    def open_status_dialog(page, report, on_confirm):
        """Open a polished dialog for updating report status with remarks.

        Args:
            page: ft.Page
            report: report dict
            on_confirm: callback(report_id, new_status, remarks)
        """
        current_status = (report.get("status") or "Pending")
        status_options = ["Pending", "In Progress", "Resolved", "Rejected"]

        status_icons = {
            "Pending": ft.Icons.SCHEDULE_OUTLINED,
            "In Progress": ft.Icons.AUTORENEW_ROUNDED,
            "Resolved": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "Rejected": ft.Icons.CANCEL_OUTLINED,
        }
        status_colors = {
            "Pending": _PENDING_TEXT,
            "In Progress": _ONGOING_TEXT,
            "Resolved": _RESOLVED_TEXT,
            "Rejected": _REJECTED_TEXT,
        }
        status_bgs = {
            "Pending": _PENDING_BG,
            "In Progress": _ONGOING_BG,
            "Resolved": _RESOLVED_BG,
            "Rejected": _REJECTED_BG,
        }

        selected = {"status": current_status}
        option_containers = {}

        remarks_field = ft.TextField(
            label="Admin Remarks / Notes",
            value=report.get("admin_remarks") or "",
            multiline=True, min_lines=2, max_lines=5,
            border_color=_BORDER, focused_border_color=_ACCENT,
            border_radius=10, text_size=13, bgcolor=_WHITE, color=_NAVY,
            prefix_icon=ft.Icons.NOTES_ROUNDED,
            hint_text="Add a note about this status change…",
            hint_style=ft.TextStyle(size=12, color=_NAVY_MUTED),
        )

        error_text = ft.Text("", size=11, color=_REJECTED_TEXT, visible=False)

        def build_option(s):
            is_sel = s == selected["status"]
            is_current = s == current_status
            clr = status_colors[s]
            bg = status_bgs[s]

            badge = []
            if is_current:
                badge.append(
                    ft.Container(
                        content=ft.Text("Current", size=8, font_family="Poppins-SemiBold",
                                        color=_NAVY_MUTED),
                        bgcolor=_BORDER_LIGHT,
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        border_radius=4,
                    )
                )

            c = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(status_icons[s], size=16, color=clr),
                            width=30, height=30, border_radius=8,
                            bgcolor=bg, alignment=ft.alignment.center,
                        ),
                        ft.Text(s, size=13, font_family="Poppins-Medium",
                                color=_NAVY if is_sel else _NAVY_MUTED, expand=True),
                        *badge,
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.RADIO_BUTTON_CHECKED if is_sel
                                else ft.Icons.RADIO_BUTTON_UNCHECKED,
                                size=18, color=clr if is_sel else _BORDER,
                            ),
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                border_radius=10,
                border=ft.border.all(1.5, clr if is_sel else _BORDER),
                bgcolor=bg if is_sel else _WHITE,
                on_click=lambda e, st=s: select_status(st),
                ink=True,
                animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            )
            option_containers[s] = c
            return c

        def select_status(st):
            selected["status"] = st
            # Rebuild all options appearance
            for s_key, cont in option_containers.items():
                is_sel = s_key == st
                clr = status_colors[s_key]
                bg = status_bgs[s_key]
                cont.border = ft.border.all(1.5, clr if is_sel else _BORDER)
                cont.bgcolor = bg if is_sel else _WHITE
                # Update the radio icon and text
                row = cont.content
                row.controls[-1].content = ft.Icon(
                    ft.Icons.RADIO_BUTTON_CHECKED if is_sel
                    else ft.Icons.RADIO_BUTTON_UNCHECKED,
                    size=18, color=clr if is_sel else _BORDER,
                )
                row.controls[1].color = _NAVY if is_sel else _NAVY_MUTED
            error_text.visible = False
            page.update()

        def on_submit(e):
            new_status = selected["status"]
            remarks = remarks_field.value.strip() if remarks_field.value else ""
            if new_status == current_status and not remarks:
                error_text.value = "Select a different status or add a remark."
                error_text.visible = True
                page.update()
                return
            dialog.open = False
            page.update()
            on_confirm(report.get("id"), new_status, remarks)

        def on_cancel(e):
            dialog.open = False
            page.update()

        # Report summary header
        desc = (report.get("issue_description") or "").strip()
        if len(desc) > 80:
            desc = desc[:78] + "…"

        report_summary = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(f"#{report.get('id')}", size=10,
                                                font_family="Poppins-SemiBold", color=_ACCENT),
                                bgcolor=ft.Colors.with_opacity(0.08, _ACCENT),
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                border_radius=6,
                            ),
                            ft.Container(
                                content=ft.Text(report.get("category", ""), size=10,
                                                font_family="Poppins-Medium", color=_NAVY_MUTED),
                                bgcolor=_BORDER_LIGHT,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                border_radius=6,
                            ),
                        ],
                        spacing=6,
                    ),
                    ft.Text(desc, size=12, font_family="Poppins-Medium", color=_NAVY,
                            max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.PERSON_OUTLINE, size=12, color=_NAVY_MUTED),
                            ft.Text(report.get("user_name") or report.get("user_email") or "-",
                                    size=11, font_family="Poppins-Light", color=_NAVY_MUTED),
                        ],
                        spacing=4,
                    ),
                ],
                spacing=6,
            ),
            padding=ft.padding.all(12),
            bgcolor=_BORDER_LIGHT,
            border_radius=10,
        )

        status_options_col = ft.Column(
            [build_option(s) for s in status_options],
            spacing=6,
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=20, color=_WHITE),
                        width=34, height=34, border_radius=10,
                        bgcolor=_ACCENT, alignment=ft.alignment.center,
                    ),
                    ft.Text("Update Report Status", size=16,
                            font_family="Poppins-Bold", color=_NAVY),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        report_summary,
                        ft.Container(height=12),
                        ft.Text("Set Status", size=12, font_family="Poppins-SemiBold",
                                color=_NAVY),
                        ft.Container(height=6),
                        status_options_col,
                        ft.Container(height=14),
                        ft.Text("Remarks", size=12, font_family="Poppins-SemiBold",
                                color=_NAVY),
                        ft.Container(height=4),
                        remarks_field,
                        error_text,
                    ],
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=380,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancel", size=13, font_family="Poppins-Medium",
                                    color=_NAVY_MUTED),
                    on_click=on_cancel,
                ),
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CHECK_ROUNDED, size=16, color=_WHITE),
                            ft.Text("Confirm", size=13, font_family="Poppins-SemiBold",
                                    color=_WHITE),
                        ],
                        spacing=6, tight=True,
                    ),
                    bgcolor=_ACCENT,
                    on_click=on_submit,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=18, vertical=10),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=16),
            bgcolor=_WHITE,
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ── Report card (upgraded with remarks + update button) ──
    @staticmethod
    def create_report_card(report, on_status_change, page=None):
        desc = (report.get("issue_description") or "").strip()
        if len(desc) > 120:
            desc = desc[:120] + "..."

        status_raw = (report.get("status") or "pending").strip().lower()
        status_text, status_bg = _STATUS_MAP.get(status_raw, (_NAVY_MUTED, _BORDER_LIGHT))
        category = report.get("category", "Uncategorized")
        remarks = report.get("admin_remarks")
        updated_at = report.get("status_updated_at")
        updated_by = report.get("status_updated_by")

        # ── Remarks display ──
        remarks_section = ft.Container()
        if remarks:
            remarks_section = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.NOTES_ROUNDED, size=13, color=_ACCENT),
                        ft.Text(remarks, size=11, font_family="Poppins-Light",
                                color=_NAVY_MUTED, expand=True, max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                italic=True),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                padding=ft.padding.symmetric(horizontal=10, vertical=8),
                bgcolor=ft.Colors.with_opacity(0.04, _ACCENT),
                border_radius=8,
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, _ACCENT)),
            )

        # ── Status update info ──
        update_info = ft.Container()
        if updated_at:
            # Format timestamp nicely
            ts_display = str(updated_at)[:16].replace("T", " ") if updated_at else ""
            by_display = f" by {updated_by}" if updated_by else ""
            update_info = ft.Row(
                [
                    ft.Icon(ft.Icons.UPDATE_ROUNDED, size=11, color=_NAVY_MUTED),
                    ft.Text(f"Updated {ts_display}{by_display}", size=9,
                            font_family="Poppins-Light", color=_NAVY_MUTED),
                ],
                spacing=4,
            )

        # ── Update status button ──
        def on_update_click(e):
            if page:
                def handle_confirm(rid, new_status, remark):
                    on_status_change(rid, new_status, remark)
                UIComponents.open_status_dialog(page, report, handle_confirm)
            else:
                # Fallback: direct status change for backward compat
                on_status_change(report.get("id"), "In Progress", "")

        update_button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=14, color=_WHITE),
                    ft.Text("Update Status", size=11, font_family="Poppins-SemiBold",
                            color=_WHITE),
                ],
                spacing=6, tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=_ACCENT,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            border_radius=8,
            on_click=on_update_click,
            ink=True,
        )

        card_children = [
            # Header row: ID + description
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(f"#{report.get('id')}", size=10,
                                        font_family="Poppins-SemiBold", color=_ACCENT),
                        bgcolor=ft.Colors.with_opacity(0.08, _ACCENT),
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                    ),
                    ft.Text(desc, size=13, font_family="Poppins-Medium",
                            color=_NAVY, expand=True, max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Container(height=1, bgcolor=_BORDER),
            # Details
            ft.Row(
                [
                    ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color=_NAVY_MUTED),
                    ft.Text(report.get("location") or "-", size=12,
                            font_family="Poppins-Light", color=_NAVY_MUTED, expand=True),
                ],
                spacing=6,
            ),
            ft.Row(
                [
                    ft.Icon(ft.Icons.PERSON_OUTLINE, size=14, color=_NAVY_MUTED),
                    ft.Text(report.get("user_name") or report.get("user_email") or "-",
                            size=12, font_family="Poppins-Light", color=_NAVY_MUTED, expand=True),
                ],
                spacing=6,
            ),
            # Status + category badges
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(report.get("status", "Pending"), size=10,
                                        font_family="Poppins-SemiBold", color=status_text),
                        bgcolor=status_bg,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                    ),
                    ft.Container(
                        content=ft.Text(category, size=10,
                                        font_family="Poppins-Medium", color=_NAVY_MUTED),
                        bgcolor=_BORDER_LIGHT,
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                    ),
                ],
                spacing=8,
            ),
        ]

        # Add remarks if present
        if remarks:
            card_children.append(remarks_section)

        # Add update info if present
        if updated_at:
            card_children.append(update_info)

        # Action row: update button
        card_children.append(
            ft.Row([update_button], alignment=ft.MainAxisAlignment.END),
        )

        return ft.Container(
            content=ft.Column(
                card_children,
                spacing=10,
                tight=True,
            ),
            padding=ft.padding.all(16),
            bgcolor=_CARD,
            border_radius=12,
            border=ft.border.all(1, _BORDER),
            margin=ft.margin.only(bottom=8),
        )

    # ── Empty state ──
    @staticmethod
    def create_empty_state(status_filter=""):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.INBOX_OUTLINED, size=40, color=_NAVY_MUTED),
                        width=72, height=72, border_radius=36,
                        bgcolor=_BORDER_LIGHT, alignment=ft.alignment.center,
                    ),
                    ft.Container(height=12),
                    ft.Text("No reports found", size=16, font_family="Poppins-Bold", color=_NAVY),
                    ft.Container(height=4),
                    ft.Text(
                        f"There are no {status_filter.lower()} reports at the moment." if status_filter else "No reports to display.",
                        size=12, font_family="Poppins-Light", color=_NAVY_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.padding.symmetric(vertical=40, horizontal=20),
            alignment=ft.alignment.center,
        )

    # ── Category list item ──
    @staticmethod
    def create_category_list_item(category_name, count, on_click):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.FOLDER_OUTLINED, size=18, color=_ACCENT),
                        width=36, height=36, border_radius=10,
                        bgcolor=ft.Colors.with_opacity(0.08, _ACCENT),
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(category_name, size=14, font_family="Poppins-Medium",
                            color=_NAVY, expand=True),
                    ft.Container(
                        content=ft.Text(str(count), size=12, font_family="Poppins-SemiBold", color=_WHITE),
                        bgcolor=_ACCENT,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        border_radius=14,
                    ),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, size=18, color=_NAVY_MUTED),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=14),
            bgcolor=_CARD,
            border_radius=12,
            border=ft.border.all(1, _BORDER),
            on_click=on_click,
            ink=True,
        )

    # ── Empty category message ──
    @staticmethod
    def create_empty_category_message(category_name=None):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=36,
                                        color=ft.Colors.with_opacity(0.25, _NAVY)),
                        width=64, height=64, border_radius=32,
                        bgcolor=_BORDER_LIGHT, alignment=ft.alignment.center,
                    ),
                    ft.Container(height=10),
                    ft.Text("No reports found", size=14, font_family="Poppins-Bold", color=_NAVY),
                    ft.Container(height=2),
                    ft.Text(
                        f"No reports in {category_name}." if category_name else "No categories found.",
                        size=12, font_family="Poppins-Light", color=_NAVY_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=ft.padding.symmetric(vertical=40),
            alignment=ft.alignment.center,
        )

    # ── Category card (unused but kept for compat) ──
    @staticmethod
    def create_category_card(category_name, count, on_click):
        return UIComponents.create_category_list_item(category_name, count, on_click)

    # ── Subpage header (kept for subpages) ──
    @staticmethod
    def create_page_header(is_dark, title, on_back, on_menu):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(title, size=18, font_family="Poppins-Bold", color=_NAVY,
                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            ft.Icons.MENU_ROUNDED, icon_color=_NAVY, icon_size=20,
                            on_click=on_menu,
                        ),
                        width=36, height=36, border_radius=10,
                        bgcolor=_BORDER_LIGHT, alignment=ft.alignment.center,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=14),
            bgcolor=_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, _BORDER)),
        )

    # ── Header (kept for compat) ──
    @staticmethod
    def create_header(is_dark, on_menu_click):
        return UIComponents.create_page_header(is_dark, "Admin Dashboard", lambda: None, on_menu_click)

