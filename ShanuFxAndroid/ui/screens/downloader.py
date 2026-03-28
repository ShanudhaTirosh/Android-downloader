"""
Shanu Fx Android - Downloader Screen
Social media download UI for Android: fetch info, pick format, download.
Author: Shanudha Tirosh
"""

import os
from typing import Optional

from kivy.uix.boxlayout   import BoxLayout
from kivy.uix.scrollview  import ScrollView
from kivy.uix.label       import Label
from kivy.uix.image       import AsyncImage
from kivy.uix.spinner     import Spinner
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics         import Color, RoundedRectangle
from kivy.metrics          import dp, sp
from kivy.clock            import Clock

from ui.theme   import C, SP, DP
from ui.widgets.shared import (Card, SectionTitle, BodyLabel, AccentButton,
                                SecondaryButton, DarkInput,
                                AccentProgressBar, Divider, show_toast)
from downloader.ytdlp_backend import ytdlp_backend, VideoInfo, DownloadProgress
from downloader.history       import history_manager, HistoryEntry
from core.config              import config, VIDEO_QUALITIES, AUDIO_BITRATES


# ─── Spinner (dropdown) styling helper ───────────────────────────────────────

def make_spinner(values, default):
    sp_widget = Spinner(
        text=default, values=values,
        size_hint_y=None, height=dp(46),
        font_size=sp(SP["sm"]),
        color=C["text_primary"],
        background_normal="",
        background_color=C["bg_elevated"],
        option_cls="SpinnerOption",
    )
    return sp_widget


# ─── Info Panel ──────────────────────────────────────────────────────────────

