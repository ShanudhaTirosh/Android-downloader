"""
Shanu Fx Android - Android Config Overlay
Overrides desktop paths to use Android-safe storage locations.
Author: Shanudha Tirosh
"""

import os
from pathlib import Path

# ── Detect Android environment ────────────────────────────────────────────────
def _is_android() -> bool:
    try:
        import android  # noqa  — only exists inside a Buildozer APK
        return True
    except ImportError:
        pass
    return os.environ.get("ANDROID_ARGUMENT") is not None or \
           os.path.exists("/data/data")


IS_ANDROID = _is_android()

if IS_ANDROID:
    # Android external storage  (/sdcard/ShanuFx  or app-private storage)
    try:
        from android.storage import primary_external_storage_path  # noqa
        _ext = primary_external_storage_path()
    except Exception:
        _ext = "/sdcard"

    DOWNLOAD_DIR = Path(_ext) / "ShanuFx"
    DATA_DIR     = Path(_ext) / ".shanufx"
else:
    # Fall back to desktop paths when running on PC for testing
    from core.config import DOWNLOAD_DIR, DATA_DIR  # noqa

DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Re-export everything else from the shared config
from core.config import (           # noqa
    config, COLORS, FONTS,
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_GITHUB,
    VIDEO_QUALITIES, AUDIO_BITRATES,
    DEFAULT_CONFIG,
)
