from __future__ import annotations

import threading
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from camera_handler import CameraHandler
from detection_filter import CURATED_CLASSES, filter_detections
from inference_handler import InferenceHandler
from speech_handler import SpeechHandler
from summary_generator import generate_summary


class AirisRoot(BoxLayout):
    def __init__(self, app_ref: "AirisApp", **kwargs):
        super().__init__(orientation="vertical", spacing=16, padding=20, **kwargs)
        self.app_ref = app_ref
        with self.canvas.before:
            Color(0.12, 0.11, 0.22, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.status = Label(
            text="Opening A.I.ris...",
            halign="center",
            valign="middle",
            font_size="20sp",
            color=(1, 1, 1, 1),
        )
        self.status.bind(size=lambda instance, _v: setattr(instance, "text_size", instance.size))
        self.add_widget(self.status)

        self.scan_btn = Button(
            text="Scan",
            size_hint=(1, 0.28),
            font_size="34sp",
            bold=True,
            background_normal="",
            background_color=(0.28, 0.2, 0.55, 1),
            color=(1, 1, 1, 1),
        )
        self.scan_btn.bind(on_press=lambda *_: self.app_ref.trigger_scan())
        self.add_widget(self.scan_btn)

    def _update_bg(self, *_):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class AirisApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.base_dir = Path(__file__).resolve().parent
        self.model_path = self.base_dir / "models" / "yolov8n.tflite"

        self.scanning = False
        self.model_ready = False

        self.camera_handler = CameraHandler()
        self.inference_handler = InferenceHandler(self.model_path)
        self.speech_handler = SpeechHandler()

    def build(self):
        Window.size = (380, 760)
        self.root_widget = AirisRoot(self)
        self._set_status("Opening A.I.ris...")
        Clock.schedule_once(lambda *_: self._initialize(), 0.1)
        return self.root_widget

    def _initialize(self):
        self.camera_handler.ensure_permissions()
        self.speech_handler.ensure_permissions()

        def load_model():
            self._set_status("Loading vision model. Please wait.")
            try:
                self.inference_handler.load()
                self.model_ready = True
                self._set_status("A.I.ris ready. Tap Scan.")
                self.speech_handler.speak("A.I.ris ready. Tap scan.")
            except Exception as exc:
                self._set_status(f"Model load failed: {exc}")

        threading.Thread(target=load_model, daemon=True).start()

    def _set_status(self, text: str):
        Clock.schedule_once(lambda *_: setattr(self.root_widget.status, "text", text), 0)

    def trigger_scan(self):
        if not self.model_ready:
            self._set_status("Model not ready yet.")
            return
        if self.scanning:
            return
        self.scanning = True
        threading.Thread(target=self._scan_once, daemon=True).start()

    def _scan_once(self):
        self._set_status("Scanning...")
        frame = self.camera_handler.capture_single_frame()
        if frame is None:
            text = "I could not access the camera right now."
            self._set_status(text)
            self.speech_handler.speak(text)
            self._schedule_idle_reset()
            return

        detections = self.inference_handler.run(frame)
        curated = filter_detections(detections, CURATED_CLASSES, min_confidence=0.4)
        summary = generate_summary(curated, frame_width=frame.shape[1])

        self._set_status(summary)
        self.speech_handler.speak(summary)
        self._schedule_idle_reset()

    def _schedule_idle_reset(self):
        def reset(*_):
            self.scanning = False
            self._set_status("Ready. Tap Scan.")

        Clock.schedule_once(reset, 6.0)


if __name__ == "__main__":
    AirisApp().run()
