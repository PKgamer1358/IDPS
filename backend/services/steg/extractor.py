import numpy as np
from PIL import Image
from io import BytesIO

class LSBExtractor:
    def extract(self, image_bytes: bytes) -> str:
        """
        Extracts LSB hidden message. Assumes the message is hidden in the LSB of pixels
        and is null-terminated.
        """
        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            img_np = np.array(image)
            flat = img_np.flatten()

            bits = [str(pixel & 1) for pixel in flat]

            # Group bits into bytes
            chars = []
            for i in range(0, len(bits), 8):
                byte = "".join(bits[i:i+8])
                if len(byte) == 8:
                    char_code = int(byte, 2)
                    if char_code == 0:  # Null terminator
                        break
                    # Only append printable characters (simple heuristic)
                    if 32 <= char_code <= 126:
                        chars.append(chr(char_code))
                    else:
                        break # Stop if non-printable found to avoid noise

            msg = "".join(chars)
            if len(msg) > 5: # Require at least some length to be considered a message
                return msg
            return None

        except Exception as e:
            print(f"Extraction error: {e}")
            return None

extractor = LSBExtractor()
