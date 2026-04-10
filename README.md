# 🔐 StegoVault · Hidden Ink

> **LSB + CA-HRD Image Steganography** — College Project Demo  
> Built with Streamlit · PIL · NumPy · SciPy

StegoVault lets you conceal secret text messages inside ordinary images and retrieve them later — completely invisible to the naked eye. It supports two steganographic methods: the classic **LSB** technique and the research-grade **CA-HRD** (Content-Aware Hybrid Reversible Steganography) algorithm.

---

## Table of Contents

- [Features](#features)
- [Methods Overview](#methods-overview)
  - [LSB — Classic](#lsb--classic)
  - [CA-HRD — Advanced](#ca-hrd--advanced)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Usage Guide](#usage-guide)
  - [Encoding a Message](#encoding-a-message)
  - [Decoding a Message](#decoding-a-message)
- [File Reference](#file-reference)
- [Technical Deep-Dive](#technical-deep-dive)
  - [LSB Algorithm](#lsb-algorithm)
  - [CA-HRD Algorithm](#ca-hrd-algorithm)
  - [Quality Metrics](#quality-metrics)
- [Method Comparison](#method-comparison)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [References](#references)

---

## Features

- **Two steganography methods** selectable per encode/decode session
- **Live capacity indicator** with colour-coded progress bar
- **Side-by-side image preview** (original vs. stego output)
- **PSNR & SSIM quality metrics** computed after every encode
- **Residual file system** for CA-HRD perfect reversible recovery
- **Download buttons** for stego image and residual file
- **Decoded message download** as `.txt`
- **Method comparison tab** with full feature table and technical deep-dive
- Refined dark editorial UI with responsive layout

---

## Methods Overview

### LSB — Classic

Hides bits by replacing the **Least Significant Bit** of each pixel channel value. A change of ±1 per channel is imperceptible to human vision. Fast, high-capacity, and simple.

### CA-HRD — Advanced

**Content-Aware Hybrid Reversible Steganography** uses luminance variance of each 8×8 image block to decide how many pixels to use for embedding — more bits in textured regions, fewer in smooth areas. Supports **Reversible Data Hiding (RDH)**: with the companion residual file, the original cover image can be mathematically restored.

---

## Installation

**Requirements:** Python 3.10 or newer.

```bash
# 1. Clone or download the project
git clone https://github.com/yourname/stegovault.git
cd stegovault

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the App

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## Usage Guide

### Encoding a Message

1. Open the **🔒 Encode** tab.
2. **Choose a method** from the selectbox:
   - `LSB (Classic)` — fastest, highest capacity
   - `CA-HRD (Advanced – Reversible & Content-Aware)` — better imperceptibility, reversible
3. **Upload a cover image** (PNG or JPG). The app shows the image dimensions and available capacity for the selected method.
4. **Type your secret message** in the text area. The live capacity bar shows how much of the image you are using.
5. Click **🔒 Embed Message**.
6. After embedding, the app shows:
   - Side-by-side preview of original and stego images
   - PSNR, SSIM, and output file size metrics
   - Download button(s)

**LSB output:** one PNG download.

**CA-HRD output:** two downloads — the stego PNG **and** a `residual.npy` file.

> ⚠️ **Keep `residual.npy` alongside the stego image.** It is required for perfect CA-HRD decoding. Without it, decoding still works but is best-effort.

---

### Decoding a Message

1. Open the **🔓 Decode** tab.
2. **Choose the matching decoding method** (must match what was used during encoding).
3. **Upload the stego PNG** exported by StegoVault.
4. *(CA-HRD only)* Upload the `residual.npy` file for perfect recovery.
5. Click **🔓 Decode Message**.
6. The revealed message appears in a monospace code box with character/word/byte stats.
7. Optionally download the message as a `.txt` file.

> ⚠️ Always use the original **PNG** file exported by StegoVault. Re-saving as JPEG destroys embedded data for both methods.

---

## File Reference

| File | Description |
|---|---|
| `app.py` | Main Streamlit application (all logic + UI) |
| `requirements.txt` | Python package dependencies |
| `stego_image.png` | LSB stego output |
| `stego_cahrd.png` | CA-HRD stego output |
| `residual.npy` | CA-HRD residual pack (capacity map + original LSBs) |
| `decoded_secret.txt` | Downloaded decoded message |

### residual.npy format

The residual file is a NumPy object array of length 2:

```
residual[0]  →  cap_map   shape (n_blocks_h, n_blocks_w)  dtype uint8
                Per-block pixel capacity used during encoding.

residual[1]  →  orig_lsb  shape (H, W, 3)                 dtype uint8
                Original pixel LSBs of the cover image.
                Used to restore the exact cover image (RDH).
```

Load manually:
```python
import numpy as np
residual = np.load("residual.npy", allow_pickle=True)
cap_map  = residual[0]
orig_lsb = residual[1]
```

---

## Technical Deep-Dive

### LSB Algorithm

**Embedding:**
1. Append the delimiter `|||END|||` to the message.
2. Encode payload as UTF-8 → flat binary string (8 bits per byte).
3. Walk every pixel channel in raster order. Replace the LSB of each channel value with the next payload bit (`val = (val & 0xFE) | bit`). Maximum distortion: ±1 per channel.
4. Save as lossless PNG.

**Extraction:**
1. Read LSBs of every channel in the same raster order.
2. Group bits into bytes; decode as UTF-8.
3. Stop when the delimiter `|||END|||` is found.

**Capacity:** `floor((H × W × 3 − delimiter_bits) / 8)` bytes.

---

### CA-HRD Algorithm

#### Content-Aware Capacity Selection

For each non-overlapping 8×8 pixel block, the **luminance variance** of the original image block is computed:

```
Y = 0.299·R + 0.587·G + 0.114·B
variance = Var(Y_block)
```

The variance is mapped to a **pixel capacity** (number of pixels used per block):

| Variance range | Pixels used | Rationale |
|---|---|---|
| > 800 | 16 | Rich texture — changes invisible |
| > 300 | 8 | Moderate texture |
| > 80 | 4 | Low texture |
| ≤ 80 | 2 | Smooth/flat — minimise distortion |

Each pixel contributes 3 bits (one per RGB channel), so effective bits per block range from 6 to 48.

#### Embedding

1. Convert payload (message + delimiter) → binary bitstream.
2. For each 8×8 block in raster order:
   - Compute luminance variance → capacity.
   - Store capacity in `cap_map[bi, bj]`.
   - Embed bits into the LSBs of the first `capacity` pixels in the block across all 3 channels.
3. Save `cap_map` and original LSBs (`orig_lsb = arr & 1`) into `residual.npy`.
4. Save stego image as lossless PNG.

#### Extraction

1. Load stego image.
2. If residual is available: read `cap_map` directly (guaranteed sync).  
   If no residual: recompute variance from the stego image (works for lossless PNG; may diverge slightly for processed images).
3. For each block, read the embedded bits from the matching pixel LSBs.
4. Accumulate bits → bytes → UTF-8 text. Stop at delimiter.

#### Reversible Data Hiding (RDH)

The `orig_lsb` array in `residual.npy` stores the original LSB of every pixel channel before modification. To perfectly restore the cover image:

```python
cover_restored = stego_arr.copy()
cover_restored[:, :, :] = (stego_arr & 0xFE) | orig_lsb
```

This satisfies the RDH property: the original image is recovered with zero distortion after message extraction.

---

### Quality Metrics

**PSNR (Peak Signal-to-Noise Ratio)**

```
PSNR = 10 · log₁₀(255² / MSE)   [dB]
```

Higher is better. Typical values:
- LSB: ~51–58 dB (minimal pixel changes)
- CA-HRD: ~46–54 dB (slightly more pixels touched per block but perceptually well-distributed)

**SSIM (Structural Similarity Index)**

Range [0, 1]. Values above 0.999 are considered visually lossless. Both methods consistently achieve > 0.999 on standard test images.

> Note: LSB tends to score higher PSNR than CA-HRD because LSB changes exactly 1 bit per pixel uniformly, while CA-HRD touches multiple pixels per block. However, CA-HRD concentrates changes in visually busy areas, making them perceptually less noticeable despite the lower PSNR number.

---

## Method Comparison

| Property | LSB | CA-HRD |
|---|---|---|
| Embedding domain | Spatial (pixel values) | Spatial, block-adaptive |
| Capacity | High (1 bit/channel/pixel) | Adaptive (6–48 bits/block) |
| PSNR | ~51–58 dB | ~46–54 dB |
| SSIM | > 0.999 | > 0.999 |
| Perceptual quality | Good | Excellent (texture-aware) |
| JPEG robustness | ❌ Destroyed | ❌ Destroyed (use PNG) |
| Reversibility | ❌ Cover image lost | ✅ Perfect via residual |
| Content-awareness | ❌ Uniform | ✅ Variance-adaptive |
| Extra files | None | `residual.npy` |
| Speed | Very fast | Moderate |
| Best for | Large messages, trusted channels | High-quality covert comms, forensics |

---

## Project Structure

```
stegovault/
├── app.py              # Streamlit app — all logic and UI
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## Dependencies

```
streamlit >= 1.32.0
Pillow    >= 10.0.0
numpy     >= 1.26.0
scipy     >= 1.12.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## References

- Cox, I. et al. (2008). *Digital Watermarking and Steganography*. Morgan Kaufmann.
- Tian, J. (2003). Reversible Data Embedding Using a Difference Expansion. *IEEE Transactions on Circuits and Systems for Video Technology*, 13(8), 890–896.
- Fridrich, J. et al. (2001). Detecting LSB Steganography in Color and Grayscale Images. *IEEE Multimedia*, 8(4), 22–28.
- Wallace, G.K. (1992). The JPEG Still Picture Compression Standard. *IEEE Transactions on Consumer Electronics*, 38(1), xviii–xxxiv.
- Pevný, T. et al. (2010). Using High-Dimensional Image Models to Perform Highly Undetectable Steganography. *Information Hiding*, 161–177.

---

*StegoVault · LSB + CA-HRD Image Steganography · College Project Demo*  
*Built with Streamlit · PIL · NumPy · SciPy*