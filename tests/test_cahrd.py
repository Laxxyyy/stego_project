"""Tests for core.cahrd — CA-HRD DCT steganography."""

import numpy as np
import pytest
from PIL import Image

from core import cahrd
from core.utils import serialize_residual, deserialize_residual


def _make_image(w: int = 128, h: int = 128) -> Image.Image:
    """Create a random RGB test image (dimensions multiple of 8)."""
    arr = np.random.randint(0, 256, (h, w, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


class TestCAHRDCapacity:
    def test_capacity_positive(self):
        img = _make_image()
        cap = cahrd.max_capacity(img)
        assert cap > 0

    def test_capacity_scales_with_size(self):
        small = cahrd.max_capacity(_make_image(64, 64))
        large = cahrd.max_capacity(_make_image(256, 256))
        assert large > small


class TestCAHRDRoundTrip:
    def test_basic_with_residual(self):
        img = _make_image()
        msg = b"Hello CA-HRD!"
        stego, cap_map, corr_bits, orig_lsbs = cahrd.encode(img, msg)
        recovered, is_enc, perfect = cahrd.decode(
            stego, cap_map=cap_map, correction_bits=corr_bits,
        )
        assert recovered == msg
        assert is_enc is False
        assert perfect is True

    def test_encrypted_flag(self):
        img = _make_image()
        msg = b"encrypted"
        stego, cap_map, corr_bits, _ = cahrd.encode(img, msg, encrypted=True)
        recovered, is_enc, _ = cahrd.decode(
            stego, cap_map=cap_map, correction_bits=corr_bits,
        )
        assert recovered == msg
        assert is_enc is True

    def test_best_effort_without_residual(self):
        """Decode without residual — best-effort mode."""
        img = _make_image()
        msg = b"best effort"
        stego, _, _, _ = cahrd.encode(img, msg)
        recovered, _, perfect = cahrd.decode(stego)
        # Best-effort may or may not succeed due to DCT rounding
        # But the perfect flag should be False
        assert perfect is False

    def test_residual_serialization_round_trip(self):
        """Full pipeline: encode → serialize residual → deserialize → decode."""
        img = _make_image()
        msg = b"full pipeline test"
        stego, cap_map, corr_bits, orig_lsbs = cahrd.encode(img, msg)

        # Serialize and deserialize
        data = serialize_residual(cap_map, corr_bits, orig_lsbs)
        cap2, corr2, lsbs2 = deserialize_residual(data)

        recovered, _, perfect = cahrd.decode(
            stego, cap_map=cap2, correction_bits=corr2,
        )
        assert recovered == msg
        assert perfect is True

    def test_unicode_message(self):
        img = _make_image()
        msg = "Ñoño 日本語 🔐".encode("utf-8")
        stego, cap_map, corr_bits, _ = cahrd.encode(img, msg)
        recovered, _, _ = cahrd.decode(
            stego, cap_map=cap_map, correction_bits=corr_bits,
        )
        assert recovered == msg

    def test_progress_callback(self):
        img = _make_image()
        progress_values = []
        stego, _, _, _ = cahrd.encode(
            img, b"test", progress_cb=lambda p: progress_values.append(p),
        )
        assert len(progress_values) > 0
        assert max(progress_values) == pytest.approx(1.0, abs=0.1)


class TestCAHRDErrors:
    def test_payload_too_large(self):
        img = _make_image(32, 32)
        cap = cahrd.max_capacity(img)
        with pytest.raises(ValueError, match="[Pp]ayload needs|CA-HRD"):
            cahrd.encode(img, b"X" * (cap + 500))
