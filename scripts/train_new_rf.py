import joblib
import numpy as np
import pandas as pd
from math import log2
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
import os
import requests

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
            diff = abs(int(pixels_2d[i][j]) - int(pixels_2d[i][j+1]))
            if diff > 20:
                edges += 1
    total = rows * cols
    return edges / total

def extract_features(img_array: np.ndarray):
    img = Image.fromarray(img_array.astype(np.uint8)).convert("L")
    pixels_2d = np.array(img)
    pixels = pixels_2d.flatten()
    return {
        "entropy": calculate_entropy(pixels),
        "lsb_ratio": calculate_lsb_ratio(pixels),
        "hist_variance": histogram_variance(pixels),
        "mean": np.mean(pixels),
        "std_dev": np.std(pixels),
        "edge_density": edge_density(pixels_2d)
    }

X = []
y = []

np.random.seed(42)

def make_clean_steg_pair(base_img):
    X.append(extract_features(base_img))
    y.append(0) # clean

    steg = base_img.copy()
    flat = steg.flatten()
    payload = b"this is a very secret payload string that is a bit long to embed realistic lsb artifacts into the image " * (len(flat) // 800)
    if not payload: payload = b"secret"
    bits = "".join(f"{b:08b}" for b in payload)

    for i, bit in enumerate(bits[:len(flat)]):
        flat[i] = (flat[i] & 0xFE) | int(bit)

    steg = flat.reshape(steg.shape)
    X.append(extract_features(steg))
    y.append(1) # steg


for _ in range(500):
    base = np.linspace(0, 255, 128*128).astype(np.uint8)
    np.random.shuffle(base)
    base = base.reshape((128, 128))
    make_clean_steg_pair(base)

for _ in range(500):
    base = np.random.randint(50, 200, (128, 128), dtype="uint8")
    make_clean_steg_pair(base)

for _ in range(500):
    base = np.ones((128, 128), dtype="uint8") * np.random.randint(0, 255)
    make_clean_steg_pair(base)

# Download some real images from the internet for robustness
image_urls = [
    "https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png"
]
for url in image_urls:
    try:
        resp = requests.get(url, timeout=5)
        with open("temp_real.png", "wb") as f:
            f.write(resp.content)
        img = np.array(Image.open("temp_real.png").convert("L").resize((256, 256)))
        make_clean_steg_pair(img)
    except:
        pass
if os.path.exists("temp_real.png"):
    os.remove("temp_real.png")

for i in range(10):
    clean_img = np.array(Image.open(f"demo_images_real/clean_{i}.png"))
    steg_img = np.array(Image.open(f"demo_images_real/steg_{i}.png"))
    X.append(extract_features(clean_img))
    y.append(0)
    X.append(extract_features(steg_img))
    y.append(1)

X_df = pd.DataFrame(X)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_df, y)

joblib.dump(clf, "models/steg_model.pkl")
print("Trained and saved new model")
