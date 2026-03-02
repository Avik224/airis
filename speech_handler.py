from __future__ import annotations

import threading


class SpeechHandler:
    def __init__(self):
        self.lock = threading.Lock()

    def ensure_permissions(self):
        try:
            from android.permissions import Permission, request_permissions

            request_permissions([
                Permission.RECORD_AUDIO,
                Permission.MODIFY_AUDIO_SETTINGS,
            ])
        except Exception:
            pass

    def speak(self, text: str):
        def worker():
            with self.lock:
                try:
                    from plyer import tts

                    tts.speak(text)
                except Exception:
                    pass

        threading.Thread(target=worker, daemon=True).start()
