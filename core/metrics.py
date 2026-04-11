"""
Image quality metrics for steganography evaluation.

* PSNR  — Peak Signal-to-Noise Ratio.
* SSIM  — Structural Similarity Index (proper 11×11 Gaussian windowed,
           matching Wang et al. 2004).
* Histogram computation per RGB channel.
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from scipy.ndimage import convolve


# ── PSNR ─────────────────────────────────────────────────────────────────────

def compute_psnr(original: Image.Image, stego: Image.Image) -> float:
    """Compute PSNR (dB) between two images.  Higher is better."""
    orig = np.array(original.convert("RGB"), dtype=np.float64)
    stg = np.array(stego.convert("RGB"), dtype=np.float64)
    mse = np.mean((orig - stg) ** 2)
    if mse == 0:
        return float("inf")
    return float(10.0 * np.log10(255.0**2 / mse))


# ── SSIM (windowed) ──────────────────────────────────────────────────────────

def _gaussian_kernel_2d(size: int = 11, sigma: float = 1.5) -> np.ndarray:
    """Create a normalised 2-D Gaussian kernel."""
    coords = np.arange(size, dtype=np.float64) - (size - 1) / 2.0
    g = np.exp(-(coords**2) / (2.0 * sigma**2))
    kernel = np.outer(g, g)
    return kernel / kernel.sum()


def compute_ssim(original: Image.Image, stego: Image.Image) -> float:
    """Compute SSIM between two images using an 11×11 Gaussian window.

    Implements the standard Wang et al. (2004) algorithm with
    ``C1 = (0.01·255)²`` and ``C2 = (0.03·255)²``.
    """
    img1 = np.array(original.convert("L"), dtype=np.float64)
    img2 = np.array(stego.convert("L"), dtype=np.float64)

    C1 = (0.01 * 255.0) ** 2
    C2 = (0.03 * 255.0) ** 2

    kernel = _gaussian_kernel_2d(11, 1.5)

    mu1 = convolve(img1, kernel, mode="reflect")
    mu2 = convolve(img2, kernel, mode="reflect")

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = convolve(img1 * img1, kernel, mode="reflect") - mu1_sq
    sigma2_sq = convolve(img2 * img2, kernel, mode="reflect") - mu2_sq
    sigma12 = convolve(img1 * img2, kernel, mode="reflect") - mu1_mu2

    num = (2.0 * mu1_mu2 + C1) * (2.0 * sigma12 + C2)
    den = (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)

    ssim_map = num / den
    return float(np.mean(ssim_map))


# ── histograms ───────────────────────────────────────────────────────────────

def compute_histograms(image: Image.Image) -> dict[str, np.ndarray]:
    """Compute per-channel histograms (256 bins, range 0-255).

    Returns ``{"red": array, "green": array, "blue": array}``.
    """
    arr = np.array(image.convert("RGB"), dtype=np.uint8)
    return {
        "red": np.histogram(arr[:, :, 0], bins=256, range=(0, 255))[0],
        "green": np.histogram(arr[:, :, 1], bins=256, range=(0, 255))[0],
        "blue": np.histogram(arr[:, :, 2], bins=256, range=(0, 255))[0],
    }
