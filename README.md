# airis
diff --git a/README.md b/README.md
index ed53d8b132827c9f83c5ff9236758a87fa8034b2..984f17c156fe316925686bfdb4bcf2f47b433bd6 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,12 @@
-# airis
\ No newline at end of file
+# airis
+
+Android-compatible Kivy + Buildozer prototype for A.I.ris with single-frame scan flow.
+
+## Build
+
+1. Place TensorFlow Lite model at `models/yolov8n.tflite`.
+2. Install Buildozer and Android prerequisites.
+3. Run:
+   ```bash
+   buildozer android debug
+   ```
