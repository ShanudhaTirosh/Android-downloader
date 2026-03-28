"""
Shanu Fx Android - Download Manager Screen
Live download queue with speed graph, pause/resume, and task controls.
Author: Shanudha Tirosh
"""

from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.scrollview  import ScrollView
from kivy.uix.label       import Label
from kivy.uix.button      import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup       import Popup
from kivy.graphics         import Color, RoundedRectangle, Line, Rectangle
from kivy.metrics          import dp, sp
from kivy.clock            import Clock

from ui.theme   import C, SP, DP
from ui.widgets.shared import (Card, SectionTitle, BodyLabel, AccentButton,
                                SecondaryButton, DarkInput,
                                AccentProgressBar, StatusBadge,
                                Divider, show_toast, add_bg)
from manager.download_manager import download_manager, filename_from_url
from manager.multi_thread     import DownloadTask, DownloadStatus


# ─── Task Card ────────────────────────────────────────────────────────────────

class TaskCard(BoxLayout):
    STATUS_COLORS = {
        DownloadStatus.QUEUED:      C["status_queued"],
        DownloadStatus.CONNECTING:  C["accent_blue"],
        DownloadStatus.DOWNLOADING: C["accent"],
        DownloadStatus.PAUSED:      C["status_paused"],
        DownloadStatus.PROCESSING:  C["accent_orange"],
        DownloadStatus.DONE:        C["status_active"],
        DownloadStatus.ERROR:       C["status_error"],
        DownloadStatus.CANCELLED:   C["text_muted"],
    }

    def __init__(self, task: DownloadTask, **kwargs):
        kwargs.setdefault("orientation",  "vertical")
        kwargs.setdefault("size_hint_y",  None)
        kwargs.setdefault("spacing",      dp(6))
        kwargs.setdefault("padding",      dp(14))
        super().__init__(**kwargs)
        self.task_id = task.task_id
        self.height  = dp(130)

        with self.canvas.before:
            Color(*C["bg_card"])
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(*C["border"])
            self._bd = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
        self.bind(pos=self._upd, size=self._upd)

        # Row 1: filename + status
        row1 = BoxLayout(orientation="horizontal",
                          size_hint_y=None, height=dp(24), spacing=dp(8))
        fname = task.filename[:40] + ("…" if len(task.filename)>40 else "")
        row1.add_widget(Label(text=fname, font_size=sp(SP["sm"]),
                               color=C["text_primary"],
                               halign="left", valign="middle",
                               size_hint_x=0.75))
        self._badge = StatusBadge(task.status.value)
        row1.add_widget(self._badge)
        self.add_widget(row1)

        # Progress bar
        self._pb = AccentProgressBar()
        self.add_widget(self._pb)

        # Row 2: percentage + speed + ETA
        row2 = BoxLayout(orientation="horizontal",
                          size_hint_y=None, height=dp(20))
        self._pct_lbl   = Label(text="0%", font_size=sp(SP["caption"]),
                                  color=C["accent"], bold=True,
                                  size_hint_x=0.2, halign="left")
        self._speed_lbl = Label(text="", font_size=sp(SP["caption"]),
                                  color=C["text_secondary"],
                                  size_hint_x=0.5, halign="center")
        self._size_lbl  = Label(text=task.size_str, font_size=sp(SP["caption"]),
                                  color=C["text_muted"],
                                  size_hint_x=0.3, halign="right")
        row2.add_widget(self._pct_lbl)
        row2.add_widget(self._speed_lbl)
        row2.add_widget(self._size_lbl)
        self.add_widget(row2)

        # Row 3: control buttons
        row3 = BoxLayout(orientation="horizontal",
                          size_hint_y=None, height=dp(36), spacing=dp(8))

        btn_kw = dict(size_hint_y=None, height=dp(34),
                      font_size=sp(SP["caption"]),
                      background_normal="", background_color=(0,0,0,0))

        self._pause_btn = Button(text="⏸", color=C["accent_light"], **btn_kw)
        self._pause_btn.bind(on_release=lambda *_: self._toggle_pause())
        add_bg(self._pause_btn, C["bg_elevated"], radius=8)

        retry_btn = Button(text="↺", color=C["accent_green"], **btn_kw)
        retry_btn.bind(on_release=lambda *_: download_manager.retry(self.task_id))
        add_bg(retry_btn, C["bg_elevated"], radius=8)

        cancel_btn = Button(text="✕", color=C["accent_red"], **btn_kw)
        cancel_btn.bind(on_release=lambda *_: download_manager.cancel(self.task_id))
        add_bg(cancel_btn, C["bg_elevated"], radius=8)

        for b in (self._pause_btn, retry_btn, cancel_btn):
            b.size_hint_x = None
            b.width       = dp(42)
            row3.add_widget(b)

        row3.add_widget(Label())  # spacer
        self.add_widget(row3)

        self._paused = False

    def _upd(self, *_):
        self._bg.pos = self._bd.pos = self.pos
        self._bg.size = self._bd.size = self.size

    def _toggle_pause(self):
        if self._paused:
            download_manager.resume(self.task_id)
            self._pause_btn.text = "⏸"
            self._paused = False
        else:
            download_manager.pause(self.task_id)
            self._pause_btn.text = "▶"
            self._paused = True

    def update(self, task: DownloadTask):
        color = self.STATUS_COLORS.get(task.status, C["text_muted"])
        self._pb.set_value(task.percent, color)
        self._pct_lbl.text   = f"{task.percent:.0f}%"
        self._speed_lbl.text = task.speed_str if task.status == DownloadStatus.DOWNLOADING else ""
        self._size_lbl.text  = f"{task.done_size_str}/{task.size_str}"
        self._badge.set_status(task.status.value)


