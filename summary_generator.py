 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/summary_generator.py b/summary_generator.py
new file mode 100644
index 0000000000000000000000000000000000000000..13998281b21aa76640cb8f5e06c2ddc7cbaf3ec3
--- /dev/null
+++ b/summary_generator.py
@@ -0,0 +1,78 @@
+from __future__ import annotations
+
+
+def _distance_bucket(height: float) -> str:
+    if height > 300:
+        return "very close"
+    if height > 220:
+        return "around two meters"
+    if height > 140:
+        return "around four meters"
+    return "around six meters"
+
+
+def _direction_bucket(center_x: float, frame_width: float) -> str:
+    ratio = center_x / max(frame_width, 1)
+    if ratio < 0.40:
+        return "left"
+    if ratio > 0.60:
+        return "right"
+    return "center"
+
+
+def generate_summary(detections, frame_width: float) -> str:
+    grouped = {}
+    for d in detections:
+        grouped.setdefault(d.class_name, []).append(d)
+
+    parts = []
+
+    people = grouped.get("person", [])
+    if people:
+        directions = {"left": 0, "center": 0, "right": 0}
+        distances = {"very close": 0, "around two meters": 0, "around four meters": 0, "around six meters": 0}
+
+        for p in people:
+            h = p.y2 - p.y1
+            cx = (p.x1 + p.x2) / 2
+            directions[_direction_bucket(cx, frame_width)] += 1
+            distances[_distance_bucket(h)] += 1
+
+        dom_dir = max(directions, key=directions.get)
+        dom_dist = max(distances, key=distances.get)
+        count = len(people)
+
+        people_phrase = "a group of people" if count > 5 else f"{count} people"
+        if count == 1:
+            people_phrase = "one person"
+
+        if dom_dir == "center":
+            parts.append(f"There are {people_phrase} ahead of you, {dom_dist}")
+        else:
+            parts.append(f"There are {people_phrase} towards your {dom_dir}, {dom_dist}")
+
+    other_order = [
+        "car",
+        "bus",
+        "truck",
+        "motorcycle",
+        "bicycle",
+        "dog",
+        "cat",
+        "chair",
+        "stairs",
+        "bench",
+        "door",
+    ]
+    other_bits = []
+    for cls in other_order:
+        if cls in grouped:
+            c = len(grouped[cls])
+            other_bits.append(f"{c} {cls}" + ("s" if c > 1 else ""))
+
+    if other_bits:
+        parts.append("Detected " + ", ".join(other_bits[:4]))
+
+    if not parts:
+        return "No important objects detected in this scan."
+    return ". ".join(parts) + "."
 
EOF
)
