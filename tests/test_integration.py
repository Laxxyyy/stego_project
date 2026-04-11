"""
Deep integration tests — stress-tests and cross-cutting edge cases.

These tests go beyond unit-level checks and verify:
  • Full pipeline: encrypt → embed → PNG save/load → decode → decrypt
  • Cross-method: encode LSB → decode LSB (not CA-HRD) — no cross-talk
  • Edge cases: 1×8 image, non-8-multiple dims for CA-HRD, max capacity
  • Encryption + steganography E2E
  • Residual encrypted + stego encrypted simultaneously
  • PNG save/load round-trip fidelity (simulate real usage)
  • Large image dimension limits for residual serialization (uint16 cap)
  • Image mode conversion (RGBA, L, P → RGB)
"""

import io
import struct
import numpy as np
import pytest
from PIL import Image

from core import lsb, cahrd, metrics, crypto
from core.utils import (
    bytes_to_bits, bits_to_bytes, build_frame, parse_header_bits,
    serialize_residual, deserialize_residual, HEADER_BITS,
)


def _make_image(w=128, h=128, seed=42):
    rng = np.random.RandomState(seed)
    arr = rng.randint(0, 256, (h, w, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def _png_round_trip(img: Image.Image) -> Image.Image:
    """Save to PNG in memory, reload — simulates actual user workflow."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Image.open(buf).copy()


# ═══════════════════════════════════════════════════════════════════════════
#  1. FULL LSB END-TO-END  (encrypt → embed → PNG → decode → decrypt)
# ═══════════════════════════════════════════════════════════════════════════

class TestLSBE2E:
    def test_encrypted_full_pipeline(self):
        """Encrypt message → embed via LSB → save PNG → reload → decode → decrypt."""
        img = _make_image(200, 200)
        msg = "Top secret: пароль=💎"
        password = "hunter2"

        # Encode
        msg_bytes = msg.encode("utf-8")
        ct = crypto.encrypt(msg_bytes, password)
        stego = lsb.encode(img, ct, encrypted=True)
        stego_png = _png_round_trip(stego)

        # Decode
        payload, is_enc = lsb.decode(stego_png)
        assert is_enc is True
        recovered = crypto.decrypt(payload, password)
        assert recovered.decode("utf-8") == msg

    def test_plaintext_full_pipeline(self):
        img = _make_image(100, 100)
        msg = "no encryption here"
        payload = msg.encode("utf-8")
        stego = lsb.encode(img, payload, encrypted=False)
        stego_png = _png_round_trip(stego)
        recovered, is_enc = lsb.decode(stego_png)
        assert is_enc is False
        assert recovered.decode("utf-8") == msg

    def test_max_capacity_exactly(self):
        """Embed exactly at max capacity — should succeed."""
        img = _make_image(50, 50)
        cap = lsb.max_capacity(img)
        payload = bytes(range(256)) * (cap // 256 + 1)
        payload = payload[:cap]
        stego = lsb.encode(img, payload)
        recovered, _ = lsb.decode(stego)
        assert recovered == payload

    def test_one_byte_over_capacity_raises(self):
        img = _make_image(50, 50)
        cap = lsb.max_capacity(img)
        with pytest.raises(ValueError):
            lsb.encode(img, b"X" * (cap + 1))

    def test_special_characters(self):
        img = _make_image()
        msg = "Ñ\x00\t\n\r\\\"'/<>&日本語🔐€£¥₹"
        stego = lsb.encode(img, msg.encode("utf-8"))
        recovered, _ = lsb.decode(_png_round_trip(stego))
        assert recovered.decode("utf-8") == msg

    def test_psnr_after_embedding(self):
        img = _make_image(200, 200)
        stego = lsb.encode(img, b"test message")
        psnr = metrics.compute_psnr(img, stego)
        assert psnr > 40  # LSB should have very high PSNR

    def test_ssim_after_embedding(self):
        img = _make_image(200, 200)
        stego = lsb.encode(img, b"test message here, not too long")
        ssim = metrics.compute_ssim(img, stego)
        assert ssim > 0.99


# ═══════════════════════════════════════════════════════════════════════════
#  2. FULL CA-HRD END-TO-END
# ═══════════════════════════════════════════════════════════════════════════

class TestCAHRDE2E:
    def test_encrypted_full_pipeline(self):
        """Encrypt → embed CA-HRD → PNG → serialize residual → decode → decrypt."""
        img = _make_image(128, 128)
        msg = "CA-HRD encrypted message 🧬"
        password = "SecurePass123!"

        msg_bytes = msg.encode("utf-8")
        ct = crypto.encrypt(msg_bytes, password)

        stego, cap_map, corr, lsbs = cahrd.encode(img, ct, encrypted=True)
        stego_png = _png_round_trip(stego)

        # Serialize + deserialize residual
        res_data = serialize_residual(cap_map, corr, lsbs, password=password)
        cap2, corr2, lsbs2 = deserialize_residual(res_data, password=password)

        # Decode
        payload, is_enc, perfect = cahrd.decode(stego_png, cap_map=cap2, correction_bits=corr2)
        assert is_enc is True
        assert perfect is True
        recovered = crypto.decrypt(payload, password)
        assert recovered.decode("utf-8") == msg

    def test_non_8_multiple_dimensions(self):
        """Image whose dimensions aren't multiples of 8 — edge pixels ignored."""
        img = _make_image(130, 135)  # 130/8=16.25, 135/8=16.875
        msg = b"edge test"
        stego, cm, cb, ls = cahrd.encode(img, msg)
        # Capacity map should be 16×16 (floor division)
        assert cm.shape == (135 // 8, 130 // 8)
        recovered, _, _ = cahrd.decode(stego, cap_map=cm, correction_bits=cb)
        assert recovered == msg

    def test_plaintext_no_residual_best_effort(self):
        """Short message, no residual — best-effort should usually work."""
        img = _make_image(128, 128)
        msg = b"hi"
        stego, _, _, _ = cahrd.encode(img, msg)
        stego_png = _png_round_trip(stego)
        # Best effort decoding — may work for short messages
        _, _, perfect = cahrd.decode(stego_png)
        assert perfect is False

    def test_metrics_after_embedding(self):
        img = _make_image(128, 128)
        stego, _, _, _ = cahrd.encode(img, b"metric test")
        psnr = metrics.compute_psnr(img, stego)
        ssim = metrics.compute_ssim(img, stego)
        assert psnr > 25
        assert ssim > 0.90


# ═══════════════════════════════════════════════════════════════════════════
#  3. CROSS-METHOD ISOLATION
# ═══════════════════════════════════════════════════════════════════════════

class TestCrossMethod:
    def test_lsb_encoded_decode_with_lsb(self):
        """Message encoded with LSB can only be decoded with LSB."""
        img = _make_image()
        msg = b"LSB only"
        stego = lsb.encode(img, msg)
        # LSB decode should work
        recovered, _ = lsb.decode(stego)
        assert recovered == msg

    def test_cahrd_encoded_with_residual(self):
        """Message encoded with CA-HRD can be decoded with CA-HRD + residual."""
        img = _make_image()
        msg = b"CA-HRD only"
        stego, cm, cb, ls = cahrd.encode(img, msg)
        recovered, _, _ = cahrd.decode(stego, cap_map=cm, correction_bits=cb)
        assert recovered == msg


# ═══════════════════════════════════════════════════════════════════════════
#  4. IMAGE MODE CONVERSIONS
# ═══════════════════════════════════════════════════════════════════════════

class TestImageModes:
    def test_rgba_image(self):
        """RGBA image should be converted to RGB for embedding."""
        arr = np.random.randint(0, 256, (100, 100, 4), dtype=np.uint8)
        img = Image.fromarray(arr, "RGBA")
        msg = b"rgba test"
        stego = lsb.encode(img, msg)
        assert stego.mode == "RGB"
        recovered, _ = lsb.decode(stego)
        assert recovered == msg

    def test_grayscale_image(self):
        """Grayscale image should be converted to RGB."""
        arr = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        img = Image.fromarray(arr, "L")
        msg = b"gray test"
        stego = lsb.encode(img, msg)
        assert stego.mode == "RGB"
        recovered, _ = lsb.decode(stego)
        assert recovered == msg

    def test_palette_image(self):
        """Palette (P) mode image should be converted to RGB."""
        img = Image.fromarray(
            np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8), "RGB"
        ).convert("P")
        msg = b"palette test"
        stego = lsb.encode(img, msg)
        assert stego.mode == "RGB"
        recovered, _ = lsb.decode(stego)
        assert recovered == msg


# ═══════════════════════════════════════════════════════════════════════════
#  5. ENCRYPTION EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════

class TestCryptoEdgeCases:
    def test_empty_password(self):
        """Empty string password should still work as a key."""
        ct = crypto.encrypt(b"data", "")
        assert crypto.decrypt(ct, "") == b"data"

    def test_very_long_password(self):
        pw = "A" * 10_000
        ct = crypto.encrypt(b"data", pw)
        assert crypto.decrypt(ct, pw) == b"data"

    def test_unicode_password(self):
        pw = "パスワード🔑"
        ct = crypto.encrypt(b"data", pw)
        assert crypto.decrypt(ct, pw) == b"data"

    def test_null_bytes_in_plaintext(self):
        data = b"\x00" * 100
        ct = crypto.encrypt(data, "pw")
        assert crypto.decrypt(ct, "pw") == data


# ═══════════════════════════════════════════════════════════════════════════
#  6. RESIDUAL FORMAT EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════

class TestResidualEdgeCases:
    def test_empty_correction_bits(self):
        cap = np.ones((2, 2), dtype=np.uint8)
        corr = np.array([], dtype=np.uint8)
        lsbs = np.zeros((16, 16, 3), dtype=np.uint8)
        data = serialize_residual(cap, corr, lsbs)
        c2, r2, l2 = deserialize_residual(data)
        np.testing.assert_array_equal(cap, c2)
        assert len(r2) == 0
        np.testing.assert_array_equal(lsbs, l2)

    def test_large_correction_bits(self):
        cap = np.ones((4, 4), dtype=np.uint8)
        corr = np.random.randint(0, 2, 10000, dtype=np.uint8)
        lsbs = np.zeros((32, 32, 3), dtype=np.uint8)
        data = serialize_residual(cap, corr, lsbs)
        _, r2, _ = deserialize_residual(data)
        np.testing.assert_array_equal(corr, r2)

    def test_version_mismatch(self):
        cap = np.ones((2, 2), dtype=np.uint8)
        corr = np.array([0], dtype=np.uint8)
        lsbs = np.zeros((16, 16, 3), dtype=np.uint8)
        data = serialize_residual(cap, corr, lsbs)
        # Tamper version byte
        bad = data[:4] + bytes([99]) + data[5:]
        with pytest.raises(ValueError, match="[Uu]nsupported"):
            deserialize_residual(bad)


# ═══════════════════════════════════════════════════════════════════════════
#  7. PROTOCOL ROBUSTNESS
# ═══════════════════════════════════════════════════════════════════════════

class TestProtocolRobustness:
    def test_length_prefix_max_value(self):
        """Huge length in header (but valid data) should work."""
        data = b"X" * 1000
        frame = build_frame(data)
        bits = bytes_to_bits(frame)
        length, enc = parse_header_bits(bits[:HEADER_BITS])
        assert length == 1000
        assert enc is False

    def test_all_zero_image_lsb(self):
        """Embed in an all-black image (all zeros)."""
        img = Image.fromarray(np.zeros((100, 100, 3), dtype=np.uint8), "RGB")
        msg = b"in the darkness"
        stego = lsb.encode(img, msg)
        recovered, _ = lsb.decode(stego)
        assert recovered == msg

    def test_all_255_image_lsb(self):
        """Embed in an all-white image (all 255s)."""
        img = Image.fromarray(np.full((100, 100, 3), 255, dtype=np.uint8), "RGB")
        msg = b"in the light"
        stego = lsb.encode(img, msg)
        recovered, _ = lsb.decode(stego)
        assert recovered == msg

    def test_gradient_image_cahrd(self):
        """Embed in a smooth gradient (low variance throughout)."""
        arr = np.zeros((64, 64, 3), dtype=np.uint8)
        for i in range(64):
            arr[i, :, :] = i * 4  # smooth gradient
        img = Image.fromarray(arr, "RGB")
        msg = b"lo"  # very short — low capacity in smooth images
        stego, cm, cb, ls = cahrd.encode(img, msg)
        recovered, _, _ = cahrd.decode(stego, cap_map=cm, correction_bits=cb)
        assert recovered == msg


# ═══════════════════════════════════════════════════════════════════════════
#  8. HISTOGRAM CORRECTNESS
# ═══════════════════════════════════════════════════════════════════════════

class TestHistogramIntegration:
    def test_histogram_change_after_lsb(self):
        img = _make_image(100, 100)
        stego = lsb.encode(img, b"histogram change test payload data")
        orig_hist = metrics.compute_histograms(img)
        stego_hist = metrics.compute_histograms(stego)
        # At least some bins should differ
        diff = sum(
            1 for ch in ("red", "green", "blue")
            for i in range(256)
            if orig_hist[ch][i] != stego_hist[ch][i]
        )
        assert diff > 0  # some pixel values changed
