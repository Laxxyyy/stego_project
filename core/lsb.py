"""
LSB (Least Significant Bit) steganography — fully vectorized.

Embeds payload bits into the LSB of each RGB pixel channel in raster order.
Uses a length-prefix + flags header so no sentinel delimiter is needed.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from PIL import Image

from .utils import bytes_to_bits, bits_to_bytes, build_frame, parse_header_bits, HEADER_BITS


# ── public API ───────────────────────────────────────────────────────────────

def max_capacity(image: Image.Image) -> int:
    """Max payload bytes an image can hold (after the 5-byte header)."""
    arr = np.array(image.convert("RGB"))
    return max(0, (arr.size - HEADER_BITS) // 8)


def encode(
    image: Image.Image,
    payload: bytes,
    *,
    encrypted: bool = False,
    progress_cb: Callable[[float], None] | None = None,
) -> Image.Image:
    """Embed *payload* into *image* using LSB replacement.

    Parameters
    ----------
    image : PIL Image
        Cover image (any mode — will be converted to RGB).
    payload : bytes
        Raw payload bytes (already encrypted if applicable).
    encrypted : bool
        Written into the frame flags so the decoder can auto-detect.
    progress_cb : callable, optional
        Called with a float in [0, 1] to report progress.

    Returns
    -------
    PIL Image
        Stego image in RGB mode.
    """
    frame = build_frame(payload, encrypted=encrypted)
    bits = bytes_to_bits(frame)
    n_bits = len(bits)

    arr = np.array(image.convert("RGB"), dtype=np.uint8)
    flat = arr.flatten()

    if n_bits > flat.size:
        raise ValueError(
            f"Payload needs {n_bits} bits but image only has {flat.size} "
            "channels available. Use a larger image or shorter message."
        )

    # ── vectorized embedding (no Python loop) ────────────────────────────
    flat[:n_bits] = (flat[:n_bits] & np.uint8(0xFE)) | bits

    if progress_cb:
        progress_cb(1.0)

    return Image.fromarray(flat.reshape(arr.shape), "RGB")


def decode(
    image: Image.Image,
    *,
    progress_cb: Callable[[float], None] | None = None,
) -> tuple[bytes, bool]:
    """Extract hidden payload from a stego image.

    Returns
    -------
    (payload_bytes, is_encrypted)
        The raw payload and whether the encrypted flag was set.
    """
    arr = np.array(image.convert("RGB"), dtype=np.uint8)
    flat = arr.flatten()

    if flat.size < HEADER_BITS:
        raise ValueError("Image too small to contain any hidden data.")

    # ── read header (vectorized) ─────────────────────────────────────────
    header_bits = flat[:HEADER_BITS] & np.uint8(1)
    msg_len, is_encrypted = parse_header_bits(header_bits)

    total_bits = HEADER_BITS + msg_len * 8
    if total_bits > flat.size or msg_len > flat.size:
        raise ValueError(
            "No valid hidden message found. "
            "Make sure you uploaded the correct PNG stego image."
        )

    # ── read payload (vectorized) ────────────────────────────────────────
    msg_bits = flat[HEADER_BITS:total_bits] & np.uint8(1)

    if progress_cb:
        progress_cb(1.0)

    return bits_to_bytes(msg_bits)[:msg_len], is_encrypted
