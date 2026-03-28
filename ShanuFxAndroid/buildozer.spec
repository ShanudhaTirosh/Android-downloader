[app]

# ── App identity ───────────────────────────────────────────────────────────────
title           = Shanu Fx Downloader
package.name    = shanufxdownloader
package.domain  = com.shanudha

# ── Source ─────────────────────────────────────────────────────────────────────
source.dir      = .
source.include_exts = py,png,jpg,kv,atlas,ico,json

# ── Version ────────────────────────────────────────────────────────────────────
version         = 1.0.0

# ── Entry point ────────────────────────────────────────────────────────────────
entrypoint      = main.py

# ── Python requirements ────────────────────────────────────────────────────────
# These are installed inside the APK via pip during build
requirements    = python3,\
                  kivy==2.3.0,\
                  kivymd,\
                  yt-dlp,\
                  requests,\
                  pillow,\
                  certifi

# ── Icons & Splash ─────────────────────────────────────────────────────────────
icon.filename           = %(source.dir)s/assets/icon_512.png
presplash.filename      = %(source.dir)s/assets/presplash.png
presplash.lottie_presplash = False

# ── Orientation ────────────────────────────────────────────────────────────────
orientation     = portrait

# ── Android permissions ────────────────────────────────────────────────────────
android.permissions = \
    INTERNET,\
    WRITE_EXTERNAL_STORAGE,\
    READ_EXTERNAL_STORAGE,\
    MANAGE_EXTERNAL_STORAGE,\
    READ_MEDIA_VIDEO,\
    READ_MEDIA_AUDIO,\
    READ_MEDIA_IMAGES,\
    WAKE_LOCK,\
    FOREGROUND_SERVICE,\
    ACCESS_NETWORK_STATE

# ── Android SDK / NDK ──────────────────────────────────────────────────────────
android.api                 = 33
android.minapi              = 24
android.ndk                 = 25b
android.sdk                 = 33
android.ndk_api             = 24

# ── Architecture (arm64-v8a for modern phones, armeabi-v7a for older) ──────────
android.archs               = arm64-v8a, armeabi-v7a

# ── Build tools ────────────────────────────────────────────────────────────────
android.build_tools_version = 33.0.0
android.gradle_dependencies = ''

# ── App features ───────────────────────────────────────────────────────────────
android.add_activities      = ''
android.allow_backup        = True
android.release_artifact    = apk

# ── Allow cleartext (HTTP) traffic — needed for some download URLs ─────────────
android.uses_cleartext_traffic = True

# ── FFmpeg: include pre-built arm64 binary in assets ──────────────────────────
# The setup.py will download the correct Android FFmpeg on first launch.
# Alternatively, bundle it here:
# android.add_jars = libs/ffmpeg-android.jar
# android.add_src  = src

# ── Meta-data ──────────────────────────────────────────────────────────────────
android.meta_data           = ''
android.library_references  = ''

# ── Buildozer & Python-for-Android settings ───────────────────────────────────
[buildozer]
log_level   = 2
warn_on_root = 1

# Path for SDK/NDK (GitHub Actions sets these automatically)
# android.sdk_path  = /path/to/sdk
# android.ndk_path  = /path/to/ndk

# ── p4a (python-for-android) settings ─────────────────────────────────────────
p4a.branch      = master
p4a.bootstrap   = sdl2

# Include all source folders as data
android.include_exts = py,png,jpg,jpeg,ico,json,txt
