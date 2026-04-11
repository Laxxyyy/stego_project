# 🔐 StegoVault · Hidden Ink

> **LSB + CA-HRD Image Steganography · AES-256-GCM Encrypted**  
> Built with Streamlit · PIL · NumPy · SciPy · Cryptography

StegoVault lets you conceal secret text messages inside ordinary images and retrieve them later — completely invisible to the naked eye. It supports two steganographic methods: the classic **LSB** technique and the research-grade **CA-HRD** (Content-Aware Hybrid Reversible Steganography) algorithm. Messages can optionally be encrypted with **AES-256-GCM** before embedding.

---

## Table of Contents

- [Features](#features)
- [Methods Overview](#methods-overview)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Usage Guide](#usage-guide)
- [Security Architecture](#security-architecture)
- [Technical Deep-Dive](#technical-deep-dive)
- [Method Comparison](#method-comparison)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Dependencies](#dependencies)
- [References](#references)

---

## Features

- **Two steganography methods** selectable per encode/decode session
- **AES-256-GCM encryption** — optional password-based message encryption
- **Auto-detect encryption** — decoder automatically detects if a message was encrypted
- **Batch processing** — embed the same message in multiple images at once
- **Live capacity indicator** with colour-coded progress bar
- **Side-by-side image preview** (original vs. stego output)
- **PSNR & windowed SSIM** quality metrics (Wang et al. 2004 standard)
- **Histogram Analysis tab** — per-channel pixel distribution comparison
- **Progress bars** for long-running CA-HRD operations
- **Safe residual format** (.svr) — no Python pickle, optionally encrypted
- **Image format validation** — warns when JPEG is uploaded for decoding
- **Length-prefix protocol** — no delimiter vulnerability
- Refined dark editorial UI with responsive layout

---

## Methods Overview

### LSB — Classic

Hides bits by replacing the **Least Significant Bit** of each pixel channel value. Fully vectorized using NumPy — no Python loops.

### CA-HRD — Advanced

**Content-Aware Hybrid Reversible Steganography** embeds payload bits into **mid-frequency DCT coefficients** within 8×8 blocks. Luminance variance drives adaptive capacity: textured regions hold more data. A residual file enables **perfect reversible data hiding (RDH)**.

---

## Installation

**Requirements:** Python 3.10 or newer.

```bash
# 1. Clone or download the project
git clone https://github.com/yourname/stegovault.git
cd stegovault

# 2. Create a virtual environment
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
2. **Choose a method**: `LSB (Classic)` or `CA-HRD (Advanced)`.
3. *(Optional)* Enter a **password** in the 🔑 field for AES-256-GCM encryption.
4. *(Optional)* Enable **📦 Batch Mode** to embed in multiple images.
5. **Upload a cover image** (PNG or JPG).
6. **Type your secret message** in the text area.
7. Click **🔒 Embed Message**.
8. Download the stego PNG (and `.svr` residual file for CA-HRD).

### Decoding a Message

1. Open the **🔓 Decode** tab.
2. **Choose the matching method** (must match encoding).
3. **Upload the stego PNG** exported by StegoVault.
4. *(CA-HRD only)* Upload the `.svr` residual file for perfect recovery.
5. If the message was encrypted, enter the **password**.
6. Click **🔓 Decode Message**.

> ⚠️ Always use the original **PNG** file. Re-saving as JPEG destroys embedded data.

---

## Security Architecture

### Encryption Flow

```
Password → PBKDF2-HMAC-SHA256 (480,000 iterations, random 16-byte salt)
         → 256-bit AES key
Message  → AES-256-GCM encrypt → ciphertext + 16-byte auth tag
```

**Wire format:** `salt (16 B) ‖ nonce (12 B) ‖ ciphertext + tag`

Total overhead: **44 bytes** per encrypted message.

### Embedded Bitstream Protocol

```
[32 bits: payload length, big-endian] [8 bits: flags] [payload bits…]
```

**Flags byte:** bit 0 = encrypted (1) / plaintext (0); bits 1–7 reserved.

This replaces the old delimiter-based protocol, eliminating:
- Delimiter collision vulnerability
- Fixed search patterns for steganalyzers

### Residual File Format (.svr)

```
b"SVRD" (4 B) │ version (1 B) │ encrypted_flag (1 B) │ body
```

Body contains: `cap_map + correction_bits + orig_pixel_lsbs` (raw binary, no pickle).
When a password is set, the body is AES-256-GCM encrypted.

---

## Technical Deep-Dive

### LSB Algorithm

**Embedding (vectorized):**
```python
flat[:n_bits] = (flat[:n_bits] & 0xFE) | payload_bits
```

No Python loops — pure NumPy array operations. Maximum distortion: ±1 per channel.

**Capacity:** `(H × W × 3 − 40) / 8` bytes (40 = header bits).

### CA-HRD Algorithm

**DCT Transform:** Uses `scipy.fft.dctn/idctn` (modern API, replaces deprecated `fftpack`).

**Content-Aware Capacity:** Per 8×8 block, luminance variance maps to DCT coefficients used:

| Variance | Coefficients/channel | Bits/block (3 ch) |
|---|---|---|
| > 800 | 6 | 18 |
| > 300 | 4 | 12 |
| > 80 | 2 | 6 |
| ≤ 80 | 1 | 3 |

**Residual Correction:** XOR correction bits fix DCT→pixel→DCT rounding errors. Original pixel LSBs enable perfect cover image restoration (RDH).

### Quality Metrics

**PSNR:** `10 · log₁₀(255² / MSE)` dB

**SSIM:** Proper 11×11 Gaussian-windowed implementation matching Wang et al. (2004):
- `C1 = (0.01·255)²`, `C2 = (0.03·255)²`
- Local statistics via `scipy.ndimage.convolve`

---

## Method Comparison

| Property | LSB | CA-HRD |
|---|---|---|
| Embedding domain | Spatial (pixel LSBs) | Frequency (DCT coefficients) |
| Capacity | High (1 bit/channel/pixel) | Adaptive (3–18 bits/block) |
| PSNR | ~51–58 dB | ~46–54 dB |
| SSIM | > 0.999 | > 0.999 |
| Reversibility | ❌ Cover image lost | ✅ Perfect via residual |
| Content-awareness | ❌ Uniform | ✅ Variance-adaptive |
| Encryption | ✅ AES-256-GCM | ✅ AES-256-GCM |
| Extra files | None | `residual.svr` |
| Speed | Very fast (vectorized) | Moderate (block DCT) |

---

## Project Structure

```
stegovault/
├── app.py                  # Streamlit UI (imports from core/)
├── core/
│   ├── __init__.py         # Package exports
│   ├── lsb.py              # Vectorized LSB encode/decode
│   ├── cahrd.py            # DCT-domain CA-HRD encode/decode
│   ├── metrics.py          # PSNR + windowed SSIM + histograms
│   ├── crypto.py           # AES-256-GCM encryption
│   └── utils.py            # Bit conversion, framing, residual I/O
├── tests/
│   ├── test_lsb.py         # LSB round-trip & edge case tests
│   ├── test_cahrd.py       # CA-HRD round-trip & pipeline tests
│   ├── test_metrics.py     # PSNR, SSIM, histogram tests
│   ├── test_crypto.py      # Encryption round-trip & error tests
│   └── test_utils.py       # Bit conversion, framing, residual tests
├── requirements.txt
└── README.md
```

---

## Testing

Run the full test suite:

```bash
python -m pytest tests/ -v
```

**59 tests** covering:
- Encryption: round-trips, wrong password, corruption, overhead
- LSB: round-trips, capacity, Unicode, binary data, visual similarity
- CA-HRD: round-trips with/without residual, serialization pipeline
- Metrics: PSNR identical/different, SSIM windowed, histograms
- Utils: bit conversion, frame protocol, residual I/O

---

## Dependencies

```
streamlit    >= 1.32.0    # Web UI framework
Pillow       >= 10.0.0    # Image I/O
numpy        >= 1.26.0    # Array operations
scipy        >= 1.12.0    # DCT transforms, convolution
cryptography >= 42.0.0    # AES-256-GCM encryption
pytest       >= 8.0.0     # Test framework
```

---

## References

- Cox, I. et al. (2008). *Digital Watermarking and Steganography*. Morgan Kaufmann.
- Tian, J. (2003). Reversible Data Embedding Using a Difference Expansion. *IEEE Trans. CSVT*, 13(8).
- Fridrich, J. et al. (2001). Detecting LSB Steganography. *IEEE Multimedia*, 8(4).
- Wallace, G.K. (1992). The JPEG Still Picture Compression Standard. *IEEE Trans. CE*, 38(1).
- Wang, Z. et al. (2004). Image Quality Assessment: From Error Visibility to Structural Similarity. *IEEE Trans. Image Process.*, 13(4).

---

*StegoVault · LSB + CA-HRD Image Steganography · AES-256-GCM Encrypted · College Project Demo*  
*Built with Streamlit · PIL · NumPy · SciPy · Cryptography*