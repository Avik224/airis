from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Detection:
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float


COCO_NAMES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    15: "cat",
    16: "dog",
    56: "chair",
    13: "bench",
}


class InferenceHandler:
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.interpreter = None
        self.input_details = None
        self.output_details = None

    def load(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"Missing model file at {self.model_path}")

        try:
            from tflite_runtime.interpreter import Interpreter
        except Exception:
            from tensorflow.lite.python.interpreter import Interpreter

        self.interpreter = Interpreter(model_path=str(self.model_path))
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def run(self, frame: np.ndarray):
        inp = self._prepare_input(frame)
        self.interpreter.set_tensor(self.input_details[0]["index"], inp)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]["index"])
        return self._decode_yolov8_output(output, frame.shape[1], frame.shape[0])

    def _prepare_input(self, frame: np.ndarray):
        _, h, w, _ = self.input_details[0]["shape"]
        resized = self._resize_nn(frame, w, h).astype(np.float32) / 255.0
        return np.expand_dims(resized, axis=0)

    def _resize_nn(self, image: np.ndarray, new_w: int, new_h: int):
        y_idx = (np.linspace(0, image.shape[0] - 1, new_h)).astype(int)
        x_idx = (np.linspace(0, image.shape[1] - 1, new_w)).astype(int)
        return image[y_idx][:, x_idx]

    def _decode_yolov8_output(self, output: np.ndarray, frame_w: int, frame_h: int):
        arr = np.squeeze(output)
        if arr.ndim != 2:
            return []
        if arr.shape[0] < arr.shape[1]:
            arr = arr.T

        detections = []
        for row in arr:
            if row.size < 6:
                continue
            x, y, w, h = row[:4]
            class_scores = row[4:]
            cls_id = int(np.argmax(class_scores))
            conf = float(class_scores[cls_id])
            name = COCO_NAMES.get(cls_id, str(cls_id))

            x1 = max(0.0, (x - w / 2.0) * frame_w)
            y1 = max(0.0, (y - h / 2.0) * frame_h)
            x2 = min(float(frame_w), (x + w / 2.0) * frame_w)
            y2 = min(float(frame_h), (y + h / 2.0) * frame_h)

            detections.append(Detection(name, conf, x1, y1, x2, y2))

        return detections
