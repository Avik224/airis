[app]
title = A.I.ris
package.name = airis
package.domain = org.airis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,tflite
version = 0.1
requirements = python3,kivy,numpy,plyer,tflite-runtime
orientation = portrait
fullscreen = 0

android.permissions = CAMERA,RECORD_AUDIO,MODIFY_AUDIO_SETTINGS
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