# ─── Add URL Popup ────────────────────────────────────────────────────────────

class AddURLPopup(Popup):
    def __init__(self, on_add, **kwargs):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))
        self._entry = DarkInput(hint_text="https://…")
        add_btn = AccentButton(text="⬇  Add Download", height=dp(48))

        def do_add(*_):
            url = self._entry.text.strip()
            if url:
                on_add(url)
                self.dismiss()

        add_btn.bind(on_release=do_add)
        content.add_widget(Label(text="Enter URL to download",
                                  font_size=sp(SP["md"]), bold=True,
                                  color=C["text_primary"],
                                  size_hint_y=None, height=dp(30)))
        content.add_widget(self._entry)
        content.add_widget(add_btn)

        super().__init__(
            title="Add Download",
            content=content,
            size_hint=(0.9, None),
            height=dp(220),
            background_color=C["bg_elevated"],
            title_color=C["text_primary"],
            **kwargs,
        )

        # Try clipboard
        try:
            from kivy.core.clipboard import Clipboard
            cb = Clipboard.paste()
            if cb and cb.startswith("http"):
                self._entry.text = cb.strip()
        except Exception:
            pass


# ─── Manager Screen ───────────────────────────────────────────────────────────

class ManagerScreen(BoxLayout):
    def __init__(self, navigate_cb, root_widget, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        super().__init__(**kwargs)
        self._navigate   = navigate_cb
        self._root       = root_widget
        self._task_cards = {}
        self._build()
        self._subscribe()
        Clock.schedule_interval(self._update_speed, 1)

    def _build(self):
        # Header bar
        hdr = BoxLayout(orientation="horizontal",
                         size_hint_y=None, height=dp(52),
                         padding=[dp(16), dp(8)], spacing=dp(10))
        hdr.add_widget(Label(text="DL Manager", font_size=sp(SP["lg"]),
                              bold=True, color=C["text_primary"],
                              halign="left", valign="middle"))

        add_btn = AccentButton(text="+ Add", size_hint_x=None,
                                width=dp(90), height=dp(40))
        add_btn.bind(on_release=self._show_add_popup)

        clr_btn = SecondaryButton(text="Clear ✓", size_hint_x=None,
                                   width=dp(90), height=dp(40))
        clr_btn.bind(on_release=self._clear_done)

        hdr.add_widget(add_btn)
        hdr.add_widget(clr_btn)
        self.add_widget(hdr)

        # Speed + stats strip
        stats_strip = BoxLayout(orientation="horizontal",
                                 size_hint_y=None, height=dp(36),
                                 padding=[dp(16), 0], spacing=dp(12))
        self._active_lbl = Label(text="Active: 0", font_size=sp(SP["caption"]),
                                   color=C["accent"])
        self._speed_lbl  = Label(text="⚡ 0 KB/s", font_size=sp(SP["caption"]),
                                   color=C["accent_green"])
        self._done_lbl   = Label(text="Done: 0", font_size=sp(SP["caption"]),
                                   color=C["text_muted"])
        for lbl in (self._active_lbl, self._speed_lbl, self._done_lbl):
            stats_strip.add_widget(lbl)
        self.add_widget(stats_strip)

        Divider_w = Divider()
        self.add_widget(Divider_w)

        # Task list
        self._scroll = ScrollView(do_scroll_x=False)
        self._list   = BoxLayout(orientation="vertical",
                                  size_hint_y=None, spacing=dp(8),
                                  padding=[dp(12), dp(8), dp(12), dp(16)])
        self._list.bind(minimum_height=self._list.setter("height"))
        self._scroll.add_widget(self._list)
        self.add_widget(self._scroll)

        self._empty_lbl = BodyLabel(
            "No downloads yet.  Tap  '+ Add'  to start.",
            color=C["text_muted"],
        )
        self._list.add_widget(self._empty_lbl)

    def _subscribe(self):
        download_manager.subscribe_new(
            lambda t: Clock.schedule_once(lambda dt: self._on_new(t))
        )
        download_manager.subscribe_update(
            lambda t: Clock.schedule_once(lambda dt: self._on_update(t))
        )

    def _on_new(self, task: DownloadTask):
        self._empty_lbl.text = ""
        card = TaskCard(task)
        self._task_cards[task.task_id] = card
        self._list.add_widget(card)
        self._refresh_stats()

    def _on_update(self, task: DownloadTask):
        card = self._task_cards.get(task.task_id)
        if card:
            card.update(task)
        self._refresh_stats()

    def _update_speed(self, *_):
        active = download_manager.get_active()
        combined = sum(t.speed_bps for t in active)
        if combined < 1024:
            s = f"{combined:.0f} B/s"
        elif combined < 1024**2:
            s = f"{combined/1024:.1f} KB/s"
        else:
            s = f"{combined/1024**2:.2f} MB/s"
        self._speed_lbl.text = f"⚡ {s}"

    def _refresh_stats(self):
        tasks  = download_manager.get_all()
        active = sum(1 for t in tasks if t.status == DownloadStatus.DOWNLOADING)
        done   = sum(1 for t in tasks if t.status == DownloadStatus.DONE)
        self._active_lbl.text = f"Active: {active}"
        self._done_lbl.text   = f"Done: {done}"

    def _show_add_popup(self, *_):
        def on_add(url):
            fname = filename_from_url(url)
            download_manager.add(url=url, filename=fname)
            show_toast(self._root, f"Added: {fname[:30]}")
        AddURLPopup(on_add=on_add).open()

    def _clear_done(self, *_):
        from manager.multi_thread import DownloadStatus
        for t in download_manager.get_all():
            if t.status in (DownloadStatus.DONE, DownloadStatus.CANCELLED):
                card = self._task_cards.pop(t.task_id, None)
                if card and card.parent:
                    card.parent.remove_widget(card)
                download_manager.remove(t.task_id)
