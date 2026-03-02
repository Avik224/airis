from __future__ import annotations

import threading

import numpy as np
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.camera import Camera


class CameraHandler:
    def __init__(self):
        self.camera = Camera(play=True, resolution=(640, 480), index=0)

    def ensure_permissions(self):
        try:
            from android.permissions import Permission, request_permissions

            request_permissions([Permission.CAMERA])
        except Exception:
            pass

    def capture_single_frame(self):
        done = threading.Event()
        holder = {"frame": None}

        def grab(*_):
            texture: Texture | None = self.camera.texture
            if texture is not None:
                size = texture.size
                pixels = texture.pixels
                rgba = np.frombuffer(pixels, dtype=np.uint8).reshape(size[1], size[0], 4)
                holder["frame"] = rgba[:, :, :3].copy()
            done.set()

        Clock.schedule_once(grab, 0)
        done.wait(timeout=1.5)
        return holder["frame"]
