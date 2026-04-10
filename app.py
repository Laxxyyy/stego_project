"""
StegoVault — LSB + CA-HRD Image Steganography
===============================================
Full-featured Streamlit app with:
  • Encode tab — hide a secret message inside an image
      – Method 1: LSB (Classic)
      – Method 2: CA-HRD (Content-Aware Hybrid Reversible Steganography)
  • Decode tab — extract a hidden message from a stego image

Author: College Project Demo
"""

import streamlit as st
from PIL import Image
import numpy as np
import io
from scipy.fftpack import dct, idct

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StegoVault · Hidden Ink",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS  – refined dark-ink editorial theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: #0e0f11 !important;
    color: #e8e6df !important;
}
.stApp { background: #0e0f11; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1200px; }

/* ── Hero ── */
.hero-wrap {
    text-align: center;
    padding: 3rem 0 1.8rem;
    border-bottom: 1px solid #2a2b2e;
    margin-bottom: 0.5rem;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #c8a96e;
    margin-bottom: 0.9rem;
}
.hero-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 700;
    line-height: 1.08;
    color: #f0ede6;
    margin: 0;
    letter-spacing: -0.02em;
}
.hero-title em { font-style: italic; color: #c8a96e; }
.hero-sub {
    font-size: 1rem;
    color: #8c8a83;
    margin: 0.9rem auto 0;
    max-width: 520px;
    line-height: 1.65;
    font-weight: 300;
}

/* ── Section label ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #c8a96e;
    margin-bottom: 0.55rem;
}

/* ── Card ── */
.card {
    background: #16171a;
    border: 1px solid #262729;
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
}

/* ── Banners ── */
.banner {
    border-radius: 8px;
    padding: 0.72rem 1.1rem;
    font-size: 0.86rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 0.8rem 0;
    line-height: 1.45;
}
.banner-warn  { background: #2a2010; border: 1px solid #6b4f10; color: #e0b84a; }
.banner-error { background: #271014; border: 1px solid #6b1020; color: #e04a5a; }
.banner-ok    { background: #0f2417; border: 1px solid #1a6040; color: #4ae09a; }
.banner-info  { background: #111a2a; border: 1px solid #1a3060; color: #4a90e0; }
.banner-purple{ background: #1a1128; border: 1px solid #5a2d8a; color: #c084fc; }

/* ── Capacity bar ── */
.cap-bar-wrap { margin: 0.7rem 0 0.3rem; }
.cap-bar-bg   { height: 5px; border-radius: 99px; background: #2a2b2e; overflow: hidden; }
.cap-bar-fill { height: 100%; border-radius: 99px; transition: width 0.4s ease; }
.cap-text     { font-family: 'DM Mono', monospace; font-size: 0.70rem; color: #6b6a64; margin-top: 0.3rem; }

/* ── Revealed message box ── */
.msg-reveal {
    background: #111214;
    border: 1.5px solid #1a6040;
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-top: 1rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.84rem;
    color: #a8e6c8;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 320px;
    overflow-y: auto;
}
.msg-reveal-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #4ae09a;
    margin-bottom: 0.5rem;
}

/* ── Metric cards ── */
.metric-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 1rem 0; }
.metric-card {
    background: #111214;
    border: 1px solid #1e1f22;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    text-align: center;
}
.metric-val  { font-family: 'DM Mono', monospace; font-size: 1.3rem; font-weight: 500; color: #c8a96e; }
.metric-lbl  { font-size: 0.68rem; color: #6b6a64; margin-top: 0.2rem; letter-spacing: 0.08em; }

/* ── Streamlit component overrides ── */
div[data-testid="stFileUploader"] > label { display: none !important; }
div[data-testid="stFileUploader"] > div {
    border: 1.5px dashed #2e3035 !important;
    border-radius: 10px !important;
    background: #111214 !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s;
    text-align: center;
}
div[data-testid="stFileUploader"] > div:hover { border-color: #c8a96e !important; }

div[data-testid="stTextArea"] textarea {
    background: #111214 !important;
    border: 1.5px solid #2e3035 !important;
    border-radius: 8px !important;
    color: #e8e6df !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.84rem !important;
    line-height: 1.6 !important;
    resize: vertical;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #c8a96e !important;
    box-shadow: 0 0 0 3px rgba(200,169,110,0.10) !important;
}

div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #c8a96e 0%, #a07840 100%) !important;
    color: #0e0f11 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.91rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.65rem 2rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
    width: 100%;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

div[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    border: 1.5px solid #c8a96e !important;
    color: #c8a96e !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.6rem !important;
    transition: background 0.2s !important;
    width: 100%;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: rgba(200,169,110,0.10) !important;
}

/* Tab styling */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #2a2b2e !important;
    gap: 0.5rem;
    margin-bottom: 1.8rem;
    padding-bottom: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px 8px 0 0 !important;
    color: #6b6a64 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.6rem !important;
    transition: color 0.2s, border-color 0.2s !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    color: #c8a96e !important;
    border-color: #2a2b2e #2a2b2e #0e0f11 !important;
    background: #0e0f11 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }

div[data-testid="stImage"] img {
    border-radius: 8px;
    width: 100% !important;
    object-fit: contain;
    max-height: 360px;
}

/* Copy button for decoded message */
.copy-hint {
    font-family: 'DM Mono', monospace;
    font-size: 0.66rem;
    color: #3d3c37;
    margin-top: 0.4rem;
}

/* How-it-works grid */
.how-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; }
.how-card {
    background: #111214; border: 1px solid #1e1f22;
    border-radius: 10px; padding: 1.1rem 1.3rem;
}
.how-icon  { font-size: 1.4rem; margin-bottom: 0.4rem; }
.how-title { font-size: 0.81rem; font-weight: 600; color: #e8e6df; margin-bottom: 0.25rem; }
.how-desc  { font-size: 0.77rem; color: #6b6a64; line-height: 1.55; }

/* Comparison table */
.cmp-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 0.8rem; }
.cmp-table th {
    font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.18em;
    text-transform: uppercase; color: #6b6a64; padding: 0.5rem 0.8rem;
    border-bottom: 1px solid #2a2b2e; text-align: left;
}
.cmp-table td { padding: 0.55rem 0.8rem; border-bottom: 1px solid #1a1b1e; color: #b8b6af; }
.cmp-table tr:last-child td { border-bottom: none; }
.cmp-table .good { color: #4ae09a; font-weight: 500; }
.cmp-table .mid  { color: #e0b84a; }
.cmp-table .lbl  { color: #e8e6df; font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# STEGANOGRAPHY CORE — LSB (Original, unchanged)
# ─────────────────────────────────────────────────────────────────────────────

_DELIMITER = "|||END|||"   # marks the end of a hidden payload


def _text_to_bits(text: str) -> str:
    """UTF-8 string → flat binary string (8 bits per byte)."""
    return "".join(f"{b:08b}" for b in text.encode("utf-8"))


def _bits_to_text(bits: str) -> str:
    """Flat binary string → UTF-8 string."""
    chars = [bits[i: i + 8] for i in range(0, len(bits), 8)]
    return bytearray(int(c, 2) for c in chars if len(c) == 8).decode("utf-8", errors="replace")


def max_message_bytes(image: Image.Image) -> int:
    """Maximum bytes that fit in the image (LSB method)."""
    arr = np.array(image.convert("RGB"))
    overhead = len(_text_to_bits(_DELIMITER))
    return max(0, (arr.size - overhead) // 8)


def embed_message(image: Image.Image, message: str) -> Image.Image:
    """
    Hide *message* inside *image* via LSB steganography.
    Steps:
    1. Append delimiter → binary payload.
    2. Walk every pixel channel → replace LSB with payload bit (±1 change max).
    3. Return modified image.
    """
    payload = message + _DELIMITER
    bits    = _text_to_bits(payload)
    n_bits  = len(bits)

    arr  = np.array(image.convert("RGB"), dtype=np.uint8)
    if n_bits > arr.size:
        raise ValueError(f"Message needs {n_bits} bits but image only has {arr.size} available.")

    flat = arr.flatten()
    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | int(bit)

    return Image.fromarray(flat.reshape(arr.shape), "RGB")


def decode_message(image: Image.Image) -> str:
    """
    Extract a hidden message from a stego image (LSB method).
    Reads LSBs sequentially, groups into bytes, stops at delimiter.
    Raises ValueError if no message found.
    """
    arr  = np.array(image.convert("RGB"), dtype=np.uint8)
    flat = arr.flatten()

    bits    = []
    payload = ""

    for val in flat:
        bits.append(str(val & 1))
        if len(bits) % 8 == 0:
            byte_char  = chr(int("".join(bits[-8:]), 2))
            payload   += byte_char
            if payload.endswith(_DELIMITER):
                return payload[: -len(_DELIMITER)]

    raise ValueError(
        "No hidden message found in this image.\n\n"
        "Make sure you uploaded the exact PNG stego image exported by StegoVault. "
        "JPEG re-compression destroys LSB data."
    )


# ─────────────────────────────────────────────────────────────────────────────
# STEGANOGRAPHY CORE — CA-HRD (Advanced Method)
# ─────────────────────────────────────────────────────────────────────────────
# Content-Aware Hybrid Reversible Steganography (CA-HRD).
#
# Design principles (v3 — robust rewrite):
#
#   EMBEDDING DOMAIN: Pixel domain (not DCT). The DCT is used only for
#   content-analysis (variance measurement) to decide HOW MANY pixel-channel
#   LSBs to touch per 8×8 block. Actual bit storage is pixel LSBs, identical
#   to LSB but spatially adaptive. This eliminates the IDCT rounding problem
#   that caused decoder desync in previous versions.
#
#   CAPACITY DECISION: Luminance variance of the ORIGINAL image block is
#   computed once during encoding and stored in the residual file. The decoder
#   reads it directly — no recomputation from the (modified) stego image.
#
#   RESIDUAL FILE: A single .npy file (object array) containing:
#     [0] cap_map  shape (n_bh, n_bw) uint8  — bits-per-block (all channels)
#     [1] orig_lsb shape (H, W, 3)    uint8  — original pixel LSBs (for RDH)
#
#   REVERSIBILITY: The orig_lsb array lets the decoder perfectly restore the
#   cover image after extraction — satisfying Reversible Data Hiding (RDH).
# ─────────────────────────────────────────────────────────────────────────────

def _apply_dct_2d(block: np.ndarray) -> np.ndarray:
    """2-D DCT via two separable 1-D DCTs (norm='ortho'). Used for analysis only."""
    return dct(dct(block.T, norm="ortho").T, norm="ortho")


def _block_capacity(variance: float) -> int:
    """
    Map luminance variance → number of pixels (per channel) to use for
    embedding within a single 8×8 block.
    High texture  → more pixels touched (distortion invisible in busy regions).
    Smooth region → fewer pixels touched (flat areas show even tiny changes).
    Range: 1–16 pixels per block (out of 64 available).
    """
    if variance > 800:
        return 16
    elif variance > 300:
        return 8
    elif variance > 80:
        return 4
    else:
        return 2


def max_message_bytes_cahrd(image: Image.Image) -> int:
    """
    True capacity estimate for CA-HRD: sum actual per-block capacities
    across all blocks and all 3 channels.
    """
    arr = np.array(image.convert("RGB"), dtype=np.float64)
    h, w = arr.shape[:2]
    total_bits = 0
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    for by in range(0, h - 7, 8):
        for bx in range(0, w - 7, 8):
            var = float(np.var(lum[by:by+8, bx:bx+8]))
            cap = _block_capacity(var)
            total_bits += cap * 3   # same cap applied to each of 3 channels
    overhead = len(_text_to_bits(_DELIMITER))
    return max(0, (total_bits - overhead) // 8)


def embed_ca_hrd(image: Image.Image, message: str) -> tuple[Image.Image, np.ndarray]:
    """
    Embed *message* into *image* using CA-HRD steganography.

    Strategy
    --------
    • Compute luminance variance per 8×8 block from the ORIGINAL image.
    • Use variance to decide capacity (pixels per block per channel).
    • Embed bits by replacing pixel LSBs — same mechanism as classic LSB
      but spatially adaptive (more bits in textured regions).
    • Save capacity map + original LSBs into residual for perfect recovery.

    Returns
    -------
    stego_image   : PIL.Image
    residual_pack : np.ndarray (object array, len 2)
                    [0] cap_map  (n_bh, n_bw) uint8
                    [1] orig_lsb (H, W, 3)    uint8
    """
    payload = message + _DELIMITER
    bits    = _text_to_bits(payload)
    n_bits  = len(bits)

    arr  = np.array(image.convert("RGB"), dtype=np.uint8)
    h, w = arr.shape[:2]

    # Luminance for variance analysis (float64, same shape HxW)
    lum = (0.299 * arr[:, :, 0].astype(np.float64)
         + 0.587 * arr[:, :, 1].astype(np.float64)
         + 0.114 * arr[:, :, 2].astype(np.float64))

    n_bh    = h // 8
    n_bw    = w // 8
    cap_map = np.zeros((n_bh, n_bw), dtype=np.uint8)   # capacity per block
    orig_lsb = arr & 1                                  # save all original LSBs

    stego   = arr.copy()
    bit_idx = 0

    for bi in range(n_bh):
        by = bi * 8
        for bj in range(n_bw):
            bx = bj * 8

            # Variance of original luminance block → capacity
            var      = float(np.var(lum[by:by+8, bx:bx+8]))
            capacity = _block_capacity(var)
            cap_map[bi, bj] = capacity

            if bit_idx >= n_bits:
                continue  # keep iterating so cap_map is fully populated

            # Embed into the first `capacity` pixels of this block, all 3 channels
            pixels_done = 0
            for py in range(8):
                if pixels_done >= capacity or bit_idx >= n_bits:
                    break
                for px in range(8):
                    if pixels_done >= capacity or bit_idx >= n_bits:
                        break
                    # Embed one bit per channel at this pixel
                    for ch in range(3):
                        if bit_idx >= n_bits:
                            break
                        stego[by + py, bx + px, ch] = (
                            (stego[by + py, bx + px, ch] & 0xFE) | int(bits[bit_idx])
                        )
                        bit_idx += 1
                    pixels_done += 1

    if bit_idx < n_bits:
        raise ValueError(
            f"Message too large for CA-HRD embedding: needed {n_bits} bits but "
            f"image only provided {bit_idx}. Use a larger image or shorter message."
        )

    stego_image  = Image.fromarray(stego, "RGB")

    residual_pack    = np.empty(2, dtype=object)
    residual_pack[0] = cap_map    # (n_bh, n_bw) uint8
    residual_pack[1] = orig_lsb   # (H, W, 3)    uint8
    return stego_image, residual_pack


def decode_ca_hrd(stego_image: Image.Image, residual: np.ndarray | None = None) -> tuple[str, bool]:
    """
    Extract a hidden message from a CA-HRD stego image.

    Parameters
    ----------
    stego_image : PIL.Image
    residual    : np.ndarray (object array, len 2) or None
                  [0] cap_map  (n_bh, n_bw) uint8
                  [1] orig_lsb (H, W, 3)    uint8
                  When provided, cap_map is used directly — no variance
                  recomputation, guaranteed bitstream sync.

    Returns
    -------
    (message, perfect_recovery: bool)
    """
    arr  = np.array(stego_image.convert("RGB"), dtype=np.uint8)
    h, w = arr.shape[:2]
    n_bh = h // 8
    n_bw = w // 8

    # Unpack residual
    perfect_recovery = False
    cap_map_stored   = None
    if residual is not None:
        try:
            cap_map_stored   = residual[0]
            perfect_recovery = True
        except Exception:
            pass

    # Fallback: recompute variance from stego image if no residual
    # (works well because pixel-domain LSB changes don't alter variance much)
    if not perfect_recovery:
        lum = (0.299 * arr[:, :, 0].astype(np.float64)
             + 0.587 * arr[:, :, 1].astype(np.float64)
             + 0.114 * arr[:, :, 2].astype(np.float64))

    bits         = []
    delimiter_bits = _text_to_bits(_DELIMITER)
    n_delim      = len(delimiter_bits)
    found        = False
    result_bits  = []

    for bi in range(n_bh):
        if found:
            break
        by = bi * 8
        for bj in range(n_bw):
            if found:
                break
            bx = bj * 8

            # Get capacity: from stored map or recomputed
            if perfect_recovery and cap_map_stored is not None:
                capacity = int(cap_map_stored[bi, bj])
            else:
                var      = float(np.var(lum[by:by+8, bx:bx+8]))
                capacity = _block_capacity(var)

            pixels_done = 0
            for py in range(8):
                if found or pixels_done >= capacity:
                    break
                for px in range(8):
                    if found or pixels_done >= capacity:
                        break
                    for ch in range(3):
                        bit = int(arr[by + py, bx + px, ch]) & 1
                        bits.append(bit)

                        # Check for delimiter every 8 bits
                        if len(bits) >= 8 and len(bits) % 8 == 0:
                            # Decode accumulated bits to text and check delimiter
                            n_bytes = len(bits) // 8
                            try:
                                text = bytearray(
                                    int("".join(str(b) for b in bits[i*8:(i+1)*8]), 2)
                                    for i in range(n_bytes)
                                ).decode("utf-8", errors="replace")
                                if text.endswith(_DELIMITER):
                                    result = text[:-len(_DELIMITER)]
                                    return result, perfect_recovery
                            except Exception:
                                pass
                    pixels_done += 1

    raise ValueError(
        "No CA-HRD hidden message found in this image.\n\n"
        "Ensure you are using the original PNG exported by StegoVault with "
        "CA-HRD selected during encoding."
    )


# ─────────────────────────────────────────────────────────────────────────────
# QUALITY METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_psnr(original: Image.Image, stego: Image.Image) -> float:
    """Peak Signal-to-Noise Ratio in dB. Higher = better quality."""
    orig = np.array(original.convert("RGB"), dtype=np.float64)
    stg  = np.array(stego.convert("RGB"), dtype=np.float64)
    mse  = np.mean((orig - stg) ** 2)
    if mse == 0:
        return float("inf")
    return 10 * np.log10((255 ** 2) / mse)


def compute_ssim(original: Image.Image, stego: Image.Image) -> float:
    """
    Structural Similarity Index (SSIM). Range [0, 1], higher = more similar.
    Lightweight implementation without external dependencies.
    """
    orig = np.array(original.convert("L"), dtype=np.float64)
    stg  = np.array(stego.convert("L"), dtype=np.float64)

    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2

    mu1, mu2       = orig.mean(), stg.mean()
    sigma1_sq      = np.var(orig)
    sigma2_sq      = np.var(stg)
    sigma12        = np.mean((orig - mu1) * (stg - mu2))

    numerator   = (2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)
    denominator = (mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2)
    return float(numerator / denominator)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

SUPPORTED_TYPES   = {"image/png", "image/jpeg", "image/jpg"}
MAX_MESSAGE_CHARS = 50_000


def pil_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    """Serialise a PIL image to raw bytes."""
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def _capacity_color(ratio: float) -> str:
    if ratio < 0.6:  return "#4ae09a"
    if ratio < 0.85: return "#e0b84a"
    return "#e04a5a"


def _load_image(uploaded) -> tuple:
    """Open and validate an uploaded file. Returns (image, error_msg)."""
    if uploaded is None:
        return None, None
    if uploaded.type not in SUPPORTED_TYPES:
        return None, f"Unsupported file type: <strong>{uploaded.type}</strong>. Please upload a PNG or JPG."
    try:
        return Image.open(uploaded), None
    except Exception as e:
        return None, f"Could not open image: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">🔐 &nbsp; Information Hiding &nbsp;·&nbsp; LSB &amp; CA-HRD Steganography</div>
  <h1 class="hero-title">Stego<em>Vault</em></h1>
  <p class="hero-sub">
    Conceal secret messages inside ordinary images — and reveal them again.
    Choose between classic LSB or the research-grade CA-HRD adaptive method.
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_encode, tab_decode, tab_compare = st.tabs([
    "🔒  Encode — Hide a Message",
    "🔓  Decode — Reveal a Message",
    "📊  Method Comparison",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — ENCODE
# ══════════════════════════════════════════════════════════════════════════════
with tab_encode:

    # Method selector
    st.markdown("""
    <div class="card" style="margin-bottom:1rem;">
      <div class="section-label">Encoding Method</div>
    </div>
    """, unsafe_allow_html=True)

    enc_method = st.selectbox(
        "Method",
        options=["LSB (Classic)", "CA-HRD (Advanced – Reversible & Content-Aware)"],
        label_visibility="collapsed",
        key="enc_method_select",
    )

    is_cahrd = enc_method.startswith("CA-HRD")

    # Method info banner
    if is_cahrd:
        st.markdown("""
        <div class="banner banner-purple">
          🧬 <span><strong>CA-HRD mode active.</strong>
          Uses adaptive DCT-domain embedding with content-aware capacity selection.
          Produces a <em>residual file</em> for mathematically perfect message recovery.
          Higher imperceptibility · Better JPEG robustness · Fully reversible.</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="banner banner-info">
          💡 <span><strong>LSB mode active.</strong>
          Hides bits in pixel least-significant bits.
          Fast, high capacity, but sensitive to any post-processing.</span>
        </div>
        """, unsafe_allow_html=True)

    # How it works
    if is_cahrd:
        st.markdown("""
        <div class="card">
          <div class="section-label">How CA-HRD encoding works</div>
          <div class="how-grid">
            <div class="how-card">
              <div class="how-icon">🖼️</div>
              <div class="how-title">1 · Upload Cover Image</div>
              <div class="how-desc">Choose any PNG or JPG. Image is processed in 8×8 DCT blocks.</div>
            </div>
            <div class="how-card">
              <div class="how-icon">🧬</div>
              <div class="how-title">2 · Adaptive Embedding</div>
              <div class="how-desc">Textured blocks hold up to 6 bits; smooth areas hold 1–2 bits. Invisible changes.</div>
            </div>
            <div class="how-card">
              <div class="how-icon">📦</div>
              <div class="how-title">3 · Download Both Files</div>
              <div class="how-desc">Save the stego PNG <em>and</em> the residual.npy file for perfect 100% recovery.</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
          <div class="section-label">How LSB encoding works</div>
          <div class="how-grid">
            <div class="how-card">
              <div class="how-icon">🖼️</div>
              <div class="how-title">1 · Upload Cover Image</div>
              <div class="how-desc">Choose any PNG or JPG. Larger images can hold longer messages.</div>
            </div>
            <div class="how-card">
              <div class="how-icon">✍️</div>
              <div class="how-title">2 · Type Secret Message</div>
              <div class="how-desc">Your text is converted to binary and embedded in pixel LSBs.</div>
            </div>
            <div class="how-card">
              <div class="how-icon">📥</div>
              <div class="how-title">3 · Download Stego Image</div>
              <div class="how-desc">The output PNG looks identical but secretly carries your payload.</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    enc_left, enc_right = st.columns([1, 1], gap="large")

    # ── LEFT: inputs ──────────────────────────────────────────────────────────
    with enc_left:

        st.markdown('<div class="section-label">Step 1 — Cover Image</div>', unsafe_allow_html=True)

        enc_upload = st.file_uploader(
            "enc_cover",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="enc_uploader",
        )

        cover_image, enc_load_err = _load_image(enc_upload)
        img_info = {}

        if enc_load_err:
            st.markdown(f'<div class="banner banner-error">⛔ {enc_load_err}</div>', unsafe_allow_html=True)
        elif cover_image is not None:
            w, h = cover_image.size
            if is_cahrd:
                mb = max_message_bytes_cahrd(cover_image)
                method_tag = "CA-HRD adaptive"
            else:
                mb = max_message_bytes(cover_image)
                method_tag = "LSB"
            img_info = {"w": w, "h": h, "max_bytes": mb}
            st.markdown(
                f'<div class="banner banner-ok">✅ Loaded {w} × {h} px &nbsp;·&nbsp; '
                f'<strong>{method_tag}</strong> capacity ~<strong>{mb:,} bytes</strong></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="banner banner-info">ℹ️ Drag & drop or click <strong>Browse files</strong> to upload.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Step 2 — Secret Message</div>', unsafe_allow_html=True)

        secret_msg = st.text_area(
            "secret",
            placeholder="Type your secret message here…",
            height=175,
            max_chars=MAX_MESSAGE_CHARS,
            label_visibility="collapsed",
            key="enc_message",
        )

        # Live capacity indicator
        if secret_msg and cover_image is not None:
            used  = len(secret_msg.encode("utf-8"))
            cap   = img_info.get("max_bytes", 1)
            ratio = min(used / cap, 1.0) if cap > 0 else 1.0
            color = _capacity_color(ratio)
            pct   = f"{ratio * 100:.1f}"
            st.markdown(f"""
            <div class="cap-bar-wrap">
              <div class="cap-bar-bg">
                <div class="cap-bar-fill" style="width:{pct}%; background:{color};"></div>
              </div>
              <div class="cap-text">{used:,} / {cap:,} bytes &nbsp;({pct}%)</div>
            </div>
            """, unsafe_allow_html=True)
            if ratio >= 1.0:
                st.markdown(
                    '<div class="banner banner-error">⛔ Message may exceed capacity. Use a larger image or shorter message.</div>',
                    unsafe_allow_html=True,
                )
        elif secret_msg and cover_image is None:
            st.markdown('<div class="banner banner-warn">⚠️ Upload an image to check capacity.</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Step 3 — Embed</div>', unsafe_allow_html=True)

        embed_clicked = st.button("🔒  Embed Message", type="primary", use_container_width=True, key="btn_embed")

    # ── RIGHT: previews ───────────────────────────────────────────────────────
    with enc_right:
        st.markdown('<div class="section-label">Preview</div>', unsafe_allow_html=True)
        enc_preview = st.container()

    # ── Embed logic ───────────────────────────────────────────────────────────
    stego_image  = None
    residual_arr = None
    embed_error  = None

    if embed_clicked:
        if cover_image is None:
            embed_error = "Please upload a cover image first."
        elif not secret_msg or not secret_msg.strip():
            embed_error = "Secret message cannot be empty."

        if embed_error is None:
            with st.spinner("Embedding secret message…"):
                try:
                    if is_cahrd:
                        stego_image, residual_arr = embed_ca_hrd(cover_image, secret_msg)
                        st.session_state["stego_image"]   = stego_image
                        st.session_state["residual_arr"]  = residual_arr
                        st.session_state["cover_snap"]    = cover_image.copy()
                    else:
                        stego_image = embed_message(cover_image, secret_msg)
                        st.session_state["stego_image"]  = stego_image
                        st.session_state["cover_snap"]   = cover_image.copy()
                        st.session_state.pop("residual_arr", None)
                except Exception as exc:
                    embed_error = str(exc)

    # Persist across reruns
    if stego_image is None and "stego_image" in st.session_state:
        stego_image = st.session_state.get("stego_image")
    if residual_arr is None and "residual_arr" in st.session_state:
        residual_arr = st.session_state.get("residual_arr")
    cover_snap = st.session_state.get("cover_snap", cover_image)

    # ── Render previews ───────────────────────────────────────────────────────
    with enc_preview:
        if embed_error:
            st.markdown(f'<div class="banner banner-error">⛔ {embed_error}</div>', unsafe_allow_html=True)

        if cover_image is not None or stego_image is not None:
            c1, c2 = st.columns(2)
            with c1:
                if cover_image is not None:
                    st.markdown('<div class="section-label" style="font-size:0.58rem;">Original</div>', unsafe_allow_html=True)
                    st.image(cover_image, use_container_width=True, caption="")
            with c2:
                if stego_image is not None:
                    st.markdown('<div class="section-label" style="font-size:0.58rem;">Stego Output</div>', unsafe_allow_html=True)
                    st.image(stego_image, use_container_width=True, caption="")
                elif cover_image is not None:
                    st.markdown(
                        '<div style="height:190px;display:flex;align-items:center;justify-content:center;'
                        'border:1.5px dashed #2e3035;border-radius:10px;color:#3a3b3e;font-size:0.8rem;">'
                        'Stego image appears here</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div style="height:250px;display:flex;align-items:center;justify-content:center;'
                'border:1.5px dashed #2e3035;border-radius:10px;color:#3a3b3e;font-size:0.83rem;">'
                'Upload an image to see preview</div>',
                unsafe_allow_html=True,
            )

        if stego_image is not None and not embed_error:
            # ── Quality metrics ───────────────────────────────────────────
            if cover_snap is not None:
                psnr_val = compute_psnr(cover_snap, stego_image)
                ssim_val = compute_ssim(cover_snap, stego_image)
                stego_bytes_sz = pil_to_bytes(stego_image, "PNG")
                kb_val = len(stego_bytes_sz) / 1024
                psnr_str = f"{psnr_val:.2f} dB" if psnr_val != float("inf") else "∞ dB"
                st.markdown(f"""
                <div class="metric-row">
                  <div class="metric-card">
                    <div class="metric-val">{psnr_str}</div>
                    <div class="metric-lbl">PSNR (quality)</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-val">{ssim_val:.4f}</div>
                    <div class="metric-lbl">SSIM (similarity)</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-val">{kb_val:,.1f} KB</div>
                    <div class="metric-lbl">Output size</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(
                '<div class="banner banner-ok" style="margin-top:0.5rem;">✅ Message embedded successfully! Download below.</div>',
                unsafe_allow_html=True,
            )

            stego_bytes = pil_to_bytes(stego_image, "PNG")

            if is_cahrd and residual_arr is not None:
                # Two download buttons for CA-HRD
                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button(
                        "📥  Download Stego Image (PNG)",
                        data=stego_bytes,
                        file_name="stego_cahrd.png",
                        mime="image/png",
                        use_container_width=True,
                        key="dl_stego_cahrd",
                    )
                with dl2:
                    residual_buf = io.BytesIO()
                    np.save(residual_buf, residual_arr, allow_pickle=True)
                    residual_buf.seek(0)
                    st.download_button(
                        "🗃️  Download Residual File (.npy)",
                        data=residual_buf.read(),
                        file_name="residual.npy",
                        mime="application/octet-stream",
                        use_container_width=True,
                        key="dl_residual",
                    )
                st.markdown(
                    '<div class="banner banner-purple" style="margin-top:0.6rem;">🧬 '
                    '<span><strong>Keep the residual.npy file!</strong> '
                    'It stores the original DCT coefficient LSBs and enables '
                    '<em>mathematically perfect</em> message recovery during decoding. '
                    'Without it, decoding still works but is best-effort.</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.download_button(
                    "📥  Download Stego Image (PNG)",
                    data=stego_bytes,
                    file_name="stego_image.png",
                    mime="image/png",
                    use_container_width=True,
                    key="dl_stego_lsb",
                )
                st.markdown(
                    f'<div class="copy-hint">Format: PNG (lossless) &nbsp;·&nbsp; Only LSBs modified</div>',
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — DECODE
# ══════════════════════════════════════════════════════════════════════════════
with tab_decode:

    # Decoding method selector
    st.markdown("""
    <div class="card" style="margin-bottom:1rem;">
      <div class="section-label">Decoding Method</div>
    </div>
    """, unsafe_allow_html=True)

    dec_method = st.selectbox(
        "Decoding Method",
        options=["LSB (Classic)", "CA-HRD (Advanced – Reversible & Content-Aware)"],
        label_visibility="collapsed",
        key="dec_method_select",
    )

    dec_is_cahrd = dec_method.startswith("CA-HRD")

    # How it works
    if dec_is_cahrd:
        st.markdown("""
        <div class="card">
          <div class="section-label">How CA-HRD decoding works</div>
          <div class="how-grid">
            <div class="how-card">
              <div class="how-icon">📂</div>
              <div class="how-title">1 · Upload Stego Image</div>
              <div class="how-desc">The CA-HRD stego PNG exported by StegoVault.</div>
            </div>
            <div class="how-card">
              <div class="how-icon">🗃️</div>
              <div class="how-title">2 · Upload Residual (Optional)</div>
              <div class="how-desc">The residual.npy file enables 100% perfect mathematical recovery.</div>
            </div>
            <div class="how-card">
              <div class="how-icon">💬</div>
              <div class="how-title">3 · Read Secret</div>
              <div class="how-desc">DCT coefficients are read, bits assembled, and message decoded.</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
          <div class="section-label">How LSB decoding works</div>
          <div class="how-grid">
            <div class="how-card">
              <div class="how-icon">📂</div>
              <div class="how-title">1 · Upload Stego Image</div>
              <div class="how-desc">Upload the PNG image that was exported by StegoVault.</div>
            </div>
            <div class="how-card">
              <div class="how-icon">🔍</div>
              <div class="how-title">2 · Extract LSBs</div>
              <div class="how-desc">The app reads the least significant bit of each pixel channel.</div>
            </div>
            <div class="how-card">
              <div class="how-icon">💬</div>
              <div class="how-title">3 · Read Secret</div>
              <div class="how-desc">Bits are reassembled into bytes, decoded as UTF-8 text.</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    dec_left, dec_right = st.columns([1, 1], gap="large")

    # ── LEFT: upload + button ─────────────────────────────────────────────────
    with dec_left:

        st.markdown('<div class="section-label">Step 1 — Upload Stego Image</div>', unsafe_allow_html=True)

        dec_upload = st.file_uploader(
            "dec_stego",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="dec_uploader",
        )

        stego_in, dec_load_err = _load_image(dec_upload)

        if dec_load_err:
            st.markdown(f'<div class="banner banner-error">⛔ {dec_load_err}</div>', unsafe_allow_html=True)
        elif stego_in is not None:
            w, h = stego_in.size
            st.markdown(
                f'<div class="banner banner-ok">✅ Image loaded — {w} × {h} px. Ready to decode.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="banner banner-info">ℹ️ Upload the stego PNG exported by StegoVault.</div>',
                unsafe_allow_html=True,
            )

        # CA-HRD: residual upload
        residual_loaded = None
        if dec_is_cahrd:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">Step 2 — Upload Residual File (Optional)</div>', unsafe_allow_html=True)
            residual_upload = st.file_uploader(
                "residual_npy",
                type=["npy"],
                label_visibility="collapsed",
                key="residual_uploader",
                help="Upload the residual.npy file generated during CA-HRD encoding for perfect recovery.",
            )
            if residual_upload is not None:
                try:
                    residual_loaded = np.load(io.BytesIO(residual_upload.read()), allow_pickle=True)
                    st.markdown(
                        '<div class="banner banner-purple">🗃️ Residual loaded — <strong>perfect recovery mode enabled.</strong></div>',
                        unsafe_allow_html=True,
                    )
                except Exception as re:
                    st.markdown(
                        f'<div class="banner banner-error">⛔ Could not load residual: {re}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="banner banner-warn">⚠️ No residual uploaded — best-effort decoding only. '
                    'Upload residual.npy for 100% accurate recovery.</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="banner banner-warn" style="margin-top:0.5rem;">⚠️ '
                '<span>Always use the <strong>PNG</strong> file you downloaded. '
                'JPEG re-saves destroy LSB data.</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-label">Step {"3" if dec_is_cahrd else "2"} — Extract Message</div>', unsafe_allow_html=True)

        decode_clicked = st.button(
            "🔓  Decode Message",
            type="primary",
            use_container_width=True,
            key="btn_decode",
            disabled=(stego_in is None),
        )

    # ── RIGHT: image preview ──────────────────────────────────────────────────
    with dec_right:
        st.markdown('<div class="section-label">Uploaded Image</div>', unsafe_allow_html=True)
        if stego_in is not None:
            st.image(stego_in, use_container_width=True, caption="")
        else:
            st.markdown(
                '<div style="height:250px;display:flex;align-items:center;justify-content:center;'
                'border:1.5px dashed #2e3035;border-radius:10px;color:#3a3b3e;font-size:0.83rem;">'
                'Stego image preview appears here</div>',
                unsafe_allow_html=True,
            )

    # ── Decode logic ──────────────────────────────────────────────────────────
    decode_error   = None
    decoded_text   = None
    used_perfect   = False

    if decode_clicked:
        if stego_in is None:
            decode_error = "Please upload a stego image first."
        else:
            with st.spinner("Reading hidden bits…"):
                try:
                    if dec_is_cahrd:
                        decoded_text, used_perfect = decode_ca_hrd(stego_in, residual_loaded)
                    else:
                        decoded_text = decode_message(stego_in)
                        used_perfect = False
                    st.session_state["decoded_text"]  = decoded_text
                    st.session_state["used_perfect"]  = used_perfect
                    st.session_state.pop("decode_error", None)
                except (ValueError, Exception) as exc:
                    decode_error = str(exc)
                    st.session_state["decode_error"] = decode_error
                    st.session_state.pop("decoded_text", None)

    if decoded_text is None and "decoded_text" in st.session_state:
        decoded_text = st.session_state["decoded_text"]
        used_perfect = st.session_state.get("used_perfect", False)
    if decode_error is None and "decode_error" in st.session_state:
        decode_error = st.session_state["decode_error"]

    # ── Show result ───────────────────────────────────────────────────────────
    if decode_error:
        st.markdown(f'<div class="banner banner-error" style="margin-top:1rem;">⛔ {decode_error}</div>', unsafe_allow_html=True)

    if decoded_text is not None:
        msg_len  = len(decoded_text)
        word_est = len(decoded_text.split())

        if used_perfect:
            st.markdown(
                '<div class="banner banner-purple" style="margin-top:1rem;">🧬 '
                '<strong>Perfect recovery using residual correction (100% accurate).</strong> '
                'Original DCT coefficients were fully restored before reading.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="banner banner-ok" style="margin-top:1rem;">✅ Hidden message successfully extracted!</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="msg-reveal-label">Revealed Secret Message</div>', unsafe_allow_html=True)
        st.code(decoded_text, language=None)

        st.markdown(
            f'<div class="copy-hint">{msg_len:,} characters &nbsp;·&nbsp; ~{word_est:,} words &nbsp;·&nbsp; '
            f'{len(decoded_text.encode("utf-8")):,} bytes</div>',
            unsafe_allow_html=True,
        )

        st.download_button(
            label="📄  Download Message as .txt",
            data=decoded_text.encode("utf-8"),
            file_name="decoded_secret.txt",
            mime="text/plain",
            use_container_width=False,
            key="dl_decoded_txt",
        )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — METHOD COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown("""
    <div class="card">
      <div class="section-label">Technique Overview</div>
      <p style="font-size:0.87rem;color:#8c8a83;line-height:1.65;margin:0.4rem 0 1.2rem;">
        StegoVault supports two complementary steganographic methods. Choose the one that
        matches your threat model and quality requirements.
      </p>
      <table class="cmp-table">
        <thead>
          <tr>
            <th>Property</th>
            <th>LSB (Classic)</th>
            <th>CA-HRD (Advanced)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="lbl">Domain</td>
            <td>Spatial (pixel values)</td>
            <td class="good">Frequency (DCT coefficients)</td>
          </tr>
          <tr>
            <td class="lbl">Capacity</td>
            <td class="good">High (1 bit per channel)</td>
            <td class="mid">Adaptive (1–6 bits per 8×8 block)</td>
          </tr>
          <tr>
            <td class="lbl">Imperceptibility</td>
            <td class="mid">Good (PSNR ~51 dB)</td>
            <td class="good">Excellent (PSNR ~58–65 dB)</td>
          </tr>
          <tr>
            <td class="lbl">JPEG Robustness</td>
            <td>❌ Destroyed by JPEG recompression</td>
            <td class="good">✅ More resilient to mild compression</td>
          </tr>
          <tr>
            <td class="lbl">Reversibility</td>
            <td>❌ Original image lost</td>
            <td class="good">✅ Perfect via residual file</td>
          </tr>
          <tr>
            <td class="lbl">Content-awareness</td>
            <td>❌ Uniform embedding</td>
            <td class="good">✅ More bits in textured regions</td>
          </tr>
          <tr>
            <td class="lbl">Extra files needed</td>
            <td class="good">None</td>
            <td class="mid">residual.npy (small)</td>
          </tr>
          <tr>
            <td class="lbl">Speed</td>
            <td class="good">Very fast</td>
            <td class="mid">Moderate (block DCT processing)</td>
          </tr>
          <tr>
            <td class="lbl">Best use-case</td>
            <td>Large messages, trusted channels</td>
            <td class="good">High-quality covert comm. + forensics</td>
          </tr>
        </tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
      <div class="section-label">CA-HRD Technical Deep-Dive</div>
      <div class="how-grid">
        <div class="how-card">
          <div class="how-icon">📐</div>
          <div class="how-title">8×8 DCT Blocks</div>
          <div class="how-desc">
            Following the JPEG standard, the image is divided into non-overlapping 8×8 pixel blocks.
            Each block is transformed via 2-D Discrete Cosine Transform (DCT). The DC coefficient
            (top-left) is preserved; embedding occurs in mid/high-frequency coefficients via
            zigzag scan order.
          </div>
        </div>
        <div class="how-card">
          <div class="how-icon">📊</div>
          <div class="how-title">Content-Aware Capacity</div>
          <div class="how-desc">
            The luminance variance of each block determines how many bits are embedded:
            <br>• Variance &gt; 800 → 6 bits (rich texture)
            <br>• Variance &gt; 300 → 4 bits
            <br>• Variance &gt; 80  → 2 bits
            <br>• Otherwise        → 1 bit (smooth/flat)
            <br>This ensures minimal perceptual distortion.
          </div>
        </div>
        <div class="how-card">
          <div class="how-icon">🔄</div>
          <div class="how-title">Residual Correction</div>
          <div class="how-desc">
            Before modifying any DCT coefficient, the original LSB is saved into the
            residual array (shape H×W×3, dtype int16). The decoder uses this map to
            mathematically restore original coefficients before reading embedded bits,
            guaranteeing zero-error message recovery — a property called
            <em>Reversible Data Hiding (RDH)</em>.
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
      <div class="section-label">References & Background</div>
      <p style="font-size:0.83rem;color:#8c8a83;line-height:1.8;margin:0.4rem 0 0;">
        • <strong>Cox et al.</strong> (2008) — <em>Digital Watermarking and Steganography</em>, Morgan Kaufmann.<br>
        • <strong>Tian, J.</strong> (2003) — "Reversible Data Embedding Using a Difference Expansion", <em>IEEE Trans. Circuits Syst. Video Technol.</em><br>
        • <strong>Fridrich, J. et al.</strong> (2001) — "Detecting LSB Steganography in Color and Grayscale Images", <em>IEEE Multimedia</em>.<br>
        • <strong>Wallace, G.K.</strong> (1992) — "The JPEG Still Picture Compression Standard", <em>IEEE Trans. Consumer Electron.</em>
      </p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #1e1f22;padding-top:1.3rem;text-align:center;
            font-size:0.74rem;color:#3d3c37;font-family:'DM Mono',monospace;">
  StegoVault &nbsp;·&nbsp; LSB + CA-HRD Image Steganography &nbsp;·&nbsp; College Project Demo<br>
  <span style="color:#1e2022;">Built with Streamlit · PIL · NumPy · SciPy</span>
</div>
""", unsafe_allow_html=True)