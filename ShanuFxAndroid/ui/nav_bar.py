"""
Shanu Fx Android - Bottom Navigation Bar
Android-style bottom tab bar with icons and active state.
Author: Shanudha Tirosh
"""

from kivy.uix.boxlayout  import BoxLayout
from kivy.uix.button     import Button
from kivy.uix.label      import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics        import Color, RoundedRectangle, Rectangle
from kivy.metrics         import dp, sp

from ui.theme import C, SP

# ─── Nav Tabs definition ──────────────────────────────────────────────────────

NAV_TABS = [
    ("home",       "⌂",  "Home"),
    ("downloader", "⬇",  "Downloader"),
    ("manager",    "⚡",  "Manager"),
    ("history",    "🕘",  "History"),
    ("settings",   "⚙",  "More"),
]


# ─── Single Tab Button ────────────────────────────────────────────────────────

class TabButton(BoxLayout):
    def __init__(self, icon, label, page_key, navigate_cb, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("spacing",     dp(2))
        kwargs.setdefault("padding",     [dp(4), dp(6)])
        super().__init__(**kwargs)

        self.page_key    = page_key
        self._navigate   = navigate_cb
        self._active     = False

        self._icon_lbl = Label(
            text=icon,
            font_size=sp(22),
            color=C["text_muted"],
            size_hint_y=None, height=dp(28),
            halign="center", valign="middle",
        )
        self._text_lbl = Label(
            text=label,
            font_size=sp(9),
            color=C["text_muted"],
            size_hint_y=None, height=dp(14),
            halign="center", valign="middle",
        )

        self.add_widget(self._icon_lbl)
        self.add_widget(self._text_lbl)

        # Active indicator dot (hidden by default)
        self._dot = FloatLayout(size_hint_y=None, height=dp(4))
        with self._dot.canvas:
            self._dot_color = Color(*C["transparent"])
            self._dot_rect  = RoundedRectangle(
                pos=(0, 0), size=(dp(20), dp(4)), radius=[dp(2)]
            )
        self._dot.bind(pos=self._upd_dot, size=self._upd_dot)
        self.add_widget(self._dot)

        # Touch binding on the whole area
        self.bind(on_touch_down=self._on_touch)

    def _upd_dot(self, w, *_):
        cx = w.center_x - dp(10)
        self._dot_rect.pos  = (cx, w.y)
        self._dot_rect.size = (dp(20), dp(4))

    def _on_touch(self, widget, touch):
        if self.collide_point(*touch.pos):
            self._navigate(self.page_key)
            return True

    def set_active(self, active: bool):
        self._active = active
        if active:
            self._icon_lbl.color = C["accent"]
            self._text_lbl.color = C["accent_light"]
            self._dot_color.rgba = C["accent"]
        else:
            self._icon_lbl.color = C["text_muted"]
            self._text_lbl.color = C["text_muted"]
            self._dot_color.rgba = C["transparent"]


# ─── Bottom Nav Bar ───────────────────────────────────────────────────────────

class BottomNavBar(BoxLayout):
    """
    Android-style bottom navigation bar.
    Height: 64dp. Background: sidebar_bg with top border.
    """

    HEIGHT = dp(64)

    def __init__(self, navigate_cb, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height",      self.HEIGHT)
        super().__init__(**kwargs)

        self._navigate  = navigate_cb
        self._tab_btns  = {}

        # Background
        with self.canvas.before:
            Color(*C["sidebar_bg"])
            self._bg = Rectangle(pos=self.pos, size=self.size)
            # Top separator line
            Color(*C["border"])
            self._line = Rectangle(pos=self.pos, size=(self.width, dp(1)))
        self.bind(pos=self._upd, size=self._upd)

        # Build tab buttons
        for page_key, icon, label in NAV_TABS:
            btn = TabButton(icon, label, page_key, navigate_cb)
            self._tab_btns[page_key] = btn
            self.add_widget(btn)

    def _upd(self, *_):
        self._bg.pos   = self.pos
        self._bg.size  = self.size
        self._line.pos = self.pos
        self._line.size = (self.width, dp(1))

    def set_active(self, page_key: str):
        for key, btn in self._tab_btns.items():
            btn.set_active(key == page_key)
