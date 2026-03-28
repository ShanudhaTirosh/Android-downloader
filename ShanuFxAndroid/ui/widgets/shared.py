"""
Shanu Fx Android - Shared Kivy Widgets
Reusable touch-friendly components for the Android UI.
Author: Shanudha Tirosh
"""

from kivy.uix.boxlayout    import BoxLayout
from kivy.uix.floatlayout  import FloatLayout
from kivy.uix.label        import Label
from kivy.uix.button       import Button
from kivy.uix.textinput    import TextInput
from kivy.uix.progressbar  import ProgressBar
from kivy.uix.scrollview   import ScrollView
from kivy.uix.widget       import Widget
from kivy.graphics          import Color, RoundedRectangle, Rectangle, Line
from kivy.metrics           import dp, sp
from kivy.properties        import StringProperty, NumericProperty, ListProperty
from kivy.clock             import Clock

from ui.theme import C, HEX, SP, DP


# ─── Helper: draw rounded background on any widget ────────────────────────────

def add_bg(widget, color, radius=14):
    """Add a rounded rectangle background to a widget."""
    with widget.canvas.before:
        Color(*color)
        widget._bg_rect = RoundedRectangle(
            pos=widget.pos, size=widget.size, radius=[dp(radius)]
        )
    widget.bind(
        pos=lambda w, v:  setattr(w._bg_rect, 'pos', v),
        size=lambda w, v: setattr(w._bg_rect, 'size', v),
    )


# ─── Card ─────────────────────────────────────────────────────────────────────

class Card(BoxLayout):
    """Dark rounded card container — glassmorphism style."""

    def __init__(self, radius=16, bg=None, border=True, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        kwargs.setdefault("padding",     dp(DP["card_padding"]))
        kwargs.setdefault("spacing",     dp(8))
        super().__init__(**kwargs)
        bg_color = bg or C["bg_card"]

        with self.canvas.before:
            # Background
            Color(*bg_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
            # Border
            if border:
                Color(*C["border"])
                self._border = RoundedRectangle(pos=self.pos, size=self.size,
                                                 radius=[dp(radius)])
        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self._bg.pos  = self.pos
        self._bg.size = self.size
        if hasattr(self, '_border'):
            self._border.pos  = self.pos
            self._border.size = self.size


# ─── Section Title ────────────────────────────────────────────────────────────

class SectionTitle(Label):
    def __init__(self, text, **kwargs):
        kwargs.setdefault("font_size",   sp(SP["md"]))
        kwargs.setdefault("bold",        True)
        kwargs.setdefault("color",       C["text_primary"])
        kwargs.setdefault("halign",      "left")
        kwargs.setdefault("valign",      "middle")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height",      dp(32))
        super().__init__(text=text, **kwargs)
        self.bind(size=lambda w, v: setattr(w, 'text_size', v))


class BodyLabel(Label):
    def __init__(self, text="", color=None, size=None, **kwargs):
        kwargs.setdefault("color",       color or C["text_secondary"])
        kwargs.setdefault("font_size",   sp(size or SP["body"]))
        kwargs.setdefault("halign",      "left")
        kwargs.setdefault("valign",      "middle")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height",      dp(26))
        super().__init__(text=text, **kwargs)
        self.bind(size=lambda w, v: setattr(w, 'text_size', v))


# ─── Accent Button ────────────────────────────────────────────────────────────

class AccentButton(Button):
    """Purple accent button with rounded corners."""

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y",  None)
        kwargs.setdefault("height",       dp(DP["btn_height"]))
        kwargs.setdefault("font_size",    sp(SP["sm"]))
        kwargs.setdefault("bold",         True)
        kwargs.setdefault("color",        (1, 1, 1, 1))
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("background_normal", "")
        super().__init__(**kwargs)

        with self.canvas.before:
            self._btn_color = Color(*C["accent"])
            self._btn_bg    = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._upd, size=self._upd)
        self.bind(on_press=self._press, on_release=self._release)

    def _upd(self, *_):
        self._btn_bg.pos  = self.pos
        self._btn_bg.size = self.size

    def _press(self, *_):
        self._btn_color.rgba = C["accent_hover"]

    def _release(self, *_):
        self._btn_color.rgba = C["accent"]


class SecondaryButton(Button):
    """Dark secondary button."""

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y",  None)
        kwargs.setdefault("height",       dp(DP["btn_height"]))
        kwargs.setdefault("font_size",    sp(SP["sm"]))
        kwargs.setdefault("color",        C["text_secondary"])
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("background_normal", "")
        super().__init__(**kwargs)

        with self.canvas.before:
            self._col = Color(*C["bg_elevated"])
            self._bg  = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
            Color(*C["border"])
            self._border = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *_):
        for attr in ('_bg', '_border'):
            r = getattr(self, attr)
            r.pos  = self.pos
            r.size = self.size


