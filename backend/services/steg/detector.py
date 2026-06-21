# backend/services/steg/detector.py

from io import BytesIO
from PIL import Image
import numpy as np

from backend.services.steg.rf_classifier import predict_rf
from backend.services.steg.algorithms import analyze_image
from backend.services.steg.extractor import extractor


class StegDetector:

    def __init__(self):
        pass

    def analyze(self, image_bytes: bytes):

        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(image)

        # RF Prediction
        rf_score = predict_rf(img_np)

        # Statistical analysis using all 7 statistical algorithms
        stats = analyze_image(img_np)
        statistical_score = stats["confidence"]

        # Compute final confidence
        final_confidence = max(rf_score, statistical_score)

        # Debugging logs
        print("RF SCORE =", rf_score)
        print("STAT SCORE =", statistical_score)
        print("FINAL SCORE =", final_confidence)

        # Verdict logic
        if final_confidence >= 0.85:
            verdict = "DETECTED"
        elif final_confidence >= 0.50:
            verdict = "SUSPICIOUS"
        else:
            verdict = "CLEAN"

        return {
            "rf_score": round(rf_score, 4),
            "cnn_score": round(rf_score, 4), # Alias to preserve dashboard and event/forensics mapping
            "chi_square_score": round(stats.get("chi_square", 0.0), 4),
            "rs_score": round(stats.get("rs_analysis", 0.0), 4),
            "histogram_score": round(stats.get("pixel_histogram", 0.0), 4),
            "statistical_score": round(statistical_score, 4),
            "final_confidence": round(final_confidence, 4),
            "verdict": verdict,
            "hidden_message": extractor.extract(image_bytes)
        }


detector = StegDetector()