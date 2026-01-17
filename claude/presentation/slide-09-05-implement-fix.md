```diff
--- a/package.json
+++ b/package.json
@@ -44,6 +44,7 @@
   "dependencies": {
+    "chart.js": "^4.4.1",

--- a/tabs/mission_control.js
+++ b/tabs/mission_control.js
+import { Chart, registerables } from 'chart.js';
+Chart.register(...registerables);

 plotElevation() {
-    /*
     const elevationDiv = $('.elevation');
```
