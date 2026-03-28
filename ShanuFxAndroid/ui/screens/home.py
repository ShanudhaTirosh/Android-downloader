"""
Shanu Fx Android - Home Screen
Dashboard with live stats and quick-action cards.
Author: Shanudha Tirosh
"""

from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.scrollview  import ScrollView
from kivy.uix.label       import Label
from kivy.uix.button      import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics         import Color, RoundedRectangle
from kivy.metrics          import dp, sp
from kivy.clock            import Clock

from ui.theme   import C, SP, DP
from ui.widgets.shared import (Card, SectionTitle, BodyLabel,
                                AccentButton, SecondaryButton,
                                Divider, add_bg)
from downloader.history      import history_manager
from manager.download_manager import download_manager
from manager.multi_thread    import DownloadStatus


# ─── Stat Card ────────────────────────────────────────────────────────────────

class StatCard(BoxLayout):
    def __init__(self, icon, label, value, accent, **kwargs):
        kwargs.setdefault("orientation",  "vertical")
        kwargs.setdefault("size_hint_y",  None)
        kwargs.setdefault("height",       dp(110))
        kwargs.setdefault("padding",      dp(14))
        kwargs.setdefault("spacing",      dp(4))
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*C["bg_card"])
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            Color(*C["border"])
            self._bd = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
            # Accent top bar
            Color(*accent)
            self._bar = RoundedRectangle(pos=self.pos,
                                          size=(self.width, dp(3)),
                                          radius=[dp(16)])
        self.bind(pos=self._upd, size=self._upd)

        icon_lbl = Label(text=icon, font_size=sp(22),
                         size_hint_y=None, height=dp(28))
        self._val_lbl = Label(text=value, font_size=sp(SP["lg"]),
                               bold=True, color=C["text_primary"],
                               size_hint_y=None, height=dp(30))
        sub_lbl = Label(text=label, font_size=sp(SP["caption"]),
                         color=C["text_secondary"],
                         size_hint_y=None, height=dp(20))

        self.add_widget(icon_lbl)
        self.add_widget(self._val_lbl)
        self.add_widget(sub_lbl)

    def _upd(self, *_):
        self._bg.pos = self._bd.pos = self.pos
        self._bg.size = self._bd.size = self.size
        self._bar.pos  = self.pos
        self._bar.size = (self.width, dp(3))

    def update(self, value: str):
        self._val_lbl.text = value


# ─── Quick Action Card ────────────────────────────────────────────────────────

class QuickAction(Button):
    def __init__(self, icon, label, subtitle, accent, on_tap, **kwargs):
        kwargs.setdefault("size_hint_y",       None)
        kwargs.setdefault("height",            dp(90))
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_color",  (0,0,0,0))
        super().__init__(**kwargs)
        self.bind(on_release=lambda *_: on_tap())

        with self.canvas.before:
            Color(*C["bg_card"])
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._upd, size=self._upd)

        inner = BoxLayout(orientation="horizontal", spacing=dp(12), padding=dp(14))
        inner.pos  = self.pos
        inner.size = self.size
        self.bind(pos =lambda w,v: setattr(inner,'pos', v),
                  size=lambda w,v: setattr(inner,'size',v))

        # Icon circle
        circle = FloatLayout(size_hint=(None, None), size=(dp(44), dp(44)))
        with circle.canvas.before:
            Color(*accent[:3], 0.2)
            RoundedRectangle(pos=circle.pos, size=circle.size, radius=[dp(22)])
        icon_lbl = Label(text=icon, font_size=sp(20), color=accent,
                          size_hint=(1,1))
        circle.add_widget(icon_lbl)
        inner.add_widget(circle)

        text_col = BoxLayout(orientation="vertical", spacing=dp(2))
        text_col.add_widget(Label(text=label, font_size=sp(SP["sm"]),
                                   bold=True, color=C["text_primary"],
                                   halign="left", valign="middle",
                                   size_hint_y=None, height=dp(22)))
        text_col.add_widget(Label(text=subtitle, font_size=sp(SP["caption"]),
                                   color=C["text_secondary"],
                                   halign="left", valign="middle",
                                   size_hint_y=None, height=dp(18)))
        inner.add_widget(text_col)
        self.add_widget(inner)

    def _upd(self, *_):
        self._bg.pos  = self.pos
        self._bg.size = self.size


# ─── Recent Row ───────────────────────────────────────────────────────────────

