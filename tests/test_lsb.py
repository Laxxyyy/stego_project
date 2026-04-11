"""Tests for core.lsb — vectorized LSB steganography."""

import numpy as np
import pytest
from PIL import Image

from core import lsb


def _make_image(w: int = 100, h: int = 100) -> Image.Image:
    """Create a random RGB test image."""
    arr = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


class TestLSBCapacity:
    def test_capacity_positive(self):
        img = _make_image(100, 100)
        cap = lsb.max_capacity(img)
        assert cap > 0

    def test_capacity_scales_with_size(self):
        small = lsb.max_capacity(_make_image(50, 50))
        large = lsb.max_capacity(_make_image(200, 200))
        assert large > small

    def test_capacity_value(self):
        img = _make_image(100, 100)
        expected = (100 * 100 * 3 - 40) // 8  # 40 header bits
        assert lsb.max_capacity(img) == expected


class TestLSBRoundTrip:
    def test_basic(self):
        img = _make_image()
        msg = b"Hello, StegoVault!"
        stego = lsb.encode(img, msg)
        recovered, is_enc = lsb.decode(stego)
        assert recovered == msg
        assert is_enc is False

    def test_encrypted_flag(self):
        img = _make_image()
        msg = b"encrypted payload"
        stego = lsb.encode(img, msg, encrypted=True)
        recovered, is_enc = lsb.decode(stego)
        assert recovered == msg
        assert is_enc is True

    def test_empty_payload(self):
        img = _make_image()
        stego = lsb.encode(img, b"")
        recovered, is_enc = lsb.decode(stego)
        assert recovered == b""

    def test_unicode_utf8(self):
        img = _make_image()
        msg = "日本語テスト 🔐 Ñoño".encode("utf-8")
        stego = lsb.encode(img, msg)
        recovered, _ = lsb.decode(stego)
        assert recovered == msg

    def test_large_message(self):
        img = _make_image(300, 300)
        cap = lsb.max_capacity(img)
        msg = bytes(range(256)) * (cap // 256)
        msg = msg[:cap]
        stego = lsb.encode(img, msg)
        recovered, _ = lsb.decode(stego)
        assert recovered == msg

    def test_binary_data(self):
        img = _make_image()
        msg = bytes(range(256))
        stego = lsb.encode(img, msg)
        recovered, _ = lsb.decode(stego)
        assert recovered == msg

    def test_progress_callback(self):
        img = _make_image()
        progress_values = []
        stego = lsb.encode(img, b"test", progress_cb=lambda p: progress_values.append(p))
        assert 1.0 in progress_values

    def test_image_visually_similar(self):
        img = _make_image()
        stego = lsb.encode(img, b"test message")
        orig_arr = np.array(img)
        stego_arr = np.array(stego)
        # Max per-pixel change should be ±1 (LSB only)
        diff = np.abs(orig_arr.astype(int) - stego_arr.astype(int))
        assert diff.max() <= 1


class TestLSBErrors:
    def test_payload_too_large(self):
        img = _make_image(10, 10)
        cap = lsb.max_capacity(img)
        with pytest.raises(ValueError, match="[Pp]ayload needs"):
            lsb.encode(img, b"X" * (cap + 100))

    def test_decode_tiny_image(self):
        img = _make_image(1, 1)
        with pytest.raises(ValueError):
            lsb.decode(img)
