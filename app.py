"""
StegoVault — LSB Image Steganography
======================================
Full-featured Streamlit app with:
  • Encode tab — hide a secret message inside an image
  • Decode tab — extract a hidden message from a stego image

Author: College Project Demo
"""

import streamlit as st
from PIL import Image
import numpy as np
import io

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
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# STEGANOGRAPHY CORE
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
    """
    Maximum bytes that fit in the image.
    Formula: (total channel values) / 8  −  delimiter bit overhead.
    """
    arr = np.array(image.convert("RGB"))
    overhead = len(_text_to_bits(_DELIMITER))
    return max(0, (arr.size - overhead) // 8)


def embed_message(image: Image.Image, message: str) -> Image.Image:
    """
    Hide *message* inside *image* via LSB steganography.

    Steps
    -----
    1. Append a fixed delimiter so the decoder knows where the message ends.
    2. Convert payload → binary string.
    3. Walk every pixel channel and replace its LSB with the next payload bit.
       The change is at most ±1 per channel — imperceptible to human eyes.
    4. Return the modified image.
    """
    payload = message + _DELIMITER
    bits    = _text_to_bits(payload)
    n_bits  = len(bits)

    arr  = np.array(image.convert("RGB"), dtype=np.uint8)
    if n_bits > arr.size:
        raise ValueError(f"Message needs {n_bits} bits but image only has {arr.size} available.")

    flat = arr.flatten()
    for i, bit in enumerate(bits):
        flat[i] = (flat[i] & 0xFE) | int(bit)   # clear LSB, set to payload bit

    return Image.fromarray(flat.reshape(arr.shape), "RGB")


def decode_message(image: Image.Image) -> str:
    """
    Extract a hidden message from a stego image.

    Steps
    -----
    1. Read the LSB of every channel value sequentially.
    2. Group bits into bytes; decode as UTF-8.
    3. Stop as soon as the delimiter sequence is found.
    4. Return the payload without the delimiter.

    Raises ValueError if no hidden message is detected.
    """
    arr  = np.array(image.convert("RGB"), dtype=np.uint8)
    flat = arr.flatten()

    bits    = []
    payload = ""

    for val in flat:
        bits.append(str(val & 1))
        if len(bits) % 8 == 0:
            # Decode last byte
            byte_char  = chr(int("".join(bits[-8:]), 2))
            payload   += byte_char
            # Check whether we've reached the end marker
            if payload.endswith(_DELIMITER):
                return payload[: -len(_DELIMITER)]

    raise ValueError(
        "No hidden message found in this image.\n\n"
        "Make sure you uploaded the exact PNG stego image exported by StegoVault. "
        "JPEG re-compression destroys LSB data."
    )


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

SUPPORTED_TYPES  = {"image/png", "image/jpeg", "image/jpg"}
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


def _load_image(uploaded) -> tuple[Image.Image | None, str | None]:
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
  <div class="hero-eyebrow">🔐 &nbsp; Information Hiding &nbsp;·&nbsp; LSB Steganography</div>
  <h1 class="hero-title">Stego<em>Vault</em></h1>
  <p class="hero-sub">
    Conceal secret messages inside ordinary images — and reveal them again.
    Completely invisible to the naked eye.
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_encode, tab_decode = st.tabs(["🔒  Encode — Hide a Message", "🔓  Decode — Reveal a Message"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — ENCODE
# ══════════════════════════════════════════════════════════════════════════════
with tab_encode:

    # How it works
    st.markdown("""
    <div class="card">
      <div class="section-label">How encoding works</div>
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
            mb   = max_message_bytes(cover_image)
            img_info = {"w": w, "h": h, "max_bytes": mb}
            st.markdown(
                f'<div class="banner banner-ok">✅ Loaded {w} × {h} px &nbsp;·&nbsp; capacity <strong>{mb:,} bytes</strong></div>',
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
                    '<div class="banner banner-error">⛔ Message exceeds capacity. Use a larger image or shorter message.</div>',
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
    stego_image = None
    embed_error = None

    if embed_clicked:
        if cover_image is None:
            embed_error = "Please upload a cover image first."
        elif not secret_msg or not secret_msg.strip():
            embed_error = "Secret message cannot be empty."
        else:
            used = len(secret_msg.encode("utf-8"))
            cap  = img_info.get("max_bytes", 0)
            if used > cap:
                embed_error = (
                    f"Message ({used:,} bytes) exceeds image capacity ({cap:,} bytes). "
                    "Use a larger image or a shorter message."
                )

        if embed_error is None:
            with st.spinner("Embedding secret message…"):
                try:
                    stego_image = embed_message(cover_image, secret_msg)
                    st.session_state["stego_image"] = stego_image
                except Exception as exc:
                    embed_error = str(exc)

    # Persist across reruns
    if "stego_image" in st.session_state:
        stego_image = st.session_state["stego_image"]

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
            st.markdown(
                '<div class="banner banner-ok" style="margin-top:1rem;">✅ Message embedded! Download your stego image below.</div>',
                unsafe_allow_html=True,
            )
            stego_bytes  = pil_to_bytes(stego_image, "PNG")
            stego_kb     = len(stego_bytes) / 1024
            st.download_button(
                "📥  Download Stego Image (PNG)",
                data=stego_bytes,
                file_name="stego_image.png",
                mime="image/png",
                use_container_width=True,
            )
            st.markdown(
                f'<div class="copy-hint">Output size: {stego_kb:,.1f} KB &nbsp;·&nbsp; '
                'Format: PNG (lossless) &nbsp;·&nbsp; Only LSBs modified</div>',
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — DECODE
# ══════════════════════════════════════════════════════════════════════════════
with tab_decode:

    # How it works
    st.markdown("""
    <div class="card">
      <div class="section-label">How decoding works</div>
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
          <div class="how-desc">Bits are reassembled into bytes, decoded as UTF-8 text, and shown to you.</div>
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

        # Important warning about JPEG
        st.markdown(
            '<div class="banner banner-warn" style="margin-top:0.5rem;">⚠️ '
            '<span>Always use the <strong>PNG</strong> file you downloaded. '
            'JPEG re-saves destroy LSB data and decoding will fail.</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Step 2 — Extract Message</div>', unsafe_allow_html=True)

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

    if decode_clicked:
        if stego_in is None:
            decode_error = "Please upload a stego image first."
        else:
            with st.spinner("Reading hidden bits…"):
                try:
                    decoded_text = decode_message(stego_in)
                    # Persist so result survives Streamlit reruns
                    st.session_state["decoded_text"] = decoded_text
                    # Clear any old error
                    st.session_state.pop("decode_error", None)
                except ValueError as ve:
                    decode_error = str(ve)
                    st.session_state["decode_error"] = decode_error
                    st.session_state.pop("decoded_text", None)
                except Exception as exc:
                    decode_error = f"Unexpected error: {exc}"
                    st.session_state["decode_error"] = decode_error
                    st.session_state.pop("decoded_text", None)

    # Persist results across reruns (Streamlit re-runs on every widget interaction)
    if decoded_text is None and "decoded_text" in st.session_state:
        decoded_text = st.session_state["decoded_text"]
    if decode_error is None and "decode_error" in st.session_state:
        decode_error = st.session_state["decode_error"]

    # ── Show result ───────────────────────────────────────────────────────────
    # Place the result section below the two columns (full width)
    if decode_error:
        st.markdown(f'<div class="banner banner-error" style="margin-top:1rem;">⛔ {decode_error}</div>', unsafe_allow_html=True)

    if decoded_text is not None:
        msg_len   = len(decoded_text)
        word_est  = len(decoded_text.split())

        st.markdown(
            '<div class="banner banner-ok" style="margin-top:1rem;">✅ Hidden message successfully extracted!</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="msg-reveal-label">Revealed Secret Message</div>', unsafe_allow_html=True)
        # Show the message in a styled read-only code box
        st.code(decoded_text, language=None)

        # Stats row
        st.markdown(
            f'<div class="copy-hint">{msg_len:,} characters &nbsp;·&nbsp; ~{word_est:,} words &nbsp;·&nbsp; '
            f'{len(decoded_text.encode("utf-8")):,} bytes</div>',
            unsafe_allow_html=True,
        )

        # Offer the message as a downloadable text file
        st.download_button(
            label="📄  Download Message as .txt",
            data=decoded_text.encode("utf-8"),
            file_name="decoded_secret.txt",
            mime="text/plain",
            use_container_width=False,
            key="dl_decoded_txt",
        )


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #1e1f22;padding-top:1.3rem;text-align:center;
            font-size:0.74rem;color:#3d3c37;font-family:'DM Mono',monospace;">
  StegoVault &nbsp;·&nbsp; LSB Image Steganography &nbsp;·&nbsp; College Project Demo<br>
  <span style="color:#1e2022;">Built with Streamlit · PIL · NumPy</span>
</div>
""", unsafe_allow_html=True)