"""
Shared utilities for StegoVault core.

Provides:
* Bit ↔ byte conversion (NumPy vectorized).
* Length-prefix encode / decode protocol.
* Safe binary serialization for CA-HRD residual files (.svr format).
* Image upload validation helpers.
"""

from __future__ import annotations

import struct
from typing import Callable

import numpy as np

# ── constants ────────────────────────────────────────────────────────────────
HEADER_BITS = 40  # 32 (length) + 8 (flags)
SUPPORTED_TYPES = {"image/png", "image/jpeg", "image/jpg"}

# Residual file format
_MAGIC = b"SVRD"
_VERSION = 1


# ── bit conversion ───────────────────────────────────────────────────────────

def bytes_to_bits(data: bytes) -> np.ndarray:
    """Convert *data* to a flat uint8 array of 0s and 1s."""
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def bits_to_bytes(bits: np.ndarray) -> bytes:
    """Convert a flat uint8 array of 0s / 1s back to bytes.

    If ``len(bits)`` is not a multiple of 8 the array is zero-padded.
    """
    remainder = len(bits) % 8
    if remainder:
        bits = np.concatenate([bits, np.zeros(8 - remainder, dtype=np.uint8)])
    return np.packbits(bits).tobytes()


# ── length-prefix protocol ──────────────────────────────────────────────────
#
# Wire format (embedded inside the image):
#   [32 bits : payload length in bytes, big-endian]
#   [ 8 bits : flags byte]
#   [payload bits …]
#
# Flags byte — bit 0: 1 = encrypted, 0 = plaintext; bits 1-7 reserved (0).
# ─────────────────────────────────────────────────────────────────────────────

def build_frame(payload: bytes, *, encrypted: bool = False) -> bytes:
    """Wrap *payload* with a length-prefix + flags header.

    Returns the full frame as raw bytes ready for bit conversion.
    """
    flags = (1 if encrypted else 0).to_bytes(1, "big")
    length = struct.pack(">I", len(payload))
    return length + flags + payload


def parse_header_bits(header_bits: np.ndarray) -> tuple[int, bool]:
    """Parse the first 40 embedded bits into ``(payload_length, is_encrypted)``."""
    if len(header_bits) < HEADER_BITS:
        raise ValueError("Not enough bits to read frame header.")
    length_bytes = bits_to_bytes(header_bits[:32])
    payload_len = struct.unpack(">I", length_bytes)[0]
    flags_byte = bits_to_bytes(header_bits[32:40])
    is_encrypted = bool(flags_byte[0] & 0x01)
    return payload_len, is_encrypted


# ── residual I/O (.svr format — no pickle) ──────────────────────────────────
#
# Binary layout:
#   b"SVRD"          4 B  magic
#   version          1 B
#   encrypted_flag   1 B  (0 = plain, 1 = AES-encrypted body)
#   ---- body (optionally encrypted) ----
#   n_bh             2 B  uint16 BE
#   n_bw             2 B
#   H                2 B
#   W                2 B
#   n_corrections    4 B  uint32 BE
#   cap_map          n_bh × n_bw  B
#   correction_bits  n_corrections B
#   orig_pixel_lsbs  H × W × 3    B
# ─────────────────────────────────────────────────────────────────────────────

def serialize_residual(
    cap_map: np.ndarray,
    correction_bits: np.ndarray,
    orig_pixel_lsbs: np.ndarray,
    password: str | None = None,
) -> bytes:
    """Serialize CA-HRD residual data to safe binary format.

    If *password* is given the body is AES-256-GCM encrypted.
    """
    from . import crypto  # lazy import to avoid circular

    n_bh, n_bw = cap_map.shape
    h, w = orig_pixel_lsbs.shape[:2]
    n_corrections = len(correction_bits)

    body_header = struct.pack(">HHHHI", n_bh, n_bw, h, w, n_corrections)
    body = (
        body_header
        + cap_map.astype(np.uint8).tobytes()
        + correction_bits.astype(np.uint8).tobytes()
        + orig_pixel_lsbs.astype(np.uint8).tobytes()
    )

    encrypted_flag = 0
    if password:
        body = crypto.encrypt(body, password)
        encrypted_flag = 1

    return _MAGIC + bytes([_VERSION, encrypted_flag]) + body


def deserialize_residual(
    data: bytes,
    password: str | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Deserialize CA-HRD residual data.

    Returns ``(cap_map, correction_bits, orig_pixel_lsbs)``.
    """
    from . import crypto

    if data[:4] != _MAGIC:
        raise ValueError("Invalid residual file — missing SVRD magic header.")
    version = data[4]
    if version != _VERSION:
        raise ValueError(f"Unsupported residual format version: {version}")

    encrypted_flag = data[5]
    body = data[6:]

    if encrypted_flag:
        if not password:
            raise ValueError(
                "This residual file is encrypted. Provide the password."
            )
        body = crypto.decrypt(body, password)

    hdr_size = struct.calcsize(">HHHHI")
    n_bh, n_bw, h, w, n_corrections = struct.unpack(">HHHHI", body[:hdr_size])
    offset = hdr_size

    cap_map_size = n_bh * n_bw
    cap_map = (
        np.frombuffer(body[offset : offset + cap_map_size], dtype=np.uint8)
        .reshape(n_bh, n_bw)
        .copy()
    )
    offset += cap_map_size

    correction_bits = np.frombuffer(
        body[offset : offset + n_corrections], dtype=np.uint8
    ).copy()
    offset += n_corrections

    lsb_size = h * w * 3
    orig_pixel_lsbs = (
        np.frombuffer(body[offset : offset + lsb_size], dtype=np.uint8)
        .reshape(h, w, 3)
        .copy()
    )

    return cap_map, correction_bits, orig_pixel_lsbs


# ── image validation ─────────────────────────────────────────────────────────

def validate_upload(uploaded_file) -> tuple[bool, str]:
    """Check whether an uploaded file is usable.

    Returns ``(ok, warning_message)``.  *warning_message* is empty when
    there is nothing to warn about.
    """
    if uploaded_file is None:
        return False, ""
    if uploaded_file.type not in SUPPORTED_TYPES:
        return False, (
            f"Unsupported file type: <strong>{uploaded_file.type}</strong>. "
            "Please upload a PNG or JPG."
        )
    if uploaded_file.type in {"image/jpeg", "image/jpg"}:
        return True, (
            "⚠️ JPEG detected — JPEG compression destroys embedded data. "
            "Use the original <strong>PNG</strong> exported by StegoVault."
        )
    return True, ""