class InfoPanel(Card):
    """Shows fetched video metadata + thumbnail."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build()

    def _build(self):
        self.add_widget(SectionTitle("Video Info"))
        self.add_widget(Divider())

        # Thumbnail
        self._thumb = AsyncImage(
            source="",
            size_hint_y=None, height=dp(180),
            allow_stretch=True, keep_ratio=True,
        )
        self.add_widget(self._thumb)

        # Fields
        self._fields = {}
        for key, label in [("title","Title"),("uploader","Channel"),
                            ("platform","Platform"),("duration","Duration")]:
            row = BoxLayout(orientation="horizontal",
                             size_hint_y=None, height=dp(28), spacing=dp(8))
            row.add_widget(Label(text=f"{label}:", font_size=sp(SP["caption"]),
                                  color=C["text_secondary"],
                                  size_hint=(None,1), width=dp(72),
                                  halign="right", valign="middle"))
            val = Label(text="—", font_size=sp(SP["caption"]),
                         color=C["text_primary"],
                         halign="left", valign="middle")
            val.bind(size=lambda w,v: setattr(w,'text_size',v))
            row.add_widget(val)
            self._fields[key] = val
            self.add_widget(row)

    def update(self, info: VideoInfo):
        self._thumb.source = info.thumbnail or ""
        self._fields["title"].text    = info.title[:48] + ("…" if len(info.title)>48 else "")
        self._fields["uploader"].text = info.uploader[:30]
        self._fields["platform"].text = info.platform_name
        self._fields["duration"].text = info.duration_str

    def reset(self):
        self._thumb.source = ""
        for lbl in self._fields.values():
            lbl.text = "—"


# ─── Downloader Screen ───────────────────────────────────────────────────────

class DownloaderScreen(BoxLayout):
    """Social media downloader screen."""

    def __init__(self, navigate_cb, root_widget, **kwargs):
        kwargs.setdefault("orientation", "vertical")
        super().__init__(**kwargs)
        self._navigate    = navigate_cb
        self._root        = root_widget
        self._info: Optional[VideoInfo] = None
        self._fetching    = False
        self._downloading = False
        self._build()

    def _build(self):
        scroll = ScrollView(do_scroll_x=False)
        inner  = BoxLayout(orientation="vertical",
                            size_hint_y=None, spacing=dp(14),
                            padding=[dp(16), dp(12), dp(16), dp(24)])
        inner.bind(minimum_height=inner.setter("height"))
        scroll.add_widget(inner)
        self.add_widget(scroll)

        # ── Header ──────────────────────────────────────────────
        inner.add_widget(Label(
            text="Media Downloader", font_size=sp(SP["xl"]),
            bold=True, color=C["text_primary"],
            halign="left", valign="middle",
            size_hint_y=None, height=dp(40),
        ))
        inner.add_widget(BodyLabel(
            "YouTube · TikTok · Instagram · Facebook + 1000 sites",
            color=C["text_secondary"],
        ))

        # ── URL Input Card ───────────────────────────────────────
        url_card = Card()
        inner.add_widget(url_card)

        url_card.add_widget(SectionTitle("Paste URL"))

        self._url_input = DarkInput(
            hint_text="https://youtube.com/watch?v=…",
        )
        url_card.add_widget(self._url_input)

        btn_row = BoxLayout(orientation="horizontal",
                             size_hint_y=None, height=dp(48), spacing=dp(8))
        paste_btn = SecondaryButton(text="📋 Paste",
                                     size_hint_x=0.35, height=dp(48))
        paste_btn.bind(on_release=self._paste_url)

        self._fetch_btn = AccentButton(text="🔍 Fetch Info",
                                        size_hint_x=0.65, height=dp(48))
        self._fetch_btn.bind(on_release=self._fetch_info)

        btn_row.add_widget(paste_btn)
        btn_row.add_widget(self._fetch_btn)
        url_card.add_widget(btn_row)

        # ── Info Panel ───────────────────────────────────────────
        self._info_panel = InfoPanel()
        inner.add_widget(self._info_panel)

        # ── Options Card ─────────────────────────────────────────
        opts_card = Card()
        inner.add_widget(opts_card)
        opts_card.add_widget(SectionTitle("Download Options"))

        opts_card.add_widget(BodyLabel("Format", color=C["text_secondary"]))
        self._fmt_spinner = make_spinner(
            ["MP4 (Video)", "MP3 (Audio)", "WEBM (Video)", "M4A (Audio)"],
            config.get("default_format","mp4").upper() + " (Video)",
        )
        opts_card.add_widget(self._fmt_spinner)

        opts_card.add_widget(BodyLabel("Quality", color=C["text_secondary"]))
        self._qual_spinner = make_spinner(
            [q.title() for q in VIDEO_QUALITIES],
            config.get("default_quality","best").title(),
        )
        opts_card.add_widget(self._qual_spinner)

        opts_card.add_widget(BodyLabel("Audio Bitrate", color=C["text_secondary"]))
        self._br_spinner = make_spinner(
            AUDIO_BITRATES,
            config.get("default_bitrate","192kbps"),
        )
        opts_card.add_widget(self._br_spinner)

        # ── Progress Card ────────────────────────────────────────
        prog_card = Card()
        inner.add_widget(prog_card)

        self._status_lbl = BodyLabel("Ready", color=C["text_secondary"])
        prog_card.add_widget(self._status_lbl)

        self._pb = AccentProgressBar()
        prog_card.add_widget(self._pb)

        speed_row = BoxLayout(orientation="horizontal",
                               size_hint_y=None, height=dp(24))
        self._pct_lbl   = Label(text="0%", font_size=sp(SP["sm"]),
                                  bold=True, color=C["accent"],
                                  size_hint_x=0.3, halign="left")
        self._speed_lbl = Label(text="", font_size=sp(SP["caption"]),
                                  color=C["text_secondary"],
                                  size_hint_x=0.4, halign="center")
        self._eta_lbl   = Label(text="", font_size=sp(SP["caption"]),
                                  color=C["text_muted"],
                                  size_hint_x=0.3, halign="right")
        speed_row.add_widget(self._pct_lbl)
        speed_row.add_widget(self._speed_lbl)
        speed_row.add_widget(self._eta_lbl)
        prog_card.add_widget(speed_row)

        # ── Download Button ──────────────────────────────────────
        self._dl_btn = AccentButton(text="⬇  Start Download")
        self._dl_btn.bind(on_release=self._start_download)
        inner.add_widget(self._dl_btn)

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _paste_url(self, *_):
        try:
            from kivy.core.clipboard import Clipboard
            text = Clipboard.paste()
            if text:
                self._url_input.text = text.strip()
        except Exception:
            pass

    def set_url(self, url: str):
        self._url_input.text = url
        self._fetch_info()

    def _fetch_info(self, *_):
        url = self._url_input.text.strip()
        if not url:
            show_toast(self._root, "Please enter a URL")
            return
        if self._fetching:
            return
        self._fetching = True
        self._fetch_btn.text = "Fetching…"
        self._info_panel.reset()

        def on_success(info):
            Clock.schedule_once(lambda dt: self._show_info(info))

        def on_error(err):
            Clock.schedule_once(lambda dt: self._on_fetch_error(err))

        ytdlp_backend.fetch_info(url, on_success=on_success, on_error=on_error)

    def _show_info(self, info: VideoInfo):
        self._info = info
        self._fetching = False
        self._fetch_btn.text = "🔍 Fetch Info"
        self._info_panel.update(info)
        show_toast(self._root, f"Fetched: {info.title[:30]}")

    def _on_fetch_error(self, err: str):
        self._fetching = False
        self._fetch_btn.text = "🔍 Fetch Info"
        show_toast(self._root, f"Error: {err[:50]}")

    def _start_download(self, *_):
        url = self._url_input.text.strip()
        if not url:
            show_toast(self._root, "Please enter a URL")
            return
        if self._downloading:
            show_toast(self._root, "Download already in progress")
            return

        fmt   = self._fmt_spinner.text.lower()
        is_audio = "mp3" in fmt or "audio" in fmt or "m4a" in fmt
        fmt_type  = "audio" if is_audio else "video"
        quality   = self._qual_spinner.text.lower()
        bitrate   = self._br_spinner.text
        out_dir   = config.get("download_dir", "/sdcard/ShanuFx")

        self._downloading = True
        self._dl_btn.text = "Downloading…"
        import time; _t0 = time.time()

        def on_progress(p: DownloadProgress):
            Clock.schedule_once(lambda dt: self._update_progress(p))

        def on_done(filepath):
            elapsed = time.time() - _t0
            Clock.schedule_once(lambda dt: self._on_done(filepath, fmt_type, elapsed))

        def on_error(err):
            Clock.schedule_once(lambda dt: self._on_error(err))

        ytdlp_backend.download(
            url=url, output_dir=out_dir,
            fmt_type=fmt_type, quality=quality, bitrate=bitrate,
            on_progress=on_progress, on_done=on_done, on_error=on_error,
        )

    def _update_progress(self, p: DownloadProgress):
        status_map = {
            "downloading": C["accent"],
            "processing":  C["accent_orange"],
            "done":        C["accent_green"],
            "error":       C["accent_red"],
        }
        color = status_map.get(p.status, C["accent"])
        self._pb.set_value(p.percent, color)
        self._pct_lbl.text   = f"{p.percent:.1f}%"
        self._speed_lbl.text = p.speed or ""
        self._eta_lbl.text   = f"ETA {p.eta}" if p.eta else ""
        texts = {
            "downloading": f"Downloading {p.percent:.0f}%",
            "processing":  "Processing with FFmpeg…",
            "done":        "✓ Complete!",
            "error":       f"✕ {p.error}",
        }
        self._status_lbl.text = texts.get(p.status, p.status)

    def _on_done(self, filepath, fmt_type, elapsed):
        self._downloading = False
        self._dl_btn.text = "⬇  Start Download"
        size = 0
        try: size = os.path.getsize(filepath)
        except: pass
        info = self._info
        entry = HistoryEntry(
            title      = info.title if info else "Download",
            url        = self._url_input.text.strip(),
            filename   = os.path.basename(filepath),
            filepath   = filepath,
            fmt_type   = fmt_type,
            size_bytes = size,
            duration   = info.duration_str if info else "",
            platform   = info.platform_name if info else "",
            status     = "done",
        )
        history_manager.add(entry)
        show_toast(self._root, f"Done in {elapsed:.1f}s  ✓")

    def _on_error(self, err):
        self._downloading = False
        self._dl_btn.text = "⬇  Start Download"
        show_toast(self._root, f"Failed: {err[:50]}")
