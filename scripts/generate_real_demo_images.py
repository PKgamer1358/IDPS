import numpy as np
from PIL import Image
import os

messages = [
    "PROJECT PHASE 2 COMPLETE",
    "SHIELDNET TEST MESSAGE",
    "RVCE CYBERSECURITY PROJECT",
    "TOP SECRET PAYLOAD",
    "CONFIDENTIAL DATA",
    "DO NOT DISCLOSE",
    "HIDDEN INFORMATION",
    "STEGANOGRAPHY DETECTED",
    "MALICIOUS CODE EMBEDDED",
    "SYSTEM COMPROMISED"
]

os.makedirs("demo_images_real", exist_ok=True)

# Create a smooth gradient image
width, height = 256, 256
gradient = np.zeros((height, width, 3), dtype=np.uint8)
for i in range(height):
    for j in range(width):
        gradient[i, j, 0] = i % 256
        gradient[i, j, 1] = j % 256
        gradient[i, j, 2] = (i + j) % 256

for i in range(10):
    # Generate clean image
    arr_clean = gradient.copy()
    Image.fromarray(arr_clean).save(f"demo_images_real/clean_{i}.png")

    # Generate steg image
    arr_steg = arr_clean.copy()
    payload = messages[i]
    bits = "".join(f"{b:08b}" for b in (payload.encode() + b"\x00"))
    flat = arr_steg.flatten()
    for j, bit in enumerate(bits[:len(flat)]):
        flat[j] = (flat[j] & 0xFE) | int(bit)
    Image.fromarray(flat.reshape(arr_steg.shape)).save(f"demo_images_real/steg_{i}.png")

print("Generated 10 clean and 10 steg images in demo_images_real/")
