"""Image downscaling and encoding.

Screenshots are shrunk before they're sent because full-resolution captures
cost far more tokens without making text meaningfully easier for a model to read.
"""

from __future__ import annotations

import io

from PIL import Image

# Claude downsamples anything larger than ~1568px on the long edge anyway.
DEFAULT_MAX_DIMENSION = 1568
MIN_MAX_DIMENSION = 256
MAX_MAX_DIMENSION = 4096

SUPPORTED_FORMATS = ("jpeg", "png")
JPEG_QUALITY = 85


def downscale(image: Image.Image, max_dimension: int) -> Image.Image:
    """Shrink so the longest edge is at most max_dimension, preserving aspect ratio."""
    if not MIN_MAX_DIMENSION <= max_dimension <= MAX_MAX_DIMENSION:
        raise ValueError(
            f"max_dimension must be between {MIN_MAX_DIMENSION} and {MAX_MAX_DIMENSION}, got {max_dimension}."
        )
    longest = max(image.size)
    if longest <= max_dimension:
        return image
    scale = max_dimension / longest
    new_size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def encode(image: Image.Image, image_format: str) -> bytes:
    """Encode to bytes. JPEG is much smaller; PNG keeps fine text perfectly crisp."""
    fmt = normalize_format(image_format)
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format {image_format!r}. Use one of: {', '.join(SUPPORTED_FORMATS)}.")

    buffer = io.BytesIO()
    if fmt == "jpeg":
        image.convert("RGB").save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    else:
        image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def normalize_format(image_format: str) -> str:
    fmt = image_format.strip().lower()
    return "jpeg" if fmt == "jpg" else fmt
