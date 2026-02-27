"""Analytics UI components for the admin dashboard – pure Flet, no external charts."""

import flet as ft
from datetime import datetime, timedelta

# ── Palette ──
_BG = "#F5F7FA"
_NAVY = "#0F2B5B"
_NAVY_MUTED = "#64748B"
_ACCENT = "#1565C0"
_WHITE = "#FFFFFF"
_CARD = "#FFFFFF"
_BORDER = "#E0E6ED"
_BORDER_LIGHT = "#F1F5F9"
_GREEN = "#15803D"
_GREEN_BG = "#DCFCE7"
_AMBER = "#B45309"
_AMBER_BG = "#FEF3C7"
_RED = "#DC2626"
_RED_BG = "#FEE2E2"
_BLUE = "#1565C0"
_BLUE_BG = "#DBEAFE"

_BAR_COLORS = ["#1565C0", "#7C3AED", "#0891B2", "#059669", "#D97706",
               "#DC2626", "#DB2777", "#4F46E5", "#0D9488", "#EA580C"]


class AnalyticsUI:
    """Pure-Flet analytics widgets for the admin dashboard."""

    # ────────────────────────────────────────────
    #  Section header
    # ────────────────────────────────────────────
    @staticmethod
    def section_header(title, icon=ft.Icons.ANALYTICS_OUTLINED):
        return ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, size=16, color=_ACCENT),
                    width=30, height=30, border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.08, _ACCENT),
                    alignment=ft.alignment.center,
                ),
                ft.Text(title, size=15, font_family="Poppins-SemiBold", color=_NAVY),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ────────────────────────────────────────────
    #  Summary stat mini-card  (used in a row)
    # ────────────────────────────────────────────
    @staticmethod
    def mini_stat(label, value, icon, color, bg):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Icon(icon, size=16, color=color),
                        width=32, height=32, border_radius=8,
                        bgcolor=bg, alignment=ft.alignment.center,
                    ),
                    ft.Column(
                        [
                            ft.Text(str(value), size=16, font_family="Poppins-Bold", color=_NAVY),
                            ft.Text(label, size=10, font_family="Poppins-Medium",
                                    color=_NAVY_MUTED, max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                        ],
                        spacing=0, expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(12),
            bgcolor=_CARD,
            border_radius=12,
            border=ft.border.all(1, _BORDER),
            expand=True,
        )

    # ────────────────────────────────────────────
    #  Horizontal bar chart (category / location)
    # ────────────────────────────────────────────
    @staticmethod
    def horizontal_bar_chart(data, title="", max_bars=6, value_key="count", label_key="category"):
        """Render a simple horizontal bar chart.

        Args:
            data: list of dicts like [{'category': 'X', 'count': 5}, …]
            title: card title
            max_bars: max bars to show
            value_key / label_key: keys in each dict
        """
        if not data:
            return ft.Container(
                content=ft.Text("No data available", size=12,
                                color=_NAVY_MUTED, font_family="Poppins-Light"),
                padding=ft.padding.all(20), alignment=ft.alignment.center,
            )

        items = data[:max_bars]
        max_val = max(d[value_key] for d in items) if items else 1

        bars = []
        for i, d in enumerate(items):
            pct = d[value_key] / max_val if max_val > 0 else 0
            color = _BAR_COLORS[i % len(_BAR_COLORS)]
            label = str(d[label_key])
            if len(label) > 18:
                label = label[:16] + "…"

            bars.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(label, size=11, font_family="Poppins-Medium",
                                            color=_NAVY, expand=True, max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(str(d[value_key]), size=11,
                                            font_family="Poppins-SemiBold", color=_NAVY),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Container(
                                content=ft.Container(
                                    bgcolor=color,
                                    border_radius=4,
                                    height=8,
                                    width=max(pct * 100, 2),  # percentage width
                                    animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
                                ),
                                bgcolor=_BORDER_LIGHT,
                                border_radius=4,
                                height=8,
                                expand=True,
                                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=ft.padding.symmetric(vertical=3),
                )
            )

        header_controls = []
        if title:
            header_controls.append(
                ft.Text(title, size=13, font_family="Poppins-SemiBold", color=_NAVY),
            )
            header_controls.append(ft.Container(height=10))

        return ft.Container(
            content=ft.Column(
                [*header_controls, *bars],
                spacing=2,
            ),
            padding=ft.padding.all(16),
            bgcolor=_CARD,
            border_radius=14,
            border=ft.border.all(1, _BORDER),
        )

    # ────────────────────────────────────────────
    #  Vertical bar chart (daily trend)
    # ────────────────────────────────────────────
    @staticmethod
    def daily_trend_chart(per_day_data, days=7):
        """Vertical bar chart showing daily report counts.

        Args:
            per_day_data: list of {'day': 'YYYY-MM-DD', 'count': N}
            days: how many days to show (fills missing days with 0)
        """
        day_map = {d['day']: d['count'] for d in per_day_data if d.get('day')}
        today = datetime.now().date()
        all_days = []
        for i in range(days - 1, -1, -1):
            dt = today - timedelta(days=i)
            key = dt.strftime("%Y-%m-%d")
            all_days.append({'day': key, 'label': dt.strftime("%a"), 'count': day_map.get(key, 0)})

        max_val = max((d['count'] for d in all_days), default=1) or 1
        bar_max_h = 80  # px for tallest bar

        bar_cols = []
        for d in all_days:
            h = max(int(d['count'] / max_val * bar_max_h), 4)
            bar_cols.append(
                ft.Column(
                    [
                        ft.Text(str(d['count']), size=9, font_family="Poppins-SemiBold",
                                color=_ACCENT, text_align=ft.TextAlign.CENTER),
                        ft.Container(
                            width=24, height=h,
                            bgcolor=_ACCENT,
                            border_radius=ft.border_radius.only(top_left=6, top_right=6),
                            animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
                        ),
                        ft.Text(d['label'], size=9, font_family="Poppins-Medium",
                                color=_NAVY_MUTED, text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=3,
                    expand=True,
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Reports This Week", size=13,
                            font_family="Poppins-SemiBold", color=_NAVY),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row(
                            bar_cols,
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            spacing=4,
                        ),
                        height=bar_max_h + 40,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
            bgcolor=_CARD,
            border_radius=14,
            border=ft.border.all(1, _BORDER),
        )

    # ────────────────────────────────────────────
    #  Resolution rate ring
    # ────────────────────────────────────────────
    @staticmethod
    def resolution_ring(rate_data):
        """Show resolution rate as a styled percentage ring.

        Args:
            rate_data: {'total': int, 'resolved': int, 'rate': float}
        """
        rate = rate_data.get('rate', 0)
        total = rate_data.get('total', 0)
        resolved = rate_data.get('resolved', 0)

        if rate >= 70:
            ring_color = _GREEN
            ring_bg = _GREEN_BG
        elif rate >= 40:
            ring_color = _AMBER
            ring_bg = _AMBER_BG
        else:
            ring_color = _RED
            ring_bg = _RED_BG

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Resolution Rate", size=13,
                            font_family="Poppins-SemiBold", color=_NAVY),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            # Ring visual
                            ft.Stack(
                                [
                                    ft.Container(
                                        width=72, height=72, border_radius=36,
                                        border=ft.border.all(6, _BORDER_LIGHT),
                                    ),
                                    ft.Container(
                                        width=72, height=72, border_radius=36,
                                        border=ft.border.all(6, ring_color),
                                        alignment=ft.alignment.center,
                                        content=ft.Text(f"{rate}%", size=14,
                                                        font_family="Poppins-Bold",
                                                        color=ring_color),
                                    ),
                                ],
                                width=72, height=72,
                            ),
                            ft.Container(width=14),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Container(width=8, height=8, border_radius=4,
                                                         bgcolor=_GREEN),
                                            ft.Text(f"Resolved: {resolved}", size=11,
                                                    font_family="Poppins-Medium", color=_NAVY),
                                        ],
                                        spacing=6,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Container(width=8, height=8, border_radius=4,
                                                         bgcolor=_NAVY_MUTED),
                                            ft.Text(f"Total: {total}", size=11,
                                                    font_family="Poppins-Medium",
                                                    color=_NAVY_MUTED),
                                        ],
                                        spacing=6,
                                    ),
                                ],
                                spacing=6,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
            bgcolor=_CARD,
            border_radius=14,
            border=ft.border.all(1, _BORDER),
        )

    # ────────────────────────────────────────────
    #  Top reporters list
    # ────────────────────────────────────────────
    @staticmethod
    def top_reporters_card(reporters):
        """Show a ranked list of top reporters.

        Args:
            reporters: list of {'name': str, 'email': str, 'count': int}
        """
        if not reporters:
            return ft.Container(
                content=ft.Text("No reporters yet", size=12,
                                color=_NAVY_MUTED, font_family="Poppins-Light"),
                padding=ft.padding.all(20), alignment=ft.alignment.center,
            )

        rows = []
        medals = ["🥇", "🥈", "🥉"]
        for i, r in enumerate(reporters[:5]):
            rank_text = medals[i] if i < 3 else f"#{i + 1}"
            name = r['name'] or r['email'].split('@')[0]
            if len(name) > 16:
                name = name[:14] + "…"

            rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(rank_text, size=13, width=28,
                                    text_align=ft.TextAlign.CENTER),
                            ft.Container(
                                content=ft.Text(
                                    (r['name'] or "?")[0].upper(),
                                    size=10, font_family="Poppins-Bold", color=_WHITE,
                                ),
                                width=28, height=28, border_radius=14,
                                bgcolor=_BAR_COLORS[i % len(_BAR_COLORS)],
                                alignment=ft.alignment.center,
                            ),
                            ft.Column(
                                [
                                    ft.Text(name, size=11,
                                            font_family="Poppins-Medium", color=_NAVY,
                                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(r['email'], size=9,
                                            font_family="Poppins-Light", color=_NAVY_MUTED,
                                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ],
                                spacing=0, expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(str(r['count']), size=11,
                                                font_family="Poppins-SemiBold", color=_WHITE),
                                bgcolor=_ACCENT,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                border_radius=10,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(vertical=6, horizontal=4),
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Top Reporters", size=13,
                            font_family="Poppins-SemiBold", color=_NAVY),
                    ft.Container(height=8),
                    *rows,
                ],
                spacing=2,
            ),
            padding=ft.padding.all(16),
            bgcolor=_CARD,
            border_radius=14,
            border=ft.border.all(1, _BORDER),
        )

    # ────────────────────────────────────────────
    #  Status distribution (horizontal stacked bar)
    # ────────────────────────────────────────────
    @staticmethod
    def status_distribution_bar(counts, total):
        """Single horizontal stacked bar showing status proportions.

        Args:
            counts: dict like {'pending': 3, 'in progress': 2, …}
            total: total reports count
        """
        if total == 0:
            return ft.Container()

        color_map = {
            'pending': _AMBER,
            'in progress': _BLUE,
            'resolved': _GREEN,
            'rejected': _RED,
        }
        label_map = {
            'pending': 'Pending',
            'in progress': 'In Progress',
            'resolved': 'Resolved',
            'rejected': 'Rejected',
        }

        segments = []
        for key in ['pending', 'in progress', 'resolved', 'rejected']:
            c = counts.get(key, 0)
            if c == 0:
                continue
            pct = c / total
            segments.append(
                ft.Container(
                    bgcolor=color_map[key],
                    border_radius=4,
                    height=12,
                    expand=int(max(pct * 100, 1)),
                    tooltip=f"{label_map[key]}: {c} ({pct:.0%})",
                )
            )

        legend_items = []
        for key in ['pending', 'in progress', 'resolved', 'rejected']:
            c = counts.get(key, 0)
            if c == 0:
                continue
            legend_items.append(
                ft.Row(
                    [
                        ft.Container(width=8, height=8, border_radius=4,
                                     bgcolor=color_map[key]),
                        ft.Text(f"{label_map[key]} {c}", size=10,
                                font_family="Poppins-Medium", color=_NAVY_MUTED),
                    ],
                    spacing=4,
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Status Distribution", size=13,
                            font_family="Poppins-SemiBold", color=_NAVY),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Row(segments, spacing=2, expand=True),
                        border_radius=6,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        height=12,
                    ),
                    ft.Container(height=8),
                    ft.Row(legend_items, spacing=12, wrap=True),
                ],
                spacing=0,
            ),
            padding=ft.padding.all(16),
            bgcolor=_CARD,
            border_radius=14,
            border=ft.border.all(1, _BORDER),
        )
