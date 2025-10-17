# kaihelper/utils/image_normalizer.py
from io import BytesIO
from PIL import Image

def to_jpeg_bytes(raw: bytes) -> bytes:
    """
    Open arbitrary image bytes (JPEG/PNG/WEBP/GIF/HEIC if pillow-heif registered),
    convert to RGB, and re-encode as clean JPEG bytes.
    """
    with Image.open(BytesIO(raw)) as img:
        img = img.convert("RGB")
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=90, optimize=True)
        return buf.getvalue()
