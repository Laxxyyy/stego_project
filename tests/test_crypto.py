"""Tests for core.crypto — AES-256-GCM encryption / decryption."""

import pytest
from core.crypto import encrypt, decrypt, OVERHEAD


class TestEncryptDecrypt:
    """Round-trip and error tests for AES-256-GCM."""

    def test_round_trip_basic(self):
        plaintext = b"Hello, StegoVault!"
        password = "strongP@ssw0rd"
        ct = encrypt(plaintext, password)
        assert decrypt(ct, password) == plaintext

    def test_round_trip_empty(self):
        ct = encrypt(b"", "pw")
        assert decrypt(ct, "pw") == b""

    def test_round_trip_unicode(self):
        msg = "日本語テスト 🔐".encode("utf-8")
        ct = encrypt(msg, "パスワード")
        assert decrypt(ct, "パスワード") == msg

    def test_round_trip_large(self):
        data = b"X" * 100_000
        ct = encrypt(data, "pass")
        assert decrypt(ct, "pass") == data

    def test_overhead_size(self):
        ct = encrypt(b"test", "pw")
        assert len(ct) == len(b"test") + OVERHEAD

    def test_wrong_password_raises(self):
        ct = encrypt(b"secret", "correct")
        with pytest.raises(ValueError, match="[Dd]ecryption failed"):
            decrypt(ct, "wrong")

    def test_corrupted_data_raises(self):
        ct = encrypt(b"data", "pw")
        corrupted = ct[:20] + bytes([ct[20] ^ 0xFF]) + ct[21:]
        with pytest.raises(ValueError):
            decrypt(corrupted, "pw")

    def test_too_short_data_raises(self):
        with pytest.raises(ValueError, match="too short"):
            decrypt(b"short", "pw")

    def test_different_passwords_produce_different_ciphertexts(self):
        data = b"same data"
        ct1 = encrypt(data, "pw1")
        ct2 = encrypt(data, "pw2")
        assert ct1 != ct2

    def test_same_password_different_salts(self):
        """Two encryptions with the same password produce different ciphertext
        (random salt + nonce)."""
        data = b"identical"
        ct1 = encrypt(data, "same")
        ct2 = encrypt(data, "same")
        assert ct1 != ct2
