import joblib
import numpy as np
import pandas as pd
from math import log2
from PIL import Image
from pathlib import Path

# Robust multi-path Model Loading
try:
    # Try exact path requested: models/steg_model.pkl
    model = joblib.load("models/steg_model.pkl")
except Exception:
    try:
        # Try path relative to this script: backend/services/steg/rf_classifier.py -> models/steg_model.pkl
        resolved_path = Path(__file__).resolve().parents[3] / "models" / "steg_model.pkl"
        model = joblib.load(resolved_path)
    except Exception:
        # Try path inside steg_module workspace folder
        model = joblib.load("D:/4th EL/Main EL/steg_module/steg_model.pkl")


def calculate_entropy(pixels):
    histogram = np.bincount(pixels, minlength=256)
    total = len(pixels)
    entropy = 0
    for count in histogram:
        if count > 0:
            probability = count / total
            entropy -= probability * log2(probability)
    return entropy


def calculate_lsb_ratio(pixels):
    ones = 0
    for pixel in pixels:
        ones += int(pixel) & 1
    return ones / len(pixels)


def histogram_variance(pixels):
    histogram = np.bincount(pixels, minlength=256)
    return np.var(histogram)


def edge_density(pixels_2d):
    edges = 0
    rows, cols = pixels_2d.shape
    for i in range(rows - 1):
        for j in range(cols - 1):
            diff = abs(
                int(pixels_2d[i][j]) -
                int(pixels_2d[i][j+1])
            )
            if diff > 20:
                edges += 1
    total = rows * cols
    return edges / total


def predict_rf(img_array: np.ndarray) -> float:
    # Convert numpy image array to grayscale (L)
    img = Image.fromarray(img_array.astype(np.uint8)).convert("L")
    pixels_2d = np.array(img)
    pixels = pixels_2d.flatten()

    features = pd.DataFrame([{
        "entropy": calculate_entropy(pixels),
        "lsb_ratio": calculate_lsb_ratio(pixels),
        "hist_variance": histogram_variance(pixels),
        "mean": np.mean(pixels),
        "std_dev": np.std(pixels),
        "edge_density": edge_density(pixels_2d)
    }])

    prob = model.predict_proba(features)[0]
    return float(prob[1])