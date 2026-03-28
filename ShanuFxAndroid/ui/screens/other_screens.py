"""
Shanu Fx Android - History / Settings / About Screens
Author: Shanudha Tirosh
"""

import webbrowser

from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.scrollview  import ScrollView
from kivy.uix.label       import Label
from kivy.uix.button      import Button
from kivy.uix.switch      import Switch
from kivy.uix.slider      import Slider
from kivy.metrics          import dp, sp
from kivy.clock            import Clock

from ui.theme   import C, SP, DP, HEX
from ui.widgets.shared import (Card, SectionTitle, BodyLabel, AccentButton,
                                SecondaryButton, DarkInput, StatusBadge,
                                Divider, show_toast, add_bg)
from downloader.history       import history_manager, HistoryEntry
from core.config              import (config, APP_NAME, APP_VERSION,
                                       APP_AUTHOR, APP_GITHUB,
                                       VIDEO_QUALITIES, AUDIO_BITRATES)


# ══════════════════════════════════════════════════════════════════════════════
#  HISTORY SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class HistoryRow(BoxLayout):
    def __init__(self, entry, on_delete, **kwargs):
        kwargs.setdefault("orientation",  "horizontal")
        kwargs.setdefault("size_hint_y",  None)
        kwargs.setdefault("height",       dp(64))
        kwargs.setdefault("spacing",      dp(8))
        kwargs.setdefault("padding",      [dp(4), dp(6)])
        super().__init__(**kwargs)

        icon = Label(text=entry.type_icon, font_size=sp(20),
                      size_hint=(None,1), width=dp(32))
        self.add_widget(icon)

        info = BoxLayout(orientation="vertical", spacing=dp(2))
        title = entry.title[:34]+"…" if len(entry.title)>34 else entry.title
        info.add_widget(Label(text=title, font_size=sp(SP["sm"]),
                               color=C["text_primary"],
                               halign="left", valign="middle",
                               size_hint_y=None, height=dp(22)))
        meta = f"{entry.platform} · {entry.size_str} · {entry.timestamp}"
        info.add_widget(Label(text=meta, font_size=sp(SP["caption"]),
                               color=C["text_muted"],
                               halign="left", valign="middle",
                               size_hint_y=None, height=dp(18)))
        self.add_widget(info)

        del_btn = Button(text="✕", color=C["accent_red"],
                          size_hint=(None,None), size=(dp(36),dp(36)),
                          background_normal="", background_color=(0,0,0,0))
        add_bg(del_btn, C["bg_elevated"], radius=8)
        del_btn.bind(on_release=lambda *_: on_delete(entry.id))
        self.add_widget(del_btn)


