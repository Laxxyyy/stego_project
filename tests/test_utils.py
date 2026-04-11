"""Tests for core.utils — bit conversion, framing, residual I/O."""

import numpy as np
import pytest
from core.utils import (
    bytes_to_bits,
    bits_to_bytes,
    build_frame,
    parse_header_bits,
    serialize_residual,
    deserialize_residual,
    HEADER_BITS,
)


class TestBitConversion:
    def test_round_trip(self):
        data = b"Hello World"
        bits = bytes_to_bits(data)
        assert len(bits) == len(data) * 8
        assert bits_to_bytes(bits) == data

    def test_empty(self):
        bits = bytes_to_bits(b"")
        assert len(bits) == 0
        assert bits_to_bytes(bits) == b""

    def test_single_byte(self):
        bits = bytes_to_bits(b"\xff")
        assert all(b == 1 for b in bits)
        assert bits_to_bytes(bits) == b"\xff"

    def test_zero_byte(self):
        bits = bytes_to_bits(b"\x00")
        assert all(b == 0 for b in bits)

    def test_values_are_0_or_1(self):
        bits = bytes_to_bits(b"test data 123")
        assert set(np.unique(bits)).issubset({0, 1})


class TestFrameProtocol:
    def test_round_trip_plaintext(self):
        payload = b"secret message"
        frame = build_frame(payload, encrypted=False)
        bits = bytes_to_bits(frame)
        length, enc = parse_header_bits(bits[:HEADER_BITS])
        assert length == len(payload)
        assert enc is False

    def test_round_trip_encrypted(self):
        payload = b"encrypted data"
        frame = build_frame(payload, encrypted=True)
        bits = bytes_to_bits(frame)
        length, enc = parse_header_bits(bits[:HEADER_BITS])
        assert length == len(payload)
        assert enc is True

    def test_frame_size(self):
        payload = b"data"
        frame = build_frame(payload)
        assert len(frame) == 5 + len(payload)  # 4 (length) + 1 (flags) + payload

    def test_empty_payload(self):
        frame = build_frame(b"")
        bits = bytes_to_bits(frame)
        length, enc = parse_header_bits(bits[:HEADER_BITS])
        assert length == 0
        assert enc is False

    def test_header_too_short_raises(self):
        with pytest.raises(ValueError, match="Not enough bits"):
            parse_header_bits(np.zeros(30, dtype=np.uint8))


class TestResidualIO:
    def _make_residual_data(self):
        cap_map = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        correction_bits = np.array([0, 1, 1, 0, 1], dtype=np.uint8)
        orig_lsbs = np.random.randint(0, 2, (16, 16, 3), dtype=np.uint8)
        return cap_map, correction_bits, orig_lsbs

    def test_round_trip_no_password(self):
        cap, corr, lsbs = self._make_residual_data()
        data = serialize_residual(cap, corr, lsbs)
        cap2, corr2, lsbs2 = deserialize_residual(data)
        np.testing.assert_array_equal(cap, cap2)
        np.testing.assert_array_equal(corr, corr2)
        np.testing.assert_array_equal(lsbs, lsbs2)

    def test_round_trip_with_password(self):
        cap, corr, lsbs = self._make_residual_data()
        data = serialize_residual(cap, corr, lsbs, password="test123")
        cap2, corr2, lsbs2 = deserialize_residual(data, password="test123")
        np.testing.assert_array_equal(cap, cap2)
        np.testing.assert_array_equal(corr, corr2)
        np.testing.assert_array_equal(lsbs, lsbs2)

    def test_wrong_password_raises(self):
        cap, corr, lsbs = self._make_residual_data()
        data = serialize_residual(cap, corr, lsbs, password="correct")
        with pytest.raises(ValueError):
            deserialize_residual(data, password="wrong")

    def test_encrypted_without_password_raises(self):
        cap, corr, lsbs = self._make_residual_data()
        data = serialize_residual(cap, corr, lsbs, password="pw")
        with pytest.raises(ValueError, match="[Ee]ncrypted"):
            deserialize_residual(data)  # no password provided

    def test_magic_header(self):
        cap, corr, lsbs = self._make_residual_data()
        data = serialize_residual(cap, corr, lsbs)
        assert data[:4] == b"SVRD"

    def test_invalid_magic_raises(self):
        with pytest.raises(ValueError, match="missing SVRD"):
            deserialize_residual(b"BADDATA")
