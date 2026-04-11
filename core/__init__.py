"""
StegoVault Core — Steganography engine package.

Modules
-------
lsb      : Classic LSB spatial-domain steganography (vectorized).
cahrd    : CA-HRD adaptive DCT-domain reversible steganography.
crypto   : AES-256-GCM encryption / decryption with PBKDF2 key derivation.
metrics  : Image quality metrics (PSNR, windowed SSIM, histograms).
utils    : Shared helpers — bit conversion, length-prefix protocol, residual I/O.
"""

from .crypto import encrypt, decrypt, OVERHEAD as CRYPTO_OVERHEAD
from . import lsb, cahrd, metrics, utils
