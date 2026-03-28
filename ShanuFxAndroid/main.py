"""
Shanu Fx Private Downloader — Android Edition
══════════════════════════════════════════════
Author:  Shanudha Tirosh
GitHub:  https://github.com/ShanudhaTirosh
Version: 1.0.0  (Android)

Entry point — Kivy App class that bootstraps all screens and navigation.
══════════════════════════════════════════════
"""

import os
import sys

# ── Add project root to path ──────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Kivy config MUST be set before importing kivy.core ───────────────────────
os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

from kivy.config  import Config
Config.set("graphics", "resizable", "1")
Config.set("kivy",     "log_level",  "warning")

from kivy.app               import App
from kivy.uix.boxlayout     import BoxLayout
from kivy.uix.floatlayout   import FloatLayout
from kivy.uix.label         import Label
from kivy.graphics           import Color, Rectangle
from kivy.metrics            import dp, sp
from kivy.core.window        import Window
from kivy.clock              import Clock

from ui.theme    import C, SP
from ui.nav_bar  import BottomNavBar

# ── Screen imports ────────────────────────────────────────────────────────────
from ui.screens.home        import HomeScreen
from ui.screens.downloader  import DownloaderScreen
from ui.screens.manager     import ManagerScreen
from ui.screens.other_screens import (HistoryScreen, SettingsScreen, AboutScreen)

# ── Config init ───────────────────────────────────────────────────────────────
from core.config import config, APP_NAME, APP_VERSION


# ─── Top Bar ──────────────────────────────────────────────────────────────────

class TopBar(BoxLayout):
    """App-wide top bar with title and version badge."""

    HEIGHT = dp(56)

    def __init__(self, **kwargs):
        kwargs.setdefault("orientation", "horizontal")
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height",      self.HEIGHT)
        kwargs.setdefault("padding",     [dp(16), dp(8)])
        kwargs.setdefault("spacing",     dp(10))
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*C["sidebar_bg"])
            self._bg = Rectangle(pos=self.pos, size=self.size)
            Color(*C["border"])
            self._line = Rectangle(pos=(self.x, self.y),
                                    size=(self.width, dp(1)))
        self.bind(pos=self._upd, size=self._upd)

        # Logo icon
        self._icon = Label(
            text="⬡", font_size=sp(22), bold=True,
            color=C["accent"], size_hint=(None,1), width=dp(32),
        )
        self.add_widget(self._icon)

        # Title
        self._title = Label(
            text="Shanu Fx", font_size=sp(SP["md"]),
            bold=True, color=C["text_primary"],
            halign="left", valign="middle",
        )
        self._title.bind(size=lambda w,v: setattr(w,'text_size',v))
        self.add_widget(self._title)

        # Version badge
        badge = Label(
            text=f"  v{APP_VERSION}  ",
            font_size=sp(SP["caption"]),
            color=C["accent_light"],
            size_hint=(None, None),
            size=(dp(60), dp(24)),
            halign="center",
        )
        with badge.canvas.before:
            Color(*C["accent"][:3], 0.2)
            from kivy.graphics import RoundedRectangle
            self._badge_bg = RoundedRectangle(
                pos=badge.pos, size=badge.size, radius=[dp(6)]
            )
        badge.bind(
            pos=lambda w,v:  setattr(self._badge_bg,'pos', v),
            size=lambda w,v: setattr(self._badge_bg,'size',v),
        )
        self.add_widget(badge)

    def set_title(self, title: str):
        self._title.text = title

    def _upd(self, *_):
        self._bg.pos   = self.pos
        self._bg.size  = self.size
        self._line.pos = (self.x, self.y)
        self._line.size = (self.width, dp(1))


# ─── Root Layout ──────────────────────────────────────────────────────────────