class RecentRow(BoxLayout):
    def __init__(self, entry, **kwargs):
        kwargs.setdefault("orientation",  "horizontal")
        kwargs.setdefault("size_hint_y",  None)
        kwargs.setdefault("height",       dp(58))
        kwargs.setdefault("spacing",      dp(10))
        kwargs.setdefault("padding",      [dp(4), dp(6)])
        super().__init__(**kwargs)

        dot_color = C["accent_green"] if entry.status == "done" else C["accent_red"]
        dot = FloatLayout(size_hint=(None, None), size=(dp(10), dp(10)))
        with dot.canvas:
            Color(*dot_color)
            RoundedRectangle(pos=dot.pos, size=dot.size, radius=[dp(5)])
        dot.bind(pos=lambda w,v: None)
        self.add_widget(dot)

        icon_lbl = Label(text=entry.type_icon, font_size=sp(20),
                          size_hint=(None,1), width=dp(28))
        self.add_widget(icon_lbl)

        text_col = BoxLayout(orientation="vertical", spacing=dp(2))
        title = entry.title[:36] + ("…" if len(entry.title) > 36 else "")
        text_col.add_widget(Label(text=title, font_size=sp(SP["sm"]),
                                   color=C["text_primary"],
                                   halign="left", valign="middle",
                                   size_hint_y=None, height=dp(22)))
        meta = f"{entry.platform}  ·  {entry.timestamp}"
        text_col.add_widget(Label(text=meta, font_size=sp(SP["caption"]),
                                   color=C["text_muted"],
                                   halign="left", valign="middle",
                                   size_hint_y=None, height=dp(18)))
        self.add_widget(text_col)

        size_lbl = Label(text=entry.size_str, font_size=sp(SP["caption"]),
                          color=C["text_secondary"],
                          size_hint=(None,1), width=dp(60),
                          halign="right", valign="middle")
        self.add_widget(size_lbl)


# ─── Home Screen ─────────────────────────────────────────────────────────────

class HomeScreen(BoxLayout):
    """Main dashboard screen."""

    def __init__(self, navigate_cb, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        super().__init__(**kwargs)
        self._navigate = navigate_cb
        self._stat_widgets = {}
        self._build()
        Clock.schedule_interval(self._refresh_stats, 5)

    def _build(self):
        scroll = ScrollView(do_scroll_x=False)
        inner  = BoxLayout(orientation="vertical",
                            size_hint_y=None, spacing=dp(16),
                            padding=[dp(16), dp(12), dp(16), dp(20)])
        inner.bind(minimum_height=inner.setter("height"))
        scroll.add_widget(inner)
        self.add_widget(scroll)

        # ── Header ────────────────────────────────────────────
        inner.add_widget(Label(
            text="Dashboard",
            font_size=sp(SP["xl"]), bold=True,
            color=C["text_primary"],
            halign="left", valign="middle",
            size_hint_y=None, height=dp(40),
        ))
        inner.add_widget(BodyLabel(
            "Welcome back, Shanudha",
            color=C["text_secondary"],
        ))

        # ── Stats (2×2 grid) ──────────────────────────────────
        inner.add_widget(SectionTitle("Overview"))

        stats_top = BoxLayout(orientation="horizontal",
                               size_hint_y=None, height=dp(110),
                               spacing=dp(10))
        stats_bot = BoxLayout(orientation="horizontal",
                               size_hint_y=None, height=dp(110),
                               spacing=dp(10))

        stats_data = [
            ("⬇", "Total",    "0", C["accent"]),
            ("🎬", "Videos",  "0", C["accent_2"]),
            ("🎵", "Audio",   "0", C["accent_green"]),
            ("⚡", "Active",  "0", C["accent_orange"]),
        ]
        for i, (icon, label, val, accent) in enumerate(stats_data):
            card = StatCard(icon, label, val, accent)
            self._stat_widgets[label] = card
            (stats_top if i < 2 else stats_bot).add_widget(card)

        inner.add_widget(stats_top)
        inner.add_widget(stats_bot)

        # ── Quick Actions ─────────────────────────────────────
        inner.add_widget(SectionTitle("Quick Actions"))

        actions = [
            ("⬇", "Downloader",      "YouTube, TikTok & more",  C["accent"],
             lambda: self._navigate("downloader")),
            ("⚡", "DL Manager",      "Active downloads",         C["accent_2"],
             lambda: self._navigate("manager")),
            ("🕘", "History",         "Past downloads",           C["accent_green"],
             lambda: self._navigate("history")),
            ("⚙",  "Settings",        "Preferences",              C["accent_orange"],
             lambda: self._navigate("settings")),
        ]
        for icon, label, sub, accent, cb in actions:
            inner.add_widget(QuickAction(icon, label, sub, accent, cb))

        # ── Recent ────────────────────────────────────────────
        inner.add_widget(SectionTitle("Recent Downloads"))
        self._recent_card = Card()
        inner.add_widget(self._recent_card)
        self._refresh_recent()

    def _refresh_stats(self, *_):
        self._stat_widgets["Total"].update(str(history_manager.count))
        self._stat_widgets["Videos"].update(str(len(history_manager.filter_by_type("video"))))
        self._stat_widgets["Audio"].update(str(len(history_manager.filter_by_type("audio"))))
        self._stat_widgets["Active"].update(str(download_manager.active_count()))
        self._refresh_recent()

    def _refresh_recent(self, *_):
        self._recent_card.clear_widgets()
        entries = history_manager.get_all()[:5]
        if not entries:
            self._recent_card.add_widget(BodyLabel(
                "No downloads yet", color=C["text_muted"]))
            return
        for i, e in enumerate(entries):
            self._recent_card.add_widget(RecentRow(e))
            if i < len(entries) - 1:
                self._recent_card.add_widget(Divider())
