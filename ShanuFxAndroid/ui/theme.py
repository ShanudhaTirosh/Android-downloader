"""
Shanu Fx Android - Kivy Theme
Colors, font sizes, and spacing constants matching the desktop dark theme.
Author: Shanudha Tirosh
"""

# ─── Colors (rgba 0-1 float tuples for Kivy) ─────────────────────────────────

def hex_to_kivy(h: str, a: float = 1.0):
    """Convert #RRGGBB hex to Kivy (r,g,b,a) 0-1 tuple."""
    h = h.lstrip("#")
    return (int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255, a)


C = {
    # Backgrounds
    "bg_primary":    hex_to_kivy("#0B0B18"),
    "bg_secondary":  hex_to_kivy("#111127"),
    "bg_card":       hex_to_kivy("#161630"),
    "bg_elevated":   hex_to_kivy("#1C1C3A"),
    "bg_hover":      hex_to_kivy("#22224A"),

    # Sidebar
    "sidebar_bg":    hex_to_kivy("#080815"),
    "sidebar_active":hex_to_kivy("#1E1E50"),

    # Accents
    "accent":        hex_to_kivy("#7C3AED"),
    "accent_hover":  hex_to_kivy("#6D28D9"),
    "accent_light":  hex_to_kivy("#A78BFA"),
    "accent_2":      hex_to_kivy("#EC4899"),
    "accent_green":  hex_to_kivy("#10B981"),
    "accent_orange": hex_to_kivy("#F59E0B"),
    "accent_red":    hex_to_kivy("#EF4444"),
    "accent_blue":   hex_to_kivy("#3B82F6"),

    # Text
    "text_primary":  hex_to_kivy("#F1F1FF"),
    "text_secondary":hex_to_kivy("#9090B8"),
    "text_muted":    hex_to_kivy("#5A5A80"),
    "text_accent":   hex_to_kivy("#A78BFA"),

    # Borders
    "border":        hex_to_kivy("#252548"),
    "border_accent": hex_to_kivy("#7C3AED"),

    # Status
    "status_active": hex_to_kivy("#10B981"),
    "status_paused": hex_to_kivy("#F59E0B"),
    "status_error":  hex_to_kivy("#EF4444"),
    "status_queued": hex_to_kivy("#6B7280"),

    # Transparent
    "transparent":   (0, 0, 0, 0),
}

# Hex versions (for KV string templates)
HEX = {
    "bg_primary":    "#0B0B18",
    "bg_card":       "#161630",
    "bg_elevated":   "#1C1C3A",
    "accent":        "#7C3AED",
    "accent_light":  "#A78BFA",
    "accent_2":      "#EC4899",
    "accent_green":  "#10B981",
    "accent_orange": "#F59E0B",
    "accent_red":    "#EF4444",
    "text_primary":  "#F1F1FF",
    "text_secondary":"#9090B8",
    "text_muted":    "#5A5A80",
    "border":        "#252548",
}

# ─── Font Sizes (sp — scales with Android display density) ───────────────────
SP = {
    "xl":    28,
    "lg":    22,
    "md":    16,
    "sm":    13,
    "xs":    11,
    "body":  14,
    "caption": 11,
}

# ─── Spacing / Sizing ─────────────────────────────────────────────────────────
DP = {
    "padding_lg":   24,
    "padding_md":   16,
    "padding_sm":   10,
    "radius_lg":    20,
    "radius_md":    14,
    "radius_sm":    8,
    "btn_height":   52,
    "input_height": 50,
    "nav_height":   64,
    "icon_size":    26,
    "card_padding": 16,
}
