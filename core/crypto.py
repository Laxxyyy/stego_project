"""
AES-256-GCM encryption with PBKDF2-HMAC-SHA256 key derivation.

Wire format
-----------
    salt (16 B) ‖ nonce (12 B) ‖ ciphertext+tag  (variable)

The ``cryptography`` library's AESGCM automatically appends a 16-byte
authentication tag to the ciphertext, so total overhead is 44 bytes.
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# ── constants ────────────────────────────────────────────────────────────────
_SALT_SIZE = 16
_NONCE_SIZE = 12
_KEY_SIZE = 32        # AES-256
_TAG_SIZE = 16        # GCM authentication tag
_ITERATIONS = 480_000

OVERHEAD = _SALT_SIZE + _NONCE_SIZE + _TAG_SIZE  # 44 bytes


# ── internal ─────────────────────────────────────────────────────────────────

def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from *password* and *salt* via PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=_KEY_SIZE,
        salt=salt,
        iterations=_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


# ── public API ───────────────────────────────────────────────────────────────

def encrypt(plaintext: bytes, password: str) -> bytes:
    """Encrypt *plaintext* with AES-256-GCM using a password-derived key.

    Returns ``salt ‖ nonce ‖ ciphertext+tag``.
    """
    salt = os.urandom(_SALT_SIZE)
    key = _derive_key(password, salt)
    nonce = os.urandom(_NONCE_SIZE)
    aesgcm = AESGCM(key)
    ct_and_tag = aesgcm.encrypt(nonce, plaintext, None)
    return salt + nonce + ct_and_tag


def decrypt(data: bytes, password: str) -> bytes:
    """Decrypt data produced by :func:`encrypt`.

    Raises ``ValueError`` on wrong password or corrupted data.
    """
    min_len = _SALT_SIZE + _NONCE_SIZE + _TAG_SIZE
    if len(data) < min_len:
        raise ValueError("Encrypted data is too short to be valid.")

    salt = data[:_SALT_SIZE]
    nonce = data[_SALT_SIZE : _SALT_SIZE + _NONCE_SIZE]
    ct_and_tag = data[_SALT_SIZE + _NONCE_SIZE :]

    key = _derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ct_and_tag, None)
    except Exception as exc:
        raise ValueError(
            "Decryption failed — wrong password or corrupted data."
        ) from exc
