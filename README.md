# 🔐 StegoVault — LSB Image Steganography

A polished Streamlit web app for **hiding** and **revealing** secret text messages inside ordinary images using Least Significant Bit (LSB) steganography.

---

## 📁 Folder Structure

```
stego_app/
├── app.py            ← Complete Streamlit app (Encode + Decode tabs)
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## 🚀 Setup & Run (Step-by-Step)

### Step 1 — Navigate into the project folder
```bash
cd stego_app
```

### Step 2 — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Launch the app
```bash
streamlit run app.py
```

Opens at **http://localhost:8501** automatically.

---

## 🎮 How to Use

### 🔒 Encode Tab — Hide a Message
| Step | Action |
|------|--------|
| 1 | Click **Browse files** → upload a PNG or JPG image |
| 2 | Type your secret message in the text area |
| 3 | Watch the capacity bar (green = safe, red = too long) |
| 4 | Click **🔒 Embed Message** |
| 5 | Preview original vs stego image side-by-side |
| 6 | Click **📥 Download Stego Image (PNG)** |

### 🔓 Decode Tab — Reveal a Message
| Step | Action |
|------|--------|
| 1 | Switch to the **Decode** tab |
| 2 | Upload the stego PNG file you downloaded earlier |
| 3 | Click **🔓 Decode Message** |
| 4 | The hidden message appears in the output box |
| 5 | Optionally download the message as a `.txt` file |

> ⚠️ **Always use the PNG file.** JPEG compression rewrites pixel values and destroys the hidden LSB data — decoding will fail.

---

## ⚙️ How LSB Steganography Works

Each pixel has **R, G, B** channels — each an 8-bit value (0–255).
The **Least Significant Bit** (rightmost bit) causes a colour change of ±1 at most.

```
Original R value:  10110110  (182)
Message bit = 1:   10110111  (183)  ← visually identical
```

The secret message is encoded as UTF-8 → binary, written bit-by-bit into pixel LSBs.
A fixed delimiter `|||END|||` marks the end so the decoder knows when to stop.

**Capacity:**
```
max_bytes ≈ (width × height × 3) / 8
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | ≥ 1.32 | Web UI |
| Pillow | ≥ 10.2 | Image I/O |
| numpy | ≥ 1.26 | Fast pixel operations |