# ─── Styled TextInput ─────────────────────────────────────────────────────────

class DarkInput(TextInput):
    """Dark-themed single-line text input."""

    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y",   None)
        kwargs.setdefault("height",        dp(DP["input_height"]))
        kwargs.setdefault("font_size",     sp(SP["body"]))
        kwargs.setdefault("foreground_color", C["text_primary"])
        kwargs.setdefault("background_color", C["bg_elevated"])
        kwargs.setdefault("cursor_color",  C["accent"])
        kwargs.setdefault("hint_text_color", C["text_muted"])
        kwargs.setdefault("multiline",     False)
        kwargs.setdefault("padding",       [dp(14), dp(14)])
        super().__init__(**kwargs)


# ─── Progress Bar ─────────────────────────────────────────────────────────────

class AccentProgressBar(BoxLayout):
    """Colored rounded progress bar with percentage label."""

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation",  "vertical")
        kwargs.setdefault("size_hint_y",  None)
        kwargs.setdefault("height",       dp(28))
        kwargs.setdefault("spacing",      dp(4))
        super().__init__(**kwargs)
        self._value = 0.0
        self._color = C["accent"]
        self._build()

    def _build(self):
        # Track
        track = FloatLayout(size_hint_y=None, height=dp(10))
        with track.canvas:
            Color(*C["bg_elevated"])
            self._track_rect = RoundedRectangle(pos=track.pos, size=track.size, radius=[dp(5)])
            Color(*self._color)
            self._fill_rect  = RoundedRectangle(pos=track.pos, size=(0, track.height), radius=[dp(5)])
        track.bind(pos=self._update_track, size=self._update_track)
        self._track = track
        self.add_widget(track)

    def _update_track(self, *_):
        t = self._track
        self._track_rect.pos  = t.pos
        self._track_rect.size = t.size
        fill_w = t.width * (self._value / 100.0)
        self._fill_rect.pos  = t.pos
        self._fill_rect.size = (fill_w, t.height)

    def set_value(self, val: float, color=None):
        self._value = max(0.0, min(val, 100.0))
        if color:
            self._color = color
        self._update_track()

    def set_color(self, color):
        self._color = color
        with self._track.canvas:
            Color(*color)


# ─── Status Badge ─────────────────────────────────────────────────────────────

class StatusBadge(Label):
    STATUS_COLORS = {
        "done":        C["accent_green"],
        "downloading": C["accent"],
        "paused":      C["accent_orange"],
        "error":       C["accent_red"],
        "queued":      C["text_muted"],
        "processing":  C["accent_orange"],
        "cancelled":   C["text_muted"],
    }

    def __init__(self, status="queued", **kwargs):
        color = self.STATUS_COLORS.get(status, C["text_muted"])
        kwargs.setdefault("font_size",   sp(SP["caption"]))
        kwargs.setdefault("size_hint",   (None, None))
        kwargs.setdefault("size",        (dp(90), dp(22)))
        kwargs.setdefault("color",       color)
        super().__init__(text=f" {status.upper()} ", **kwargs)
        add_bg(self, (*color[:3], 0.18), radius=6)

    def set_status(self, status: str):
        color = self.STATUS_COLORS.get(status, C["text_muted"])
        self.text  = f" {status.upper()} "
        self.color = color


# ─── Divider ─────────────────────────────────────────────────────────────────

class Divider(Widget):
    def __init__(self, **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height",      dp(1))
        super().__init__(**kwargs)
        with self.canvas:
            Color(*C["border"])
            self._line = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w, v:  setattr(w._line, 'pos', v),
                  size=lambda w, v: setattr(w._line, 'size', v))


# ─── Toast Notification ──────────────────────────────────────────────────────

class ToastLabel(Label):
    """Temporary popup message at bottom of screen."""

    def __init__(self, message: str, duration: float = 3.0, **kwargs):
        kwargs.setdefault("size_hint",  (0.85, None))
        kwargs.setdefault("height",     dp(48))
        kwargs.setdefault("font_size",  sp(SP["sm"]))
        kwargs.setdefault("color",      C["text_primary"])
        kwargs.setdefault("halign",     "center")
        super().__init__(text=message, **kwargs)
        add_bg(self, C["bg_elevated"], radius=12)
        Clock.schedule_once(lambda dt: self.parent.remove_widget(self)
                             if self.parent else None, duration)


def show_toast(root_widget, message: str, color=None):
    """Show a toast at the bottom of root_widget."""
    toast = ToastLabel(message)
    toast.pos_hint = {"center_x": 0.5, "y": 0.05}
    root_widget.add_widget(toast)
