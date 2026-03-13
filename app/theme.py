"""
Central theme/color definitions for FIXIT.
Provides light and dark palettes + a page-aware getter.
"""

LIGHT = {
    "BG":           "#F5F7FA",
    "NAVY":         "#0F2B5B",
    "NAVY_LIGHT":   "#1A3A6B",
    "NAVY_MUTED":   "#64748B",
    "ACCENT":       "#1565C0",
    "ACCENT_HOVER": "#0D47A1",
    "WHITE":        "#FFFFFF",
    "CARD":         "#FFFFFF",
    "BORDER":       "#E0E6ED",
    "BORDER_LIGHT": "#F1F5F9",
    # Status
    "PENDING_TEXT": "#B45309",
    "PENDING_BG":   "#FEF3C7",
    "ONGOING_TEXT": "#1565C0",
    "ONGOING_BG":   "#DBEAFE",
    "RESOLVED_TEXT":"#15803D",
    "RESOLVED_BG":  "#DCFCE7",
    "REJECTED_TEXT":"#DC2626",
    "REJECTED_BG":  "#FEE2E2",
    # Extra
    "GREEN":        "#15803D",
    "GREEN_BG":     "#DCFCE7",
    "RED":          "#DC2626",
    "RED_BG":       "#FEE2E2",
    "AMBER":        "#B45309",
    "AMBER_BG":     "#FEF3C7",
    # Login / form fields
    "FIELD_BORDER": "#CFD8DC",
    "FIELD_FOCUS":  "#1565C0",
    "TEXT_MUTED":   "#90A4AE",
    "DIVIDER":      "#E0E6ED",
}

DARK = {
    "BG":           "#0F172A",
    "NAVY":         "#F1F5F9",
    "NAVY_LIGHT":   "#E2E8F0",
    "NAVY_MUTED":   "#94A3B8",
    "ACCENT":       "#3B82F6",
    "ACCENT_HOVER": "#2563EB",
    "WHITE":        "#1E293B",
    "CARD":         "#1E293B",
    "BORDER":       "#334155",
    "BORDER_LIGHT": "#243048",
    # Status — lighter/brighter variants for dark backgrounds
    "PENDING_TEXT": "#FBBF24",
    "PENDING_BG":   "#292516",
    "ONGOING_TEXT": "#60A5FA",
    "ONGOING_BG":   "#172032",
    "RESOLVED_TEXT":"#34D399",
    "RESOLVED_BG":  "#0E2820",
    "REJECTED_TEXT":"#F87171",
    "REJECTED_BG":  "#301414",
    # Extra
    "GREEN":        "#34D399",
    "GREEN_BG":     "#0E2820",
    "RED":          "#F87171",
    "RED_BG":       "#301414",
    "AMBER":        "#FBBF24",
    "AMBER_BG":     "#292516",
    # Login / form fields
    "FIELD_BORDER": "#334155",
    "FIELD_FOCUS":  "#3B82F6",
    "TEXT_MUTED":   "#64748B",
    "DIVIDER":      "#334155",
}


def get_colors(page) -> dict:
    """Return the appropriate color dict for the current session theme."""
    is_dark = page.session.get("is_dark_theme") or False
    return DARK if is_dark else LIGHT


def is_dark_mode(page) -> bool:
    return page.session.get("is_dark_theme") or False
