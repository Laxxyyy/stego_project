"""Tests for core.metrics — PSNR, SSIM, histograms."""

import numpy as np
import pytest
from PIL import Image

from core.metrics import compute_psnr, compute_ssim, compute_histograms


def _make_image(w: int = 100, h: int = 100, seed: int = 42) -> Image.Image:
    rng = np.random.RandomState(seed)
    arr = rng.randint(0, 256, (h, w, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


class TestPSNR:
    def test_identical_images(self):
        img = _make_image()
        psnr = compute_psnr(img, img)
        # compute_psnr no longer returns inf; it floors MSE at a tiny epsilon,
        # giving a very large finite value (~323 dB) for identical images.
        assert psnr > 300 and np.isfinite(psnr)

    def test_different_images(self):
        img1 = _make_image(seed=1)
        img2 = _make_image(seed=2)
        psnr = compute_psnr(img1, img2)
        assert 0 < psnr < 100

    def test_slight_modification(self):
        img = _make_image()
        arr = np.array(img).copy()
        arr[0, 0, 0] = np.uint8((int(arr[0, 0, 0]) + 1) % 256)
        modified = Image.fromarray(arr, "RGB")
        psnr = compute_psnr(img, modified)
        assert psnr > 50  # very small change → very high PSNR


class TestSSIM:
    def test_identical_images(self):
        img = _make_image()
        ssim = compute_ssim(img, img)
        assert ssim == pytest.approx(1.0, abs=1e-6)

    def test_different_images(self):
        img1 = _make_image(seed=1)
        img2 = _make_image(seed=2)
        ssim = compute_ssim(img1, img2)
        assert -1 <= ssim < 1  # can be slightly negative for uncorrelated random images

    def test_ssim_range(self):
        """SSIM should be in [-1, 1] range."""
        img1 = _make_image(seed=10)
        img2 = _make_image(seed=20)
        ssim = compute_ssim(img1, img2)
        assert -1 <= ssim <= 1

    def test_near_identical_high_ssim(self):
        """A single pixel change should give SSIM very close to 1."""
        img = _make_image()
        arr = np.array(img).copy()
        arr[50, 50, 0] = np.uint8((int(arr[50, 50, 0]) + 1) % 256)
        modified = Image.fromarray(arr, "RGB")
        ssim = compute_ssim(img, modified)
        assert ssim > 0.99


class TestHistograms:
    def test_keys(self):
        img = _make_image()
        h = compute_histograms(img)
        assert set(h.keys()) == {"red", "green", "blue"}

    def test_shape(self):
        img = _make_image()
        h = compute_histograms(img)
        for ch in ("red", "green", "blue"):
            assert h[ch].shape == (256,)

    def test_sum_equals_pixel_count(self):
        w, h_px = 100, 100
        img = _make_image(w, h_px)
        h = compute_histograms(img)
        for ch in ("red", "green", "blue"):
            assert h[ch].sum() == w * h_px

    def test_solid_image(self):
        arr = np.full((50, 50, 3), 128, dtype=np.uint8)
        img = Image.fromarray(arr, "RGB")
        h = compute_histograms(img)
        for ch in ("red", "green", "blue"):
            assert h[ch][128] == 50 * 50
            assert h[ch].sum() == 50 * 50
