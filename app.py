"""
StegoVault — LSB + CA-HRD Image Steganography
===============================================
Full-featured Streamlit app with:
  • Encode tab  — hide a secret message (single or batch)
  • Decode tab  — extract a hidden message
  • Method Comparison tab
  • Histogram Analysis tab

Security: optional AES-256-GCM encryption with password.
Protocols: length-prefix framing (no delimiter vulnerability).
Residual:  safe binary .svr format (no pickle).

Author: College Project Demo
"""

import io
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

from core import lsb, cahrd, metrics, utils, crypto, CRYPTO_OVERHEAD

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StegoVault · Hidden Ink",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
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
.hero-wrap { text-align: center; padding: 3rem 0 1.8rem; border-bottom: 1px solid #2a2b2e; margin-bottom: 0.5rem; }
.hero-eyebrow { font-family: 'DM Mono', monospace; font-size: 0.72rem; letter-spacing: 0.28em; text-transform: uppercase; color: #c8a96e; margin-bottom: 0.9rem; }
.hero-title { font-family: 'Playfair Display', Georgia, serif; font-size: clamp(2.4rem, 5vw, 4rem); font-weight: 700; line-height: 1.08; color: #f0ede6; margin: 0; letter-spacing: -0.02em; }
.hero-title em { font-style: italic; color: #c8a96e; }
.hero-sub { font-size: 1rem; color: #8c8a83; margin: 0.9rem auto 0; max-width: 560px; line-height: 1.65; font-weight: 300; }
.section-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.22em; text-transform: uppercase; color: #c8a96e; margin-bottom: 0.55rem; }
.card { background: #16171a; border: 1px solid #262729; border-radius: 12px; padding: 1.6rem 1.8rem; margin-bottom: 1.2rem; }
.banner { border-radius: 8px; padding: 0.72rem 1.1rem; font-size: 0.86rem; display: flex; align-items: center; gap: 0.6rem; margin: 0.8rem 0; line-height: 1.45; }
.banner-warn  { background: #2a2010; border: 1px solid #6b4f10; color: #e0b84a; }
.banner-error { background: #271014; border: 1px solid #6b1020; color: #e04a5a; }
.banner-ok    { background: #0f2417; border: 1px solid #1a6040; color: #4ae09a; }
.banner-info  { background: #111a2a; border: 1px solid #1a3060; color: #4a90e0; }
.banner-purple{ background: #1a1128; border: 1px solid #5a2d8a; color: #c084fc; }
.cap-bar-wrap { margin: 0.7rem 0 0.3rem; }
.cap-bar-bg   { height: 5px; border-radius: 99px; background: #2a2b2e; overflow: hidden; }
.cap-bar-fill { height: 100%; border-radius: 99px; transition: width 0.4s ease; }
.cap-text     { font-family: 'DM Mono', monospace; font-size: 0.70rem; color: #6b6a64; margin-top: 0.3rem; }
.msg-reveal { background: #111214; border: 1.5px solid #1a6040; border-radius: 10px; padding: 1.3rem 1.5rem; margin-top: 1rem; font-family: 'DM Mono', monospace; font-size: 0.84rem; color: #a8e6c8; line-height: 1.7; white-space: pre-wrap; word-break: break-word; max-height: 320px; overflow-y: auto; }
.msg-reveal-label { font-family: 'DM Mono', monospace; font-size: 0.6rem; letter-spacing: 0.22em; text-transform: uppercase; color: #4ae09a; margin-bottom: 0.5rem; }
.metric-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 1rem 0; }
.metric-card { background: #111214; border: 1px solid #1e1f22; border-radius: 10px; padding: 0.9rem 1.1rem; text-align: center; }
.metric-val  { font-family: 'DM Mono', monospace; font-size: 1.3rem; font-weight: 500; color: #c8a96e; }
.metric-lbl  { font-size: 0.68rem; color: #6b6a64; margin-top: 0.2rem; letter-spacing: 0.08em; }
div[data-testid="stFileUploader"] > label { display: none !important; }
div[data-testid="stFileUploader"] > div { border: 1.5px dashed #2e3035 !important; border-radius: 10px !important; background: #111214 !important; padding: 1.5rem !important; transition: border-color 0.2s; text-align: center; }
div[data-testid="stFileUploader"] > div:hover { border-color: #c8a96e !important; }
div[data-testid="stTextArea"] textarea { background: #111214 !important; border: 1.5px solid #2e3035 !important; border-radius: 8px !important; color: #e8e6df !important; font-family: 'DM Mono', monospace !important; font-size: 0.84rem !important; line-height: 1.6 !important; resize: vertical; }
div[data-testid="stTextArea"] textarea:focus { border-color: #c8a96e !important; box-shadow: 0 0 0 3px rgba(200,169,110,0.10) !important; }
div[data-testid="stButton"] > button[kind="primary"] { background: linear-gradient(135deg, #c8a96e 0%, #a07840 100%) !important; color: #0e0f11 !important; font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; font-size: 0.91rem !important; letter-spacing: 0.04em !important; border: none !important; border-radius: 8px !important; padding: 0.65rem 2rem !important; transition: opacity 0.2s, transform 0.15s !important; width: 100%; }
div[data-testid="stButton"] > button[kind="primary"]:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
div[data-testid="stDownloadButton"] > button { background: transparent !important; border: 1.5px solid #c8a96e !important; color: #c8a96e !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; font-size: 0.87rem !important; border-radius: 8px !important; padding: 0.6rem 1.6rem !important; transition: background 0.2s !important; width: 100%; }
div[data-testid="stDownloadButton"] > button:hover { background: rgba(200,169,110,0.10) !important; }
div[data-testid="stTabs"] [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #2a2b2e !important; gap: 0.5rem; margin-bottom: 1.8rem; padding-bottom: 0 !important; }
div[data-testid="stTabs"] [data-baseweb="tab"] { background: transparent !important; border: 1px solid transparent !important; border-radius: 8px 8px 0 0 !important; color: #6b6a64 !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.92rem !important; font-weight: 500 !important; padding: 0.65rem 1.6rem !important; transition: color 0.2s, border-color 0.2s !important; }
div[data-testid="stTabs"] [aria-selected="true"] { color: #c8a96e !important; border-color: #2a2b2e #2a2b2e #0e0f11 !important; background: #0e0f11 !important; }
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }
div[data-testid="stImage"] img { border-radius: 8px; width: 100% !important; object-fit: contain; max-height: 360px; }
.copy-hint { font-family: 'DM Mono', monospace; font-size: 0.66rem; color: #3d3c37; margin-top: 0.4rem; }
.how-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; }
.how-card { background: #111214; border: 1px solid #1e1f22; border-radius: 10px; padding: 1.1rem 1.3rem; }
.how-icon  { font-size: 1.4rem; margin-bottom: 0.4rem; }
.how-title { font-size: 0.81rem; font-weight: 600; color: #e8e6df; margin-bottom: 0.25rem; }
.how-desc  { font-size: 0.77rem; color: #6b6a64; line-height: 1.55; }
.cmp-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 0.8rem; }
.cmp-table th { font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase; color: #6b6a64; padding: 0.5rem 0.8rem; border-bottom: 1px solid #2a2b2e; text-align: left; }
.cmp-table td { padding: 0.55rem 0.8rem; border-bottom: 1px solid #1a1b1e; color: #b8b6af; }
.cmp-table tr:last-child td { border-bottom: none; }
.cmp-table .good { color: #4ae09a; font-weight: 500; }
.cmp-table .mid  { color: #e0b84a; }
.cmp-table .lbl  { color: #e8e6df; font-weight: 500; }
div[data-testid="stTextInput"] input { background: #111214 !important; border: 1.5px solid #2e3035 !important; border-radius: 8px !important; color: #e8e6df !important; font-family: 'DM Mono', monospace !important; font-size: 0.84rem !important; }
div[data-testid="stTextInput"] input:focus { border-color: #c8a96e !important; box-shadow: 0 0 0 3px rgba(200,169,110,0.10) !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

MAX_MESSAGE_CHARS = 50_000


def _pil_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def _capacity_color(ratio: float) -> str:
    if ratio < 0.6:
        return "#4ae09a"
    if ratio < 0.85:
        return "#e0b84a"
    return "#e04a5a"


def _load_image(uploaded) -> tuple:
    if uploaded is None:
        return None, None
    ok, warn = utils.validate_upload(uploaded)
    if not ok and warn:
        return None, warn
    try:
        return Image.open(uploaded), warn  # warn may contain JPEG warning
    except Exception as e:
        return None, f"Could not open image: {e}"


def _effective_capacity(raw_cap: int, use_encryption: bool) -> int:
    """Adjust raw payload capacity for encryption overhead."""
    if use_encryption:
        return max(0, raw_cap - CRYPTO_OVERHEAD)
    return raw_cap


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <div class="hero-eyebrow">🔐 &nbsp; Information Hiding &nbsp;·&nbsp; LSB &amp; CA-HRD Steganography &nbsp;·&nbsp; AES-256 Encrypted</div>
  <h1 class="hero-title">Stego<em>Vault</em></h1>
  <p class="hero-sub">
    Conceal secret messages inside ordinary images — and reveal them again.
    Choose between classic LSB or research-grade CA-HRD. Optionally encrypt with AES-256-GCM.
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_encode, tab_decode, tab_compare, tab_histogram = st.tabs([
    "🔒  Encode — Hide a Message",
    "🔓  Decode — Reveal a Message",
    "📊  Method Comparison",
    "📈  Histogram Analysis",
])

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — ENCODE
# ══════════════════════════════════════════════════════════════════════════════
with tab_encode:

    # ── method selector ──────────────────────────────────────────────────
    st.markdown("""
    <div class="card" style="margin-bottom:1rem;">
      <div class="section-label">Encoding Settings</div>
    </div>
    """, unsafe_allow_html=True)

    enc_col1, enc_col2, enc_col3 = st.columns([2, 1, 1])
    with enc_col1:
        enc_method = st.selectbox(
            "Method",
            options=["LSB (Classic)", "CA-HRD (Advanced – Reversible & Content-Aware)"],
            label_visibility="collapsed", key="enc_method_select",
        )
    with enc_col2:
        enc_password = st.text_input(
            "🔑 Password (optional)", type="password", key="enc_password",
            placeholder="AES-256 encryption",
        )
    with enc_col3:
        batch_mode = st.checkbox("📦 Batch Mode", key="batch_mode")

    is_cahrd = enc_method.startswith("CA-HRD")
    use_enc = bool(enc_password and enc_password.strip())

    if use_enc:
        st.markdown(
            '<div class="banner banner-purple">🔑 <span><strong>AES-256-GCM encryption active.</strong> '
            'Message will be encrypted before embedding. You will need the same password to decode.</span></div>',
            unsafe_allow_html=True)

    if is_cahrd:
        st.markdown("""
        <div class="banner banner-purple">
          🧬 <span><strong>CA-HRD mode active.</strong>
          Uses adaptive DCT-domain embedding with content-aware capacity selection.
          Produces a <em>residual file</em> for mathematically perfect message recovery.
          Higher imperceptibility · Fully reversible.</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
          <div class="section-label">How CA-HRD encoding works</div>
          <div class="how-grid">
            <div class="how-card"><div class="how-icon">🖼️</div><div class="how-title">1 · Upload Cover Image</div>
              <div class="how-desc">Choose any PNG or JPG. Image is processed in 8×8 DCT blocks.</div></div>
            <div class="how-card"><div class="how-icon">🧬</div><div class="how-title">2 · Adaptive DCT Embedding</div>
              <div class="how-desc">Textured blocks hold up to 6 bits per channel in mid-frequency DCT coefficients; smooth areas hold 1–2 bits.</div></div>
            <div class="how-card"><div class="how-icon">📦</div><div class="how-title">3 · Download Both Files</div>
              <div class="how-desc">Save the stego PNG <em>and</em> the residual .svr for perfect 100% recovery.</div></div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="banner banner-info">
          💡 <span><strong>LSB mode active.</strong>
          Hides bits in pixel least-significant bits. Fast, high capacity, but sensitive to any post-processing.</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
          <div class="section-label">How LSB encoding works</div>
          <div class="how-grid">
            <div class="how-card"><div class="how-icon">🖼️</div><div class="how-title">1 · Upload Cover Image</div>
              <div class="how-desc">Choose any PNG or JPG. Larger images can hold longer messages.</div></div>
            <div class="how-card"><div class="how-icon">✍️</div><div class="how-title">2 · Type Secret Message</div>
              <div class="how-desc">Your text is converted to binary and embedded in pixel LSBs.</div></div>
            <div class="how-card"><div class="how-icon">📥</div><div class="how-title">3 · Download Stego Image</div>
              <div class="how-desc">The output PNG looks identical but secretly carries your payload.</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

    enc_left, enc_right = st.columns([1, 1], gap="large")

    with enc_left:
        # ── upload ───────────────────────────────────────────────────────
        st.markdown('<div class="section-label">Step 1 — Cover Image</div>', unsafe_allow_html=True)
        if batch_mode:
            enc_uploads = st.file_uploader(
                "enc_cover", type=["png", "jpg", "jpeg"],
                label_visibility="collapsed", key="enc_uploader_batch",
                accept_multiple_files=True,
            )
        else:
            enc_upload_single = st.file_uploader(
                "enc_cover", type=["png", "jpg", "jpeg"],
                label_visibility="collapsed", key="enc_uploader",
            )
            enc_uploads = [enc_upload_single] if enc_upload_single else []

        cover_images = []
        img_info_list = []
        for up in enc_uploads:
            img, err = _load_image(up)
            if err and not img:
                st.markdown(f'<div class="banner banner-error">⛔ {err}</div>', unsafe_allow_html=True)
            elif img:
                if err:  # JPEG warning
                    st.markdown(f'<div class="banner banner-warn">{err}</div>', unsafe_allow_html=True)
                w, h = img.size
                raw_cap = cahrd.max_capacity(img) if is_cahrd else lsb.max_capacity(img)
                eff_cap = _effective_capacity(raw_cap, use_enc)
                method_tag = "CA-HRD adaptive" if is_cahrd else "LSB"
                cover_images.append(img)
                img_info_list.append({"w": w, "h": h, "max_bytes": eff_cap})
                st.markdown(
                    f'<div class="banner banner-ok">✅ {up.name}: {w}×{h} px &nbsp;·&nbsp; '
                    f'<strong>{method_tag}</strong> capacity ~<strong>{eff_cap:,} bytes</strong></div>',
                    unsafe_allow_html=True)

        if not enc_uploads or not cover_images:
            st.markdown(
                '<div class="banner banner-info">ℹ️ Drag & drop or click '
                '<strong>Browse files</strong> to upload.</div>',
                unsafe_allow_html=True)

        # ── message ──────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Step 2 — Secret Message</div>', unsafe_allow_html=True)
        secret_msg = st.text_area(
            "secret", placeholder="Type your secret message here…",
            height=175, max_chars=MAX_MESSAGE_CHARS,
            label_visibility="collapsed", key="enc_message",
        )

        if secret_msg and cover_images:
            used = len(secret_msg.encode("utf-8"))
            if use_enc:
                used += CRYPTO_OVERHEAD
            min_cap = min(info["max_bytes"] for info in img_info_list) if img_info_list else 1
            ratio = min(used / min_cap, 1.0) if min_cap > 0 else 1.0
            color = _capacity_color(ratio)
            pct = f"{ratio * 100:.1f}"
            st.markdown(f"""
            <div class="cap-bar-wrap"><div class="cap-bar-bg">
                <div class="cap-bar-fill" style="width:{pct}%; background:{color};"></div>
              </div><div class="cap-text">{used:,} / {min_cap:,} bytes &nbsp;({pct}%)</div></div>
            """, unsafe_allow_html=True)
            if ratio >= 1.0:
                st.markdown(
                    '<div class="banner banner-error">⛔ Message may exceed capacity. '
                    'Use a larger image or shorter message.</div>',
                    unsafe_allow_html=True)
        elif secret_msg and not cover_images:
            st.markdown(
                '<div class="banner banner-warn">⚠️ Upload an image to check capacity.</div>',
                unsafe_allow_html=True)

        # ── embed button ─────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Step 3 — Embed</div>', unsafe_allow_html=True)
        embed_clicked = st.button(
            "🔒  Embed Message", type="primary",
            use_container_width=True, key="btn_embed",
        )

    with enc_right:
        st.markdown('<div class="section-label">Preview</div>', unsafe_allow_html=True)
        enc_preview = st.container()

    # ── embed logic ──────────────────────────────────────────────────────
    if embed_clicked:
        if not cover_images:
            with enc_preview:
                st.markdown(
                    '<div class="banner banner-error">⛔ Please upload a cover image first.</div>',
                    unsafe_allow_html=True)
        elif not secret_msg or not secret_msg.strip():
            with enc_preview:
                st.markdown(
                    '<div class="banner banner-error">⛔ Secret message cannot be empty.</div>',
                    unsafe_allow_html=True)
        else:
            # Prepare payload once (shared by all images in batch)
            msg_bytes = secret_msg.encode("utf-8")
            if use_enc:
                payload = crypto.encrypt(msg_bytes, enc_password.strip())
            else:
                payload = msg_bytes

            results = []
            progress_bar = st.progress(0, text="Embedding…")

            for idx, cover_img in enumerate(cover_images):
                try:
                    if is_cahrd:
                        def _prog(p, _i=idx, _n=len(cover_images)):
                            progress_bar.progress(
                                (_i + p) / _n,
                                text=f"Embedding image {_i+1}/{_n}…",
                            )
                        stego_img, cap_map, corr_bits, orig_lsbs = cahrd.encode(
                            cover_img, payload, encrypted=use_enc, progress_cb=_prog,
                        )
                        residual_bytes = utils.serialize_residual(
                            cap_map, corr_bits, orig_lsbs,
                            password=enc_password.strip() if use_enc else None,
                        )
                        results.append({
                            "cover": cover_img, "stego": stego_img,
                            "residual": residual_bytes, "error": None,
                        })
                    else:
                        stego_img = lsb.encode(
                            cover_img, payload, encrypted=use_enc,
                        )
                        progress_bar.progress(
                            (idx + 1) / len(cover_images),
                            text=f"Embedding image {idx+1}/{len(cover_images)}…",
                        )
                        results.append({
                            "cover": cover_img, "stego": stego_img,
                            "residual": None, "error": None,
                        })
                except Exception as exc:
                    results.append({
                        "cover": cover_img, "stego": None,
                        "residual": None, "error": str(exc),
                    })

            progress_bar.progress(1.0, text="Done!")
            st.session_state["enc_results"] = results
            st.session_state["enc_is_cahrd"] = is_cahrd

    # ── display results ──────────────────────────────────────────────────
    results = st.session_state.get("enc_results", [])
    cached_is_cahrd = st.session_state.get("enc_is_cahrd", False)

    with enc_preview:
        if results:
            for r_idx, res in enumerate(results):
                if res["error"]:
                    st.markdown(
                        f'<div class="banner banner-error">⛔ Image {r_idx+1}: {res["error"]}</div>',
                        unsafe_allow_html=True)
                    continue

                cover_img = res["cover"]
                stego_img = res["stego"]

                if len(results) > 1:
                    st.markdown(
                        f'<div class="section-label" style="margin-top:1rem;">Image {r_idx+1}</div>',
                        unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        '<div class="section-label" style="font-size:0.58rem;">Original</div>',
                        unsafe_allow_html=True)
                    st.image(cover_img, use_container_width=True)
                with c2:
                    st.markdown(
                        '<div class="section-label" style="font-size:0.58rem;">Stego Output</div>',
                        unsafe_allow_html=True)
                    st.image(stego_img, use_container_width=True)

                # Metrics
                psnr_val = metrics.compute_psnr(cover_img, stego_img)
                ssim_val = metrics.compute_ssim(cover_img, stego_img)
                stego_bytes = _pil_to_bytes(stego_img, "PNG")
                kb_val = len(stego_bytes) / 1024
                psnr_str = f"{psnr_val:.2f} dB" if psnr_val != float("inf") else "∞ dB"
                st.markdown(f"""
                <div class="metric-row">
                  <div class="metric-card"><div class="metric-val">{psnr_str}</div><div class="metric-lbl">PSNR (quality)</div></div>
                  <div class="metric-card"><div class="metric-val">{ssim_val:.4f}</div><div class="metric-lbl">SSIM (similarity)</div></div>
                  <div class="metric-card"><div class="metric-val">{kb_val:,.1f} KB</div><div class="metric-lbl">Output size</div></div>
                </div>""", unsafe_allow_html=True)

                st.markdown(
                    '<div class="banner banner-ok" style="margin-top:0.5rem;">'
                    '✅ Message embedded successfully! Download below.</div>',
                    unsafe_allow_html=True)

                suffix = f"_{r_idx+1}" if len(results) > 1 else ""

                if cached_is_cahrd and res["residual"]:
                    dl1, dl2 = st.columns(2)
                    with dl1:
                        st.download_button(
                            "📥  Download Stego Image (PNG)",
                            data=stego_bytes,
                            file_name=f"stego_cahrd{suffix}.png",
                            mime="image/png",
                            use_container_width=True,
                            key=f"dl_stego_cahrd_{r_idx}",
                        )
                    with dl2:
                        st.download_button(
                            "🗃️  Download Residual File (.svr)",
                            data=res["residual"],
                            file_name=f"residual{suffix}.svr",
                            mime="application/octet-stream",
                            use_container_width=True,
                            key=f"dl_residual_{r_idx}",
                        )
                    st.markdown(
                        '<div class="banner banner-purple" style="margin-top:0.6rem;">🧬 '
                        '<span><strong>Keep the .svr residual file!</strong> '
                        'It stores DCT coefficient corrections and original pixel LSBs for '
                        '<em>mathematically perfect</em> message recovery. '
                        'Without it, decoding still works but is best-effort.</span></div>',
                        unsafe_allow_html=True)
                else:
                    st.download_button(
                        "📥  Download Stego Image (PNG)",
                        data=stego_bytes,
                        file_name=f"stego_image{suffix}.png",
                        mime="image/png",
                        use_container_width=True,
                        key=f"dl_stego_lsb_{r_idx}",
                    )
                    st.markdown(
                        '<div class="copy-hint">Format: PNG (lossless) &nbsp;·&nbsp; '
                        'Only LSBs modified</div>',
                        unsafe_allow_html=True)

        elif cover_images:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    '<div class="section-label" style="font-size:0.58rem;">Original</div>',
                    unsafe_allow_html=True)
                st.image(cover_images[0], use_container_width=True)
            with c2:
                st.markdown(
                    '<div style="height:190px;display:flex;align-items:center;'
                    'justify-content:center;border:1.5px dashed #2e3035;'
                    'border-radius:10px;color:#3a3b3e;font-size:0.8rem;">'
                    'Stego image appears here</div>',
                    unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="height:250px;display:flex;align-items:center;'
                'justify-content:center;border:1.5px dashed #2e3035;'
                'border-radius:10px;color:#3a3b3e;font-size:0.83rem;">'
                'Upload an image to see preview</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — DECODE
# ══════════════════════════════════════════════════════════════════════════════
with tab_decode:

    st.markdown("""
    <div class="card" style="margin-bottom:1rem;">
      <div class="section-label">Decoding Settings</div>
    </div>""", unsafe_allow_html=True)

    dec_col1, dec_col2 = st.columns([2, 1])
    with dec_col1:
        dec_method = st.selectbox(
            "Decoding Method",
            options=["LSB (Classic)", "CA-HRD (Advanced – Reversible & Content-Aware)"],
            label_visibility="collapsed", key="dec_method_select",
        )
    with dec_col2:
        dec_password = st.text_input(
            "🔑 Password (if encrypted)", type="password", key="dec_password",
            placeholder="Leave blank if none",
        )

    dec_is_cahrd = dec_method.startswith("CA-HRD")

    if dec_is_cahrd:
        st.markdown("""
        <div class="card">
          <div class="section-label">How CA-HRD decoding works</div>
          <div class="how-grid">
            <div class="how-card"><div class="how-icon">📂</div><div class="how-title">1 · Upload Stego Image</div>
              <div class="how-desc">The CA-HRD stego PNG exported by StegoVault.</div></div>
            <div class="how-card"><div class="how-icon">🗃️</div><div class="how-title">2 · Upload Residual (Optional)</div>
              <div class="how-desc">The residual .svr file enables 100% perfect mathematical recovery.</div></div>
            <div class="how-card"><div class="how-icon">💬</div><div class="how-title">3 · Read Secret</div>
              <div class="how-desc">DCT coefficients are read, correction bits applied, and the message decoded.</div></div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
          <div class="section-label">How LSB decoding works</div>
          <div class="how-grid">
            <div class="how-card"><div class="how-icon">📂</div><div class="how-title">1 · Upload Stego Image</div>
              <div class="how-desc">Upload the PNG image that was exported by StegoVault.</div></div>
            <div class="how-card"><div class="how-icon">🔍</div><div class="how-title">2 · Extract LSBs</div>
              <div class="how-desc">The app reads the least significant bit of each pixel channel.</div></div>
            <div class="how-card"><div class="how-icon">💬</div><div class="how-title">3 · Read Secret</div>
              <div class="how-desc">Bits are reassembled into bytes, decoded as UTF-8 text.</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

    dec_left, dec_right = st.columns([1, 1], gap="large")

    with dec_left:
        st.markdown(
            '<div class="section-label">Step 1 — Upload Stego Image</div>',
            unsafe_allow_html=True)
        dec_upload = st.file_uploader(
            "dec_stego", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed", key="dec_uploader",
        )
        stego_in, dec_load_warn = _load_image(dec_upload)

        if dec_load_warn and not stego_in:
            st.markdown(
                f'<div class="banner banner-error">⛔ {dec_load_warn}</div>',
                unsafe_allow_html=True)
        elif stego_in is not None:
            w, h = stego_in.size
            st.markdown(
                f'<div class="banner banner-ok">✅ Image loaded — {w} × {h} px. '
                f'Ready to decode.</div>',
                unsafe_allow_html=True)
            if dec_load_warn:  # JPEG warning
                st.markdown(
                    f'<div class="banner banner-warn">{dec_load_warn}</div>',
                    unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="banner banner-info">ℹ️ Upload the stego PNG '
                'exported by StegoVault.</div>',
                unsafe_allow_html=True)

        # Residual file for CA-HRD
        residual_data = None
        if dec_is_cahrd:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-label">Step 2 — Upload Residual File (Optional)</div>',
                unsafe_allow_html=True)
            residual_upload = st.file_uploader(
                "residual_svr", type=["svr", "npy"],
                label_visibility="collapsed", key="residual_uploader",
                help="Upload .svr residual for perfect recovery.",
            )
            if residual_upload is not None:
                try:
                    raw = residual_upload.read()
                    # Support both new .svr and legacy .npy
                    if raw[:4] == b"SVRD":
                        pw = dec_password.strip() if dec_password else None
                        cap_map, corr_bits, orig_lsbs = utils.deserialize_residual(raw, password=pw)
                        residual_data = (cap_map, corr_bits)
                        st.markdown(
                            '<div class="banner banner-purple">🗃️ Residual loaded — '
                            '<strong>perfect recovery mode enabled.</strong></div>',
                            unsafe_allow_html=True)
                    else:
                        # Legacy .npy format (backward compat)
                        import warnings
                        warnings.filterwarnings("ignore")
                        legacy = np.load(io.BytesIO(raw), allow_pickle=True)
                        cap_map = legacy[0]
                        corr_bits = legacy[1] if len(legacy) > 1 else np.array([], dtype=np.uint8)
                        residual_data = (cap_map, corr_bits)
                        st.markdown(
                            '<div class="banner banner-warn">⚠️ Legacy .npy residual loaded. '
                            'Consider re-encoding with the new .svr format for better security.</div>',
                            unsafe_allow_html=True)
                except Exception as re_err:
                    st.markdown(
                        f'<div class="banner banner-error">⛔ Could not load residual: {re_err}</div>',
                        unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="banner banner-warn">⚠️ No residual uploaded — '
                    'best-effort decoding only. Upload residual for 100% accurate recovery.</div>',
                    unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="banner banner-warn" style="margin-top:0.5rem;">⚠️ '
                '<span>Always use the <strong>PNG</strong> file you downloaded. '
                'JPEG re-saves destroy LSB data.</span></div>',
                unsafe_allow_html=True)

        # Decode button
        st.markdown("<br>", unsafe_allow_html=True)
        step_n = "3" if dec_is_cahrd else "2"
        st.markdown(
            f'<div class="section-label">Step {step_n} — Extract Message</div>',
            unsafe_allow_html=True)
        decode_clicked = st.button(
            "🔓  Decode Message", type="primary",
            use_container_width=True, key="btn_decode",
            disabled=(stego_in is None),
        )

    with dec_right:
        st.markdown(
            '<div class="section-label">Uploaded Image</div>',
            unsafe_allow_html=True)
        if stego_in is not None:
            st.image(stego_in, use_container_width=True)
        else:
            st.markdown(
                '<div style="height:250px;display:flex;align-items:center;'
                'justify-content:center;border:1.5px dashed #2e3035;'
                'border-radius:10px;color:#3a3b3e;font-size:0.83rem;">'
                'Stego image preview appears here</div>',
                unsafe_allow_html=True)

    # ── decode logic ─────────────────────────────────────────────────────
    if decode_clicked and stego_in is not None:
        decode_error = None
        decoded_text = None
        used_perfect = False

        with st.spinner("Reading hidden bits…"):
            try:
                if dec_is_cahrd:
                    cap = residual_data[0] if residual_data else None
                    corr = residual_data[1] if residual_data else None
                    raw_payload, is_encrypted, used_perfect = cahrd.decode(
                        stego_in, cap_map=cap, correction_bits=corr,
                    )
                else:
                    raw_payload, is_encrypted = lsb.decode(stego_in)
                    used_perfect = False

                # Handle decryption
                if is_encrypted:
                    pw = dec_password.strip() if dec_password else None
                    if not pw:
                        decode_error = (
                            "This message is AES-256 encrypted. "
                            "Please provide the password in the password field above."
                        )
                    else:
                        try:
                            raw_payload = crypto.decrypt(raw_payload, pw)
                        except ValueError as ve:
                            decode_error = str(ve)

                if not decode_error:
                    decoded_text = raw_payload.decode("utf-8", errors="replace")
                    st.session_state["decoded_text"] = decoded_text
                    st.session_state["used_perfect"] = used_perfect
                    st.session_state["was_encrypted"] = is_encrypted
                    st.session_state.pop("decode_error", None)
            except Exception as exc:
                decode_error = str(exc)
                st.session_state["decode_error"] = decode_error
                st.session_state.pop("decoded_text", None)

        if decode_error:
            st.session_state["decode_error"] = decode_error

    # ── display results ──────────────────────────────────────────────────
    decoded_text = st.session_state.get("decoded_text")
    used_perfect = st.session_state.get("used_perfect", False)
    was_encrypted = st.session_state.get("was_encrypted", False)
    decode_error = st.session_state.get("decode_error")

    if decode_error:
        st.markdown(
            f'<div class="banner banner-error" style="margin-top:1rem;">'
            f'⛔ {decode_error}</div>',
            unsafe_allow_html=True)

    if decoded_text is not None:
        msg_len = len(decoded_text)
        word_est = len(decoded_text.split())

        if used_perfect:
            st.markdown(
                '<div class="banner banner-purple" style="margin-top:1rem;">🧬 '
                '<strong>Perfect recovery using residual correction (100% accurate).</strong> '
                'Original DCT coefficients were fully restored before reading.</div>',
                unsafe_allow_html=True)

        if was_encrypted:
            st.markdown(
                '<div class="banner banner-ok" style="margin-top:0.5rem;">🔓 '
                '<strong>Message decrypted successfully</strong> (AES-256-GCM verified).</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="banner banner-ok" style="margin-top:1rem;">'
                '✅ Hidden message successfully extracted!</div>',
                unsafe_allow_html=True)

        st.markdown(
            '<div class="msg-reveal-label">Revealed Secret Message</div>',
            unsafe_allow_html=True)
        st.code(decoded_text, language=None)
        st.markdown(
            f'<div class="copy-hint">{msg_len:,} characters &nbsp;·&nbsp; '
            f'~{word_est:,} words &nbsp;·&nbsp; '
            f'{len(decoded_text.encode("utf-8")):,} bytes</div>',
            unsafe_allow_html=True)
        st.download_button(
            label="📄  Download Message as .txt",
            data=decoded_text.encode("utf-8"),
            file_name="decoded_secret.txt",
            mime="text/plain",
            use_container_width=False, key="dl_decoded_txt",
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
        <thead><tr><th>Property</th><th>LSB (Classic)</th><th>CA-HRD (Advanced)</th></tr></thead>
        <tbody>
          <tr><td class="lbl">Domain</td><td>Spatial (pixel values)</td><td class="good">Frequency (DCT coefficients)</td></tr>
          <tr><td class="lbl">Capacity</td><td class="good">High (1 bit per channel)</td><td class="mid">Adaptive (1–6 bits per 8×8 block per channel)</td></tr>
          <tr><td class="lbl">Imperceptibility</td><td class="mid">Good (PSNR ~51 dB)</td><td class="good">Excellent (texture-aware distortion)</td></tr>
          <tr><td class="lbl">Reversibility</td><td>❌ Original image lost</td><td class="good">✅ Perfect via residual file</td></tr>
          <tr><td class="lbl">Content-awareness</td><td>❌ Uniform embedding</td><td class="good">✅ Variance-adaptive per block</td></tr>
          <tr><td class="lbl">Encryption</td><td class="good">✅ AES-256-GCM (optional)</td><td class="good">✅ AES-256-GCM (optional)</td></tr>
          <tr><td class="lbl">Extra files needed</td><td class="good">None</td><td class="mid">residual.svr (small)</td></tr>
          <tr><td class="lbl">Speed</td><td class="good">Very fast (vectorized)</td><td class="mid">Moderate (block DCT processing)</td></tr>
          <tr><td class="lbl">Best use-case</td><td>Large messages, trusted channels</td><td class="good">High-quality covert comm. + forensics</td></tr>
        </tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
      <div class="section-label">CA-HRD Technical Deep-Dive</div>
      <div class="how-grid">
        <div class="how-card"><div class="how-icon">📐</div><div class="how-title">8×8 DCT Blocks</div>
          <div class="how-desc">Following the JPEG standard, the image is divided into non-overlapping 8×8 pixel blocks. Each block is transformed via 2-D Discrete Cosine Transform (DCT). The DC coefficient (top-left) is preserved; embedding occurs in mid/high-frequency coefficients via zigzag scan order.</div></div>
        <div class="how-card"><div class="how-icon">📊</div><div class="how-title">Content-Aware Capacity</div>
          <div class="how-desc">The luminance variance of each block determines how many DCT coefficients are used:<br>• Variance &gt; 800 → 6 coefficients<br>• Variance &gt; 300 → 4 coefficients<br>• Variance &gt; 80  → 2 coefficients<br>• Otherwise → 1 coefficient<br>This ensures minimal perceptual distortion.</div></div>
        <div class="how-card"><div class="how-icon">🔄</div><div class="how-title">Residual Correction</div>
          <div class="how-desc">DCT→pixel→DCT round-trips introduce rounding errors. The residual file stores XOR correction bits for each embedded position, guaranteeing zero-error recovery. It also stores original pixel LSBs for perfect cover image restoration (<em>Reversible Data Hiding</em>).</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
      <div class="section-label">Security Features</div>
      <div class="how-grid">
        <div class="how-card"><div class="how-icon">🔑</div><div class="how-title">AES-256-GCM Encryption</div>
          <div class="how-desc">Messages are optionally encrypted with AES-256 in GCM mode before embedding. Key derivation uses PBKDF2-HMAC-SHA256 with 480,000 iterations and a random 16-byte salt. Even if a steganalyzer detects hidden data, the content is cryptographically secured.</div></div>
        <div class="how-card"><div class="how-icon">📐</div><div class="how-title">Length-Prefix Protocol</div>
          <div class="how-desc">No fixed delimiter — the payload length is encoded in the first 32 bits followed by an 8-bit flags byte. This eliminates delimiter collision vulnerabilities and enables encryption auto-detection.</div></div>
        <div class="how-card"><div class="how-icon">🗃️</div><div class="how-title">Safe Residual Format (.svr)</div>
          <div class="how-desc">Residual files use a custom binary format with a magic header — no Python pickle. The residual body can itself be AES-encrypted when a password is set.</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
      <div class="section-label">References &amp; Background</div>
      <p style="font-size:0.83rem;color:#8c8a83;line-height:1.8;margin:0.4rem 0 0;">
        • <strong>Cox et al.</strong> (2008) — <em>Digital Watermarking and Steganography</em>, Morgan Kaufmann.<br>
        • <strong>Tian, J.</strong> (2003) — "Reversible Data Embedding Using a Difference Expansion", <em>IEEE Trans. Circuits Syst. Video Technol.</em><br>
        • <strong>Fridrich, J. et al.</strong> (2001) — "Detecting LSB Steganography in Color and Grayscale Images", <em>IEEE Multimedia</em>.<br>
        • <strong>Wallace, G.K.</strong> (1992) — "The JPEG Still Picture Compression Standard", <em>IEEE Trans. Consumer Electron.</em><br>
        • <strong>Wang, Z. et al.</strong> (2004) — "Image Quality Assessment: From Error Visibility to Structural Similarity", <em>IEEE Trans. Image Process.</em>
      </p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — HISTOGRAM ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_histogram:
    st.markdown("""
    <div class="card">
      <div class="section-label">Pixel Distribution Analysis</div>
      <p style="font-size:0.87rem;color:#8c8a83;line-height:1.65;margin:0.4rem 0 0;">
        Compare per-channel pixel value histograms before and after embedding.
        Minimal difference indicates high-quality steganography.
      </p>
    </div>
    """, unsafe_allow_html=True)

    hist_col1, hist_col2 = st.columns(2)
    with hist_col1:
        st.markdown(
            '<div class="section-label">Original Image</div>',
            unsafe_allow_html=True)
        hist_orig_upload = st.file_uploader(
            "hist_orig", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed", key="hist_orig_uploader",
        )
    with hist_col2:
        st.markdown(
            '<div class="section-label">Stego Image</div>',
            unsafe_allow_html=True)
        hist_stego_upload = st.file_uploader(
            "hist_stego", type=["png", "jpg", "jpeg"],
            label_visibility="collapsed", key="hist_stego_uploader",
        )

    hist_orig_img, _ = _load_image(hist_orig_upload)
    hist_stego_img, _ = _load_image(hist_stego_upload)

    if hist_orig_img and hist_stego_img:
        orig_hist = metrics.compute_histograms(hist_orig_img)
        stego_hist = metrics.compute_histograms(hist_stego_img)

        channels = [
            ("red", "Red Channel", "#e04a5a"),
            ("green", "Green Channel", "#4ae09a"),
            ("blue", "Blue Channel", "#4a90e0"),
        ]

        for ch_key, ch_name, ch_color in channels:
            st.markdown(
                f'<div class="section-label" style="margin-top:1.5rem;">{ch_name}</div>',
                unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            pixel_values = list(range(256))

            with c1:
                df_orig = pd.DataFrame({
                    "Pixel Value": pixel_values,
                    "Count": orig_hist[ch_key].tolist(),
                })
                st.markdown(
                    '<div style="font-size:0.72rem;color:#6b6a64;margin-bottom:0.3rem;">'
                    'Original</div>',
                    unsafe_allow_html=True)
                st.area_chart(
                    df_orig.set_index("Pixel Value"),
                    color=ch_color,
                    height=180,
                )
            with c2:
                df_stego = pd.DataFrame({
                    "Pixel Value": pixel_values,
                    "Count": stego_hist[ch_key].tolist(),
                })
                st.markdown(
                    '<div style="font-size:0.72rem;color:#6b6a64;margin-bottom:0.3rem;">'
                    'Stego</div>',
                    unsafe_allow_html=True)
                st.area_chart(
                    df_stego.set_index("Pixel Value"),
                    color=ch_color,
                    height=180,
                )

        # Difference histogram
        st.markdown(
            '<div class="section-label" style="margin-top:2rem;">'
            'Pixel Value Difference Distribution</div>',
            unsafe_allow_html=True)
        orig_arr = np.array(hist_orig_img.convert("RGB"), dtype=np.int16)
        stego_arr = np.array(hist_stego_img.convert("RGB"), dtype=np.int16)
        if orig_arr.shape == stego_arr.shape:
            diff = (stego_arr - orig_arr).flatten()
            diff_vals, diff_counts = np.unique(diff, return_counts=True)
            df_diff = pd.DataFrame({
                "Pixel Difference": diff_vals.tolist(),
                "Count": diff_counts.tolist(),
            })
            st.bar_chart(df_diff.set_index("Pixel Difference"), color="#c8a96e", height=220)

            # Stats
            nonzero = np.count_nonzero(diff)
            total = diff.size
            pct_changed = nonzero / total * 100
            st.markdown(f"""
            <div class="metric-row">
              <div class="metric-card"><div class="metric-val">{nonzero:,}</div><div class="metric-lbl">Pixels changed</div></div>
              <div class="metric-card"><div class="metric-val">{pct_changed:.2f}%</div><div class="metric-lbl">Change ratio</div></div>
              <div class="metric-card"><div class="metric-val">{float(np.max(np.abs(diff))):.0f}</div><div class="metric-lbl">Max |difference|</div></div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="banner banner-warn">⚠️ Images have different dimensions. '
                'Cannot compute pixel difference.</div>',
                unsafe_allow_html=True)
    elif hist_orig_img or hist_stego_img:
        st.markdown(
            '<div class="banner banner-info">ℹ️ Upload both images to compare histograms.</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="banner banner-info">ℹ️ Upload an original and stego image to visualise '
            'pixel distribution changes.</div>',
            unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid #1e1f22;padding-top:1.3rem;text-align:center;
            font-size:0.74rem;color:#3d3c37;font-family:'DM Mono',monospace;">
  StegoVault &nbsp;·&nbsp; LSB + CA-HRD Image Steganography &nbsp;·&nbsp; AES-256-GCM Encrypted &nbsp;·&nbsp; College Project Demo<br>
  <span style="color:#1e2022;">Built with Streamlit · PIL · NumPy · SciPy · Cryptography</span>
</div>
""", unsafe_allow_html=True)