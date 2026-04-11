"""
CA-HRD — Content-Aware Hybrid Reversible DCT Steganography.

Embeds payload bits into mid-frequency DCT coefficients of 8×8 blocks.
Luminance variance drives per-block capacity (content-aware).
A residual file stores XOR correction bits and original pixel LSBs for
mathematically perfect reversible data hiding (RDH).

Uses ``scipy.fft.dctn / idctn`` (modern API, replaces deprecated fftpack).
"""

from __future__ import annotations

from typing import Callable

import numpy as np
from PIL import Image
from scipy.fft import dctn, idctn

from .utils import (
    bytes_to_bits,
    bits_to_bytes,
    build_frame,
    parse_header_bits,
    HEADER_BITS,
)

# ── zigzag scan order for 8×8 block ─────────────────────────────────────────
_ZIGZAG = [
    (0, 0), (0, 1), (1, 0), (2, 0), (1, 1), (0, 2), (0, 3), (1, 2),
    (2, 1), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (0, 5),
    (1, 4), (2, 3), (3, 2), (4, 1), (5, 0), (6, 0), (5, 1), (4, 2),
    (3, 3), (2, 4), (1, 5), (0, 6), (0, 7), (1, 6), (2, 5), (3, 4),
    (4, 3), (5, 2), (6, 1), (7, 0), (7, 1), (6, 2), (5, 3), (4, 4),
    (3, 5), (2, 6), (1, 7), (2, 7), (3, 6), (4, 5), (5, 4), (6, 3),
    (7, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 7), (4, 7), (5, 6),
    (6, 5), (7, 4), (7, 5), (6, 6), (5, 7), (6, 7), (7, 6), (7, 7),
]


# ── internal helpers ─────────────────────────────────────────────────────────

def _dct2d(block: np.ndarray) -> np.ndarray:
    """Forward 2-D type-II DCT (ortho-normalised)."""
    return dctn(block, type=2, norm="ortho")


def _idct2d(block: np.ndarray) -> np.ndarray:
    """Inverse 2-D type-II DCT (ortho-normalised)."""
    return idctn(block, type=2, norm="ortho")


def _block_capacity(variance: float) -> int:
    """Map luminance variance → number of DCT coefficients per channel."""
    if variance > 800:
        return 6
    if variance > 300:
        return 4
    if variance > 80:
        return 2
    return 1


def _luminance(arr: np.ndarray) -> np.ndarray:
    """BT.601 luminance from an (H, W, 3) RGB float64 array."""
    return (
        0.299 * arr[:, :, 0]
        + 0.587 * arr[:, :, 1]
        + 0.114 * arr[:, :, 2]
    )


# ── public API ───────────────────────────────────────────────────────────────

def max_capacity(image: Image.Image) -> int:
    """Max payload bytes the image can hold via CA-HRD embedding."""
    arr = np.array(image.convert("RGB"), dtype=np.float64)
    h, w = arr.shape[:2]
    lum = _luminance(arr)

    total_bits = 0
    for by in range(0, h - 7, 8):
        for bx in range(0, w - 7, 8):
            var = float(np.var(lum[by : by + 8, bx : bx + 8]))
            total_bits += _block_capacity(var) * 3  # 3 channels

    return max(0, (total_bits - HEADER_BITS) // 8)


def encode(
    image: Image.Image,
    payload: bytes,
    *,
    encrypted: bool = False,
    progress_cb: Callable[[float], None] | None = None,
) -> tuple[Image.Image, np.ndarray, np.ndarray, np.ndarray]:
    """Embed *payload* using adaptive DCT-domain steganography.

    Returns
    -------
    (stego_image, cap_map, correction_bits, orig_pixel_lsbs)
    """
    frame = build_frame(payload, encrypted=encrypted)
    bits = bytes_to_bits(frame)
    n_bits = len(bits)

    arr = np.array(image.convert("RGB"), dtype=np.uint8)
    h, w = arr.shape[:2]

    # Store original pixel LSBs for reversible data hiding
    orig_pixel_lsbs = (arr & 1).astype(np.uint8)

    lum = _luminance(arr.astype(np.float64))
    n_bh, n_bw = h // 8, w // 8
    cap_map = np.zeros((n_bh, n_bw), dtype=np.uint8)

    stego_float = arr.astype(np.float64)
    bit_idx = 0
    embed_log: list[tuple[int, int, int, int, int]] = []

    for bi in range(n_bh):
        by = bi * 8
        for bj in range(n_bw):
            bx = bj * 8
            var = float(np.var(lum[by : by + 8, bx : bx + 8]))
            cap = _block_capacity(var)
            cap_map[bi, bj] = cap
            if bit_idx >= n_bits:
                continue
            for ch in range(3):
                if bit_idx >= n_bits:
                    break
                block = stego_float[by : by + 8, bx : bx + 8, ch].copy()
                dct_block = _dct2d(block)
                for k in range(1, cap + 1):
                    if bit_idx >= n_bits:
                        break
                    zy, zx = _ZIGZAG[k]
                    coeff_int = int(np.round(dct_block[zy, zx]))
                    intended = int(bits[bit_idx])
                    coeff_int = (coeff_int & ~1) | intended
                    dct_block[zy, zx] = float(coeff_int)
                    embed_log.append((bi, bj, ch, k, intended))
                    bit_idx += 1
                stego_float[by : by + 8, bx : bx + 8, ch] = _idct2d(dct_block)

        # Report progress per block-row
        if progress_cb:
            progress_cb((bi + 1) / n_bh)

    if bit_idx < n_bits:
        raise ValueError(
            f"CA-HRD: payload needs {n_bits} bits but image provides only "
            f"{bit_idx}. Use a larger image or shorter message."
        )

    stego_uint8 = np.clip(np.round(stego_float), 0, 255).astype(np.uint8)

    # ── compute XOR correction bits for DCT round-trip rounding ──────────
    correction_bits: list[int] = []
    dct_cache: dict[tuple[int, int, int], np.ndarray] = {}

    for bi, bj, ch, k, intended in embed_log:
        key = (bi, bj, ch)
        if key not in dct_cache:
            by, bx = bi * 8, bj * 8
            dct_cache[key] = _dct2d(
                stego_uint8[by : by + 8, bx : bx + 8, ch].astype(np.float64)
            )
        zy, zx = _ZIGZAG[k]
        recovered_lsb = int(np.round(dct_cache[key][zy, zx])) & 1
        correction_bits.append(recovered_lsb ^ intended)

    return (
        Image.fromarray(stego_uint8, "RGB"),
        cap_map,
        np.array(correction_bits, dtype=np.uint8),
        orig_pixel_lsbs,
    )


def decode(
    image: Image.Image,
    cap_map: np.ndarray | None = None,
    correction_bits: np.ndarray | None = None,
    *,
    progress_cb: Callable[[float], None] | None = None,
) -> tuple[bytes, bool, bool]:
    """Extract hidden payload from a CA-HRD stego image.

    Parameters
    ----------
    cap_map, correction_bits : optional
        From the residual file.  When provided, decoding is *perfect*;
        otherwise best-effort (recompute variance from stego pixels).

    Returns
    -------
    (payload_bytes, is_encrypted, used_perfect_mode)
    """
    arr = np.array(image.convert("RGB"), dtype=np.uint8)
    h, w = arr.shape[:2]
    n_bh, n_bw = h // 8, w // 8

    perfect = cap_map is not None and correction_bits is not None
    lum = None
    if not perfect:
        lum = _luminance(arr.astype(np.float64))

    raw_bits: list[int] = []
    corr_idx = 0
    header_parsed = False
    payload_len = 0
    is_encrypted = False
    total_needed = HEADER_BITS  # start by reading header

    for bi in range(n_bh):
        by = bi * 8
        for bj in range(n_bw):
            bx = bj * 8
            if perfect:
                cap = int(cap_map[bi, bj])
            else:
                var = float(np.var(lum[by : by + 8, bx : bx + 8]))
                cap = _block_capacity(var)

            for ch in range(3):
                block = arr[by : by + 8, bx : bx + 8, ch].astype(np.float64)
                dct_block = _dct2d(block)
                for k in range(1, cap + 1):
                    if len(raw_bits) >= total_needed:
                        break
                    zy, zx = _ZIGZAG[k]
                    bit = int(np.round(dct_block[zy, zx])) & 1
                    if perfect and corr_idx < len(correction_bits):
                        bit ^= int(correction_bits[corr_idx])
                        corr_idx += 1
                    raw_bits.append(bit)

                    # Parse header once we have enough bits
                    if not header_parsed and len(raw_bits) >= HEADER_BITS:
                        hdr = np.array(raw_bits[:HEADER_BITS], dtype=np.uint8)
                        payload_len, is_encrypted = parse_header_bits(hdr)
                        total_needed = HEADER_BITS + payload_len * 8
                        header_parsed = True

                if len(raw_bits) >= total_needed and header_parsed:
                    break
            if len(raw_bits) >= total_needed and header_parsed:
                break

        if progress_cb:
            progress_cb((bi + 1) / n_bh)
        if len(raw_bits) >= total_needed and header_parsed:
            break

    if not header_parsed:
        raise ValueError(
            "No CA-HRD hidden message found. "
            "Ensure you uploaded the correct PNG stego image."
        )

    payload_bits = np.array(
        raw_bits[HEADER_BITS : HEADER_BITS + payload_len * 8], dtype=np.uint8
    )
    payload_bytes = bits_to_bytes(payload_bits)[:payload_len]

    return payload_bytes, is_encrypted, perfect
