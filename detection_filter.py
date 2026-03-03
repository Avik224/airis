from __future__ import annotations

CURATED_CLASSES = {
    "person",
    "car",
    "bus",
    "truck",
    "motorcycle",
    "bicycle",
    "dog",
    "cat",
    "chair",
    "stairs",
    "bench",
    "door",
}


def filter_detections(detections, curated_classes, min_confidence=0.4):
    return [
        d
        for d in detections
        if d.class_name in curated_classes and float(d.confidence) >= min_confidence
    ]