class RootLayout(FloatLayout):
    """
    Full-screen layout:
    ┌──────────────────┐
    │   TopBar  56dp   │
    ├──────────────────┤
    │                  │
    │   Page Content   │
    │                  │
    ├──────────────────┤
    │  BottomNav 64dp  │
    └──────────────────┘
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(*C["bg_primary"])
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda w,v: setattr(w._bg,'pos',v),
                  size=lambda w,v: setattr(w._bg,'size',v))

        # ── Top bar ──────────────────────────────────────────────
        self._topbar = TopBar()
        self._topbar.pos_hint = {"top": 1, "x": 0}
        self._topbar.size_hint_x = 1
        self.add_widget(self._topbar)

        # ── Bottom nav ───────────────────────────────────────────
        self._navbar = BottomNavBar(navigate_cb=self._navigate)
        self._navbar.pos_hint = {"bottom": 1, "x": 0}
        self._navbar.size_hint_x = 1
        self.add_widget(self._navbar)

        # ── Page container ───────────────────────────────────────
        self._pages    = {}
        self._current  = ""
        self._container = BoxLayout(orientation="vertical")
        self._container.size_hint = (1, None)
        self._container.pos_hint  = {"x": 0}
        self.add_widget(self._container)

        # Build & bind container size
        self.bind(size=self._update_container, pos=self._update_container)

        # ── Register pages ───────────────────────────────────────
        self._register_pages()
        self._navigate("home")

    def _update_container(self, *_):
        top = self.top - TopBar.HEIGHT
        bot = BottomNavBar.HEIGHT
        self._container.y      = bot
        self._container.height = self.height - TopBar.HEIGHT - BottomNavBar.HEIGHT
        self._container.width  = self.width

    def _register_pages(self):
        pages = {
            "home":       HomeScreen(navigate_cb=self._navigate),
            "downloader": DownloaderScreen(navigate_cb=self._navigate,
                                            root_widget=self),
            "manager":    ManagerScreen(navigate_cb=self._navigate,
                                         root_widget=self),
            "history":    HistoryScreen(navigate_cb=self._navigate,
                                         root_widget=self),
            "settings":   SettingsScreen(navigate_cb=self._navigate,
                                          root_widget=self),
            "about":      AboutScreen(navigate_cb=self._navigate,
                                       root_widget=self),
        }
        self._pages = pages

    PAGE_TITLES = {
        "home":       "Dashboard",
        "downloader": "Downloader",
        "manager":    "DL Manager",
        "history":    "History",
        "settings":   "Settings",
        "about":      "About",
    }

    def _navigate(self, page_key: str):
        if page_key not in self._pages:
            return
        if page_key == self._current:
            return

        self._container.clear_widgets()
        self._container.add_widget(self._pages[page_key])
        self._current = page_key

        self._navbar.set_active(page_key)
        self._topbar.set_title(self.PAGE_TITLES.get(page_key, page_key.title()))

    def go_to_downloader(self, url: str = ""):
        self._navigate("downloader")
        if url:
            page = self._pages.get("downloader")
            if page and hasattr(page, "set_url"):
                page.set_url(url)


# ─── Kivy App ─────────────────────────────────────────────────────────────────

class ShanuFxApp(App):
    """Main Kivy App class."""

    title = APP_NAME

    def build(self):
        # Dark window background
        Window.clearcolor = C["bg_primary"]

        # Android status bar color (if on device)
        try:
            from android.runnable import run_on_ui_thread  # noqa
            from jnius import autoclass                     # noqa
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            window   = activity.getWindow()
            window.setStatusBarColor(0xFF0B0B18)
        except Exception:
            pass

        self._root = RootLayout()
        return self._root

    def on_start(self):
        """Called once app has started — check for first run."""
        if config.get("first_run", True):
            from core.setup import setup_manager
            setup_manager.on_complete(lambda: config.set("first_run", False))
            setup_manager.run_setup()

    def on_pause(self):
        """Android back-button / pause — return True to keep running."""
        return True

    def on_resume(self):
        """Resumed from background."""
        pass


if __name__ == "__main__":
    ShanuFxApp().run()
