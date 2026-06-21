# FINAL DEMO GUIDE: ShieldNet Pipeline B (Steganography Detection)

This guide provides instructions to run the ShieldNet platform and demonstrate the newly fixed Pipeline B (RandomForest-based Steganography Detection).

## 1. Startup Instructions

First, ensure you are using `scikit-learn==1.3.2` and have installed all requirements.
1. Make sure no old servers are running (`kill -9 $(lsof -t -i:8009)`)
2. Start the FastAPI backend:
   ```bash
   uvicorn backend.main:app --port 8009 --reload
   ```
3. Open `dashboard.html` in your web browser.

## 2. Demo Workflow

1. In the Dashboard, navigate to the **Image Steg** tab (Panel 4).
2. You will find the "Image Steganography Analyzer" widget.
3. Click "browse" or drag-and-drop a clean image from `demo_images_real/clean_0.png`.
4. Click **ANALYZE IMAGE**.
5. Repeat with a steganographic image `demo_images_real/steg_0.png`.

## 3. Test Images Used

We generated realistic gradient images containing our payloads. The images are located in the `demo_images_real` directory:
- `demo_images_real/clean_0.png` through `clean_9.png`: No hidden data.
- `demo_images_real/steg_0.png` through `steg_9.png`: Contains hidden text payload using LSB embedding.

*Payload Examples:* "PROJECT PHASE 2 COMPLETE", "SHIELDNET TEST MESSAGE", "RVCE CYBERSECURITY PROJECT"

## 4. Expected Outputs

**For Clean Images:**
- Final Confidence: ~10% to 40% (CLEAN)
- RF Score: ~0.0
- Verdict Badge: ✓ CLEAN (Green)
- Hidden Payload: "Not Detected"

**For Steg Images:**
- Final Confidence: ~90% to 99% (DETECTED)
- RF Score: ~0.90+
- Verdict Badge: 🚨 DETECTED (Red)
- Hidden Payload: 🔓 Payload: [The actual embedded message, e.g., "PROJECT PHASE 2 COMPLETE"]

*Both scenarios should log incidents to the backend Database and trigger WebSocket alerts automatically, appending to the "Image Steg Detection Feed" and the Global "Live Unified Event Feed".*

## 5. Troubleshooting Section

- **Issue:** Model throws an incompatible scikit-learn error.
  **Fix:** Ensure you have scikit-learn 1.3.2 installed via `pip install scikit-learn==1.3.2`. We re-trained the model to fix incompatibilities, but maintaining standard versions across environments prevents random breakages.

- **Issue:** Extraction returns random characters or nothing.
  **Fix:** The LSB extractor assumes simple bit replacement using a null terminator. Using LSB on compressed JPGs destroys data. We use PNGs (`demo_images_real/*.png`). Only use lossless image formats for LSB extraction demos.

- **Issue:** Backend not reachable from Dashboard.
  **Fix:** Check that the backend server is running on `127.0.0.1:8009`. If port is different, ensure the `API` constant inside `dashboard.html` matches.