class HistoryScreen(BoxLayout):
    def __init__(self, navigate_cb, root_widget, **kwargs):
        kwargs.setdefault("orientation","vertical")
        super().__init__(**kwargs)
        self._navigate = navigate_cb
        self._root     = root_widget
        self._build()

    def _build(self):
        # Header
        hdr = BoxLayout(orientation="horizontal", size_hint_y=None,
                         height=dp(52), padding=[dp(16),dp(8)], spacing=dp(8))
        hdr.add_widget(Label(text="History", font_size=sp(SP["xl"]),
                              bold=True, color=C["text_primary"],
                              halign="left", valign="middle"))
        clr = SecondaryButton(text="🗑 Clear", size_hint_x=None,
                               width=dp(90), height=dp(40))
        clr.bind(on_release=self._clear_all)
        hdr.add_widget(clr)
        self.add_widget(hdr)

        # Stats
        self._stats_lbl = BodyLabel("0 downloads", color=C["text_muted"])
        self.add_widget(self._stats_lbl)
        self.add_widget(Divider())

        # List
        scroll = ScrollView(do_scroll_x=False)
        self._list = BoxLayout(orientation="vertical", size_hint_y=None,
                                spacing=dp(6),
                                padding=[dp(12), dp(8), dp(12), dp(16)])
        self._list.bind(minimum_height=self._list.setter("height"))
        scroll.add_widget(self._list)
        self.add_widget(scroll)
        self._refresh()

    def _refresh(self):
        self._list.clear_widgets()
        entries = history_manager.get_all()
        self._stats_lbl.text = f"{len(entries)} downloads"
        if not entries:
            self._list.add_widget(BodyLabel(
                "No history yet", color=C["text_muted"]))
            return
        for i, entry in enumerate(entries):
            self._list.add_widget(HistoryRow(entry, on_delete=self._delete))
            if i < len(entries)-1:
                self._list.add_widget(Divider())

    def _delete(self, entry_id):
        history_manager.remove(entry_id)
        self._refresh()

    def _clear_all(self, *_):
        history_manager.clear()
        self._refresh()
        show_toast(self._root, "History cleared")


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class SettingToggleRow(BoxLayout):
    def __init__(self, label, desc, config_key, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height",      dp(56))
        kwargs.setdefault("spacing",     dp(10))
        super().__init__(**kwargs)
        self._key = config_key

        text_col = BoxLayout(orientation="vertical", spacing=dp(2))
        text_col.add_widget(Label(text=label, font_size=sp(SP["sm"]),
                                   color=C["text_primary"],
                                   halign="left", valign="middle",
                                   size_hint_y=None, height=dp(22)))
        text_col.add_widget(Label(text=desc, font_size=sp(SP["caption"]),
                                   color=C["text_muted"],
                                   halign="left", valign="middle",
                                   size_hint_y=None, height=dp(18)))
        self.add_widget(text_col)

        self._sw = Switch(active=config.get(config_key, True),
                           size_hint=(None,None), size=(dp(80), dp(40)))
        self._sw.bind(active=self._on_toggle)
        self.add_widget(self._sw)

    def _on_toggle(self, _, value):
        config.set(self._key, value)


class SettingsScreen(BoxLayout):
    def __init__(self, navigate_cb, root_widget, **kwargs):
        kwargs.setdefault("orientation","vertical")
        super().__init__(**kwargs)
        self._navigate = navigate_cb
        self._root     = root_widget
        self._build()

    def _build(self):
        scroll = ScrollView(do_scroll_x=False)
        inner  = BoxLayout(orientation="vertical", size_hint_y=None,
                            spacing=dp(14),
                            padding=[dp(16), dp(12), dp(16), dp(24)])
        inner.bind(minimum_height=inner.setter("height"))
        scroll.add_widget(inner)
        self.add_widget(scroll)

        inner.add_widget(Label(text="Settings", font_size=sp(SP["xl"]),
                                bold=True, color=C["text_primary"],
                                halign="left", valign="middle",
                                size_hint_y=None, height=dp(40)))

        # ── Download folder ────────────────────────────────────
        folder_card = Card()
        inner.add_widget(folder_card)
        folder_card.add_widget(SectionTitle("Download Location"))
        self._dir_input = DarkInput(
            text=config.get("download_dir", "/sdcard/ShanuFx"),
            hint_text="/sdcard/ShanuFx",
        )
        folder_card.add_widget(self._dir_input)

        # ── Threads slider ─────────────────────────────────────
        threads_card = Card()
        inner.add_widget(threads_card)
        threads_card.add_widget(SectionTitle("Download Threads"))

        sldr_row = BoxLayout(orientation="horizontal",
                              size_hint_y=None, height=dp(44), spacing=dp(12))
        self._threads_lbl = Label(
            text=str(config.get("max_threads", 8)),
            font_size=sp(SP["md"]), bold=True,
            color=C["accent"], size_hint=(None,1), width=dp(36),
        )
        sldr = Slider(min=1, max=32, value=config.get("max_threads", 8),
                       step=1, size_hint_x=1,
                       cursor_size=(dp(24), dp(24)),
                       value_track=True, value_track_color=C["accent"])
        def on_sldr(_, v):
            v = int(v)
            self._threads_lbl.text = str(v)
            config.set("max_threads", v)
        sldr.bind(value=on_sldr)
        sldr_row.add_widget(sldr)
        sldr_row.add_widget(self._threads_lbl)
        threads_card.add_widget(sldr_row)

        # ── Toggles ────────────────────────────────────────────
        toggles_card = Card()
        inner.add_widget(toggles_card)
        toggles_card.add_widget(SectionTitle("Behavior"))

        toggles = [
            ("Clipboard Detection",  "Auto-detect URLs from clipboard", "clipboard_detection"),
            ("Show Notifications",   "Toast alerts on events",           "show_notifications"),
            ("Auto-Start Downloads", "Download immediately",             "auto_start_download"),
        ]
        for label, desc, key in toggles:
            toggles_card.add_widget(SettingToggleRow(label, desc, key))
            toggles_card.add_widget(Divider())

        # ── Save button ────────────────────────────────────────
        save_btn = AccentButton(text="✓  Save Settings")
        save_btn.bind(on_release=self._save)
        inner.add_widget(save_btn)

    def _save(self, *_):
        config.set("download_dir", self._dir_input.text.strip())
        show_toast(self._root, "Settings saved ✓")


# ══════════════════════════════════════════════════════════════════════════════
#  ABOUT SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class AboutScreen(BoxLayout):
    def __init__(self, navigate_cb, root_widget, **kwargs):
        kwargs.setdefault("orientation","vertical")
        super().__init__(**kwargs)
        self._navigate = navigate_cb
        self._root     = root_widget
        self._build()

    def _build(self):
        scroll = ScrollView(do_scroll_x=False)
        inner  = BoxLayout(orientation="vertical", size_hint_y=None,
                            spacing=dp(14),
                            padding=[dp(16), dp(12), dp(16), dp(24)])
        inner.bind(minimum_height=inner.setter("height"))
        scroll.add_widget(inner)
        self.add_widget(scroll)

        # App hero card
        hero = Card()
        inner.add_widget(hero)

        hero.add_widget(Label(text="⬡", font_size=sp(52), bold=True,
                               color=C["accent"], size_hint_y=None, height=dp(64)))
        hero.add_widget(Label(text=APP_NAME, font_size=sp(SP["lg"]),
                               bold=True, color=C["text_primary"],
                               halign="center", valign="middle",
                               size_hint_y=None, height=dp(32)))
        hero.add_widget(Label(text=f"Version {APP_VERSION}  ·  Android Edition",
                               font_size=sp(SP["sm"]),
                               color=C["text_secondary"],
                               halign="center", valign="middle",
                               size_hint_y=None, height=dp(24)))
        hero.add_widget(Divider())
        hero.add_widget(BodyLabel(
            "All-in-one media downloader for Android.\n"
            "Download from YouTube, TikTok, Instagram, Facebook\n"
            "and 1000+ sites. Powered by yt-dlp.",
            color=C["text_secondary"],
        ))

        # Dev card
        dev = Card()
        inner.add_widget(dev)
        dev.add_widget(SectionTitle("Developer"))
        dev.add_widget(Divider())

        dev_row = BoxLayout(orientation="horizontal",
                             size_hint_y=None, height=dp(60),
                             spacing=dp(12))
        avatar = Label(text="ST", font_size=sp(24), bold=True,
                        color=C["accent"],
                        size_hint=(None,1), width=dp(52))
        add_bg(avatar, (*C["accent"][:3], 0.2), radius=26)
        dev_row.add_widget(avatar)

        info_col = BoxLayout(orientation="vertical", spacing=dp(4))
        info_col.add_widget(Label(text=APP_AUTHOR, font_size=sp(SP["md"]),
                                   bold=True, color=C["text_primary"],
                                   halign="left", valign="middle",
                                   size_hint_y=None, height=dp(26)))
        info_col.add_widget(Label(text="Full-Stack Dev · Sri Lanka 🇱🇰",
                                   font_size=sp(SP["caption"]),
                                   color=C["text_secondary"],
                                   halign="left", valign="middle",
                                   size_hint_y=None, height=dp(20)))
        dev_row.add_widget(info_col)
        dev.add_widget(dev_row)

        # Social buttons
        links = [
            ("⭐  GitHub",    APP_GITHUB,                          C["accent"]),
            ("📸  Instagram", "https://www.instagram.com/shanu.fx/", C["accent_2"]),
        ]
        for label, url, color in links:
            btn = Button(text=label, font_size=sp(SP["sm"]),
                          color=color,
                          size_hint_y=None, height=dp(46),
                          background_normal="", background_color=(0,0,0,0))
            add_bg(btn, (*color[:3], 0.15), radius=10)
            btn.bind(on_release=lambda *_, u=url: webbrowser.open(u))
            dev.add_widget(btn)

        # Tech stack
        tech = Card()
        inner.add_widget(tech)
        tech.add_widget(SectionTitle("Tech Stack"))
        tech.add_widget(Divider())

        stack = [
            ("🐍", "Python 3.11",    "Core language"),
            ("📱", "Kivy 2.x",       "Android UI framework"),
            ("⬇",  "yt-dlp",         "Media downloader"),
            ("🎬", "FFmpeg",          "Video processing"),
        ]
        for icon, name, desc in stack:
            row = BoxLayout(orientation="horizontal",
                             size_hint_y=None, height=dp(40), spacing=dp(10))
            row.add_widget(Label(text=icon, font_size=sp(18),
                                  size_hint=(None,1), width=dp(30)))
            col = BoxLayout(orientation="vertical")
            col.add_widget(Label(text=name, font_size=sp(SP["sm"]),
                                  bold=True, color=C["text_primary"],
                                  halign="left", valign="middle",
                                  size_hint_y=None, height=dp(20)))
            col.add_widget(Label(text=desc, font_size=sp(SP["caption"]),
                                  color=C["text_muted"],
                                  halign="left", valign="middle",
                                  size_hint_y=None, height=dp(16)))
            row.add_widget(col)
            tech.add_widget(row)

        # Copyright
        inner.add_widget(Label(
            text=f"© 2025 {APP_AUTHOR}  ·  {APP_NAME}",
            font_size=sp(SP["caption"]), color=C["text_muted"],
            halign="center", size_hint_y=None, height=dp(30),
        ))
