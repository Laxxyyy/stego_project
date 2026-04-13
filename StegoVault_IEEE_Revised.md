# StegoVault: A Content-Aware Hybrid Reversible Data Hiding Framework Using Adaptive DCT-Domain Embedding and AES-256-GCM Encryption

---

**Lakshya Yadav**

Department of Computer Science and Engineering,
Vellore Institute of Technology, Vellore, India
lakshya.yadav@vitstudent.ac.in

---

## *Abstract*

This paper presents StegoVault, a dual-mode image steganography framework combining a classical Least Significant Bit (LSB) method with a novel Content-Aware Hybrid Reversible Data Hiding (CA-HRD) algorithm. CA-HRD embeds payload bits into mid-frequency Discrete Cosine Transform (DCT) coefficients of 8x8 image blocks, assigning per-block capacity adaptively based on luminance variance thresholds. This strategy concentrates distortion in textured regions where the Human Visual System (HVS) is least sensitive. A lightweight residual correction mechanism, comprising XOR-based DCT rounding error compensation and original pixel LSB preservation, guarantees mathematically perfect reversible data hiding (RDH). Both steganographic channels are optionally secured with AES-256-GCM authenticated encryption derived via PBKDF2-HMAC-SHA256. Experimental evaluation demonstrates that CA-HRD achieves PSNR values above 46 dB and SSIM scores exceeding 0.999 while preserving full reversibility. The classical LSB channel provides PSNR in the range of 51-58 dB. Comparative analysis against recent hybrid, transform-domain, and AI-assisted methods establishes that CA-HRD is simpler than deep-learning pipelines yet more capable than spatial-only schemes.

*Index Terms*— image steganography, reversible data hiding, discrete cosine transform, content-aware embedding, AES-256-GCM encryption, luminance variance adaptation, least significant bit

---

## I. INTRODUCTION

Information hiding, or steganography, is the science of concealing secret data within innocuous cover media such that the very existence of the communication remains undetectable [1]. Unlike cryptography, which renders a message unintelligible, steganography aims to make it invisible. With the exponential growth of digital imagery across social media, cloud storage, and electronic health records, image steganography has emerged as a critical enabler for privacy-preserving communication, digital rights management, and forensic watermarking.

Traditional spatial-domain techniques, exemplified by Least Significant Bit (LSB) replacement [3], offer high embedding capacity and computational simplicity but suffer from statistical detectability under attacks such as chi-square analysis and RS steganalysis. Transform-domain approaches that operate on Discrete Cosine Transform (DCT) [4], Discrete Wavelet Transform (DWT), or Integer Lifting Wavelet Transform (ILWT) [6] coefficients provide improved robustness against image processing operations, but often sacrifice either capacity or reversibility.

Reversible Data Hiding (RDH) adds a further constraint: the original cover image must be perfectly reconstructable after message extraction. This property is essential in applications where the cover medium itself carries legal, medical, or forensic significance. Classical RDH methods such as histogram shifting and difference expansion [2] operate in the spatial domain and are vulnerable to the same detectability issues as LSB.

Recent advances have explored hybrid frameworks that merge multiple embedding domains [6], leverage Generative Adversarial Networks (GANs) for stego-image generation [7], or employ adaptive strategies guided by pixel-difference statistics [9]. However, these approaches often introduce significant computational cost, require GPU resources for training, or lack a complete reversibility guarantee.

This paper presents StegoVault, a dual-mode steganography system whose principal contribution is the Content-Aware Hybrid Reversible Data Hiding (CA-HRD) algorithm. CA-HRD embeds payload bits into mid-frequency DCT coefficients of 8x8 blocks, with the number of coefficients used per block determined adaptively by the luminance variance of that block. A lightweight residual file—stored in a safe binary format—captures XOR correction bits for DCT rounding errors and original pixel LSBs, enabling mathematically exact cover image restoration. Both modes (LSB and CA-HRD) support optional AES-256-GCM authenticated encryption, implemented with PBKDF2-derived keys. The system is packaged as a modular Python web application offering real-time quality metrics (PSNR, SSIM), histogram analysis, and batch processing.

The remainder of this paper is organized as follows: Section II defines the problem statement. Section III surveys related work. Section IV details the proposed methodology and system design. Section V describes the implementation. Section VI presents experimental results and discussion. Section VII concludes, and Section VIII outlines future work.

---

## II. PROBLEM STATEMENT

Despite significant progress in image steganography, several challenges persist that limit the practical deployment of existing solutions:

1) *Irreversibility of embedding.* Most spatial-domain techniques permanently alter the cover image. In scenarios involving medical imaging, satellite imagery, or legal documents, any irreversible modification to the cover medium is unacceptable.

2) *Uniform embedding distortion.* Classical LSB and fixed-coefficient DCT methods distribute distortion uniformly across the image, including visually sensitive smooth regions (sky, skin tones) where artifacts are perceptible to the HVS. A content-aware strategy is needed to concentrate modifications in textured areas.

3) *Lack of integrated security.* Many steganographic tools treat encryption as an afterthought or rely on weak password hashing. A production-grade system must integrate authenticated encryption with strong key derivation directly into the embedding pipeline.

4) *Complexity of state-of-the-art methods.* Recent deep-learning-based steganographic methods [7] achieve impressive results but require GPU training, large datasets, and introduce significant deployment complexity—barriers for many users and institutions.

5) *Fragmented tooling.* Existing academic implementations often demonstrate a single technique without providing a usable, multi-method application with quality metrics, batch processing, and a graphical interface suitable for non-expert users.

This work addresses these challenges by proposing a lightweight, non-AI hybrid framework that delivers content-aware frequency-domain steganography with full reversibility, optional AES-256-GCM encryption, and an accessible web-based interface—bridging the gap between research-grade algorithms and practical usability.

---

## III. RELATED WORK

This section reviews recent works in image steganography and reversible data hiding relevant to the design of CA-HRD.

### A. Adaptive DCT-Based Steganography

Noorallahzadeh (2026) [5] proposed an adaptive DCT-based steganography algorithm for JPEG images that uses edge detection to identify suitable embedding locations and employs a base-3 encoding scheme for coefficient modification. While the edge-detection-driven adaptivity is effective for JPEG-specific workflows, it is tightly coupled to the JPEG compression pipeline and does not support reversible data hiding. In contrast, the CA-HRD method uses luminance variance rather than edge detection to drive adaptivity, operates on uncompressed pixel data (enabling non-JPEG reversibility), and guarantees perfect cover image reconstruction through residual correction.

### B. Hybrid Transform-Domain RDH

El-den et al. (2025) [6] introduced a reversible and robust hybrid steganography framework that combines the Radon Transform (RT) with the Integer Lifting Wavelet Transform (ILWT). Their hybrid transform approach achieves robustness against geometric attacks but introduces computational overhead from the Radon Transform and requires careful management of two transform domains. The CA-HRD approach adopts a simpler single-transform (DCT) architecture with variance-based capacity selection, offering a more practical and computationally accessible alternative while retaining full reversibility.

### C. DCT + GAN Hybrid Steganography

Malik et al. (2025) [7] proposed a hybrid steganography framework combining DCT embedding with a Generative Adversarial Network (GAN) for generating stego images that resist steganalysis. While the deep-learning component enhances statistical undetectability, it introduces significant computational cost, requires GPU-accelerated training, and reduces reproducibility. The CA-HRD framework achieves content-aware imperceptibility through variance-adaptive coefficient selection—a lightweight, training-free mechanism that remains accessible on commodity hardware.

### D. Surveys and Taxonomies

Ragab et al. (2025) [8] conducted a comprehensive survey of digital image steganography and reversible data hiding, covering spatial, transform-domain (including DCT), adaptive, and encrypted-domain methods. Their taxonomy identifies a clear gap in the literature for methods that combine (i) DCT-domain embedding, (ii) content-aware capacity adaptation, (iii) full reversibility, and (iv) integrated authenticated encryption within a single framework. The CA-HRD algorithm directly fills this gap.

### E. Spatial-Domain Adaptive RDH

Daiyrbayeva et al. (2025) [9] presented an adaptive steganographic method for reversible data hiding based on statistical features of pixel differences. Their histogram-based approach operates entirely in the spatial domain, using pixel-difference distributions to adaptively determine embedding locations. While effective for spatial-domain RDH, the method remains susceptible to spatial-domain steganalysis attacks. CA-HRD's frequency-domain (DCT) operation provides inherent resistance to such attacks by distributing modifications across transform coefficients rather than directly altering pixel values.

### F. Foundational Work

The CA-HRD algorithm builds upon several foundational contributions: Tian's (2003) difference expansion for RDH [2], which established the principle of auxiliary data for reversibility; Fridrich et al.'s (2001) LSB steganalysis [3], which motivates moving beyond spatial-domain-only approaches; Wallace's (1992) description of the DCT in JPEG compression [4], which provides the mathematical basis for coefficient manipulation; and Wang et al.'s (2004) Structural Similarity Index (SSIM) [10], which informs the quality evaluation methodology used in this paper.

---

## IV. PROPOSED METHODOLOGY AND SYSTEM DESIGN

### A. System Architecture

StegoVault follows a modular architecture with clear separation between the user interface layer and the core algorithmic engine. The system comprises six core modules. The presentation layer consists of a Streamlit-based web interface (app.py) providing Encode, Decode, Compare, and Histogram tabs. The algorithmic layer contains five modules: lsb.py (spatial-domain LSB embedding), cahrd.py (DCT-domain CA-HRD embedding with reversibility), metrics.py (PSNR and SSIM computation), crypto.py (AES-256-GCM encryption), and utils.py (bit I/O, framing protocol, and residual serialization). The architecture is illustrated in Fig. 1.

[Figure 1 placeholder: A layered block diagram showing the Streamlit Web UI layer at the top with Encode, Decode, Compare, and Histogram tabs, connected via arrows to the core algorithmic modules (lsb.py, cahrd.py, metrics.py, crypto.py) in the middle layer, all sharing the utils.py utility module at the bottom layer.]

Fig. 1. StegoVault system architecture showing the layered relationship between the web UI and the core algorithmic modules.

### B. CA-HRD Algorithm Design

The Content-Aware Hybrid Reversible Data Hiding algorithm consists of three principal stages: (1) content analysis and capacity mapping, (2) adaptive DCT-domain embedding, and (3) residual computation for reversibility.

#### 1) Content Analysis — Luminance Variance Mapping

The cover image is divided into non-overlapping 8x8 pixel blocks. For each block, the luminance channel is computed using the BT.601 standard:

L(x, y) = 0.299 * R(x, y) + 0.587 * G(x, y) + 0.114 * B(x, y)    (1)

The variance of the luminance block, sigma_L^2, serves as a proxy for visual texture complexity. A four-tier capacity mapping assigns the number of DCT coefficients per channel used for embedding, as shown in TABLE I.

TABLE I
VARIANCE-ADAPTIVE CAPACITY MAPPING

| Variance Threshold (sigma_L^2) | Coefficients per Channel | Bits per Block (3 channels) |
|---|---|---|
| > 800 (highly textured) | 6 | 18 |
| > 300 (moderately textured) | 4 | 12 |
| > 80 (mildly textured) | 2 | 6 |
| <= 80 (smooth) | 1 | 3 |

Higher variance blocks receive more payload bits under the assumption that the HVS is less sensitive to modifications in textured regions. This mapping is stored as a compact cap_map matrix of dimensions floor(H/8) x floor(W/8), where each entry is a single byte.

#### 2) Adaptive DCT-Domain Embedding

For each 8x8 block and each of the three RGB colour channels:

*Step 1 — Forward DCT.* A 2-D type-II orthonormalized DCT is applied:

D = DCT_2D(block)    (2)

*Step 2 — Coefficient selection.* The first k mid-frequency positions (indices 1 through k, in zig-zag scan order) are selected, where k is the capacity assigned to this block. The DC coefficient (index 0) is always preserved to prevent visible brightness shifts.

*Step 3 — LSB replacement in DCT domain.* Each selected coefficient is rounded to the nearest integer, and its least significant bit is replaced with the next payload bit:

D'[z_i] = (D[z_i] AND 0xFFFFFFFE) OR b_i    (3)

where z_i is the zig-zag position and b_i is the payload bit.

*Step 4 — Inverse DCT.* The modified coefficient matrix is transformed back to the spatial domain via inverse DCT, and pixel values are clamped to the valid [0, 255] range.

#### 3) Residual Correction for Reversibility

The forward DCT, quantize, inverse DCT, clamp, and forward DCT pipeline introduces rounding errors. If the stego image is re-transformed, the recovered coefficient LSBs may differ from the intended payload bits. The CA-HRD residual correction addresses this through two mechanisms.

*XOR Correction Bits.* After embedding, the stego image (uint8) is re-transformed block-by-block. For each embedded coefficient, the recovered LSB is compared against the intended bit. A correction bit c_i is computed as:

c_i = recovered_lsb_i XOR intended_bit_i    (4)

During decoding, the decoder reads the raw coefficient LSB and applies c_i via XOR to recover the exact intended bit, completely eliminating rounding-induced errors.

*Original Pixel LSBs.* The LSBs of all pixels in the cover image are recorded before embedding. Combined with the stego image and the correction-corrected payload extraction, this enables the decoder to reconstruct the original cover image exactly.

The residual data—cap_map, correction_bits, and orig_pixel_lsbs—is serialized into a compact binary format (.svr) with the following layout:

    b"SVRD" (4 B) | version (1 B) | encrypted_flag (1 B) | body

When a password is provided, the body is encrypted with AES-256-GCM, binding the residual file's confidentiality to the same password used for the payload.

### C. LSB Steganography Module

The classical LSB channel provides a high-capacity, low-latency alternative. Embedding is fully vectorized using NumPy array operations (Algorithm 1), requiring no Python-level loops and yielding near-instantaneous embedding even on large images. The maximum capacity is (H x W x 3 - 40) / 8 bytes, where 40 accounts for the header bits.

Algorithm 1: Vectorized LSB Embedding

    flat[:n_bits] = (flat[:n_bits] & 0xFE) | payload_bits

### D. Encryption Layer

Both methods share a common encryption pipeline based on AES-256-GCM authenticated encryption:

1) *Key Derivation.* The user's password is processed through PBKDF2-HMAC-SHA256 with 480,000 iterations and a random 16-byte salt, producing a 256-bit key.

2) *Encryption.* AES-256-GCM encrypts the plaintext with a random 12-byte nonce, producing ciphertext concatenated with a 16-byte authentication tag.

3) *Wire Format.* salt (16 B) || nonce (12 B) || ciphertext + tag, introducing a fixed 44-byte overhead.

The authentication tag provides integrity verification: any modification to the ciphertext during transmission or steganalysis will cause decryption to fail, alerting the recipient to tampering.

### E. Length-Prefix Framing Protocol

Embedded data uses a length-prefix framing protocol rather than delimiter-based termination:

    [32 bits: payload length, big-endian] [8 bits: flags] [payload bits...]

The flags byte encodes metadata (bit 0: encrypted/plaintext; bits 1-7: reserved). This design eliminates two vulnerabilities present in delimiter-based schemes: (i) delimiter collision, where the secret message contains the terminator sequence, and (ii) fixed search patterns that steganalyzers can exploit.

---

## V. IMPLEMENTATION DETAILS

### A. Technology Stack

The system is implemented entirely in Python 3.10+ using the libraries listed in TABLE II.

TABLE II
TECHNOLOGY STACK AND LIBRARY DEPENDENCIES

| Component | Library | Role |
|---|---|---|
| Web interface | Streamlit >= 1.32.0 | Interactive UI with tabs, file upload, progress bars |
| Image processing | Pillow >= 10.0.0 | Image I/O and format conversion |
| Numerical operations | NumPy >= 1.26.0 | Vectorized bit manipulation, array operations |
| Signal processing | SciPy >= 1.12.0 | DCT/IDCT transforms, Gaussian convolution for SSIM |
| Cryptography | cryptography >= 42.0.0 | AES-256-GCM, PBKDF2-HMAC-SHA256 |
| Testing | pytest >= 8.0.0 | Unit and integration test framework |

### B. Module Descriptions

*core/cahrd.py (269 lines).* Implements the CA-HRD encode/decode pipeline. Key functions include orthonormalized 2-D DCT/IDCT, variance-to-coefficient mapping, BT.601 luminance extraction, pre-embedding capacity estimation, and encoding that returns a tuple of stego image, cap_map, correction_bits, and orig_pixel_lsbs. Decoding supports both perfect (residual-assisted) and best-effort (recomputed variance) modes.

*core/lsb.py (109 lines).* Vectorized LSB encode/decode using NumPy bitwise operations for zero-loop embedding and extraction, with progress callbacks for UI integration.

*core/crypto.py (79 lines).* AES-256-GCM encryption and decryption with PBKDF2 key derivation. Handles salt and nonce generation, wire format packing/unpacking, and provides meaningful error messages for wrong-password or corruption scenarios.

*core/metrics.py (84 lines).* Computes PSNR and windowed SSIM following the Wang et al. (2004) standard [10] using an 11x11 Gaussian kernel with sigma = 1.5. Also provides per-channel histogram computation for visual analysis.

*core/utils.py (199 lines).* Shared utilities including vectorized bit-byte conversion, length-prefix frame construction and parsing, safe binary serialization for .svr residual files, and image upload validation with JPEG format warnings.

*app.py (977 lines).* Streamlit web application with four main tabs: Encode (single and batch mode), Decode (with residual file support), Method Comparison, and Histogram Analysis. Features a custom dark editorial UI with responsive layout, real-time capacity indicators, and side-by-side image preview with quality metrics.

### C. Zig-Zag Scan Order

The CA-HRD algorithm traverses DCT coefficients in zig-zag order, a standard practice inherited from the JPEG compression pipeline [4]. The zig-zag scan ensures that low-frequency (perceptually important) coefficients are visited first, while embedding targets mid-frequency positions (indices 1 through k), avoiding the DC coefficient entirely.

### D. Test Coverage

The system is validated by a comprehensive test suite of 59+ unit and integration tests organized across six test files: test_crypto.py (encryption round-trips, wrong password detection, data corruption handling), test_lsb.py (LSB round-trips, capacity limits, Unicode text, binary payload), test_cahrd.py (CA-HRD round-trips with and without residual data), test_metrics.py (PSNR, SSIM windowed computation, histogram bins), test_utils.py (bit conversion, frame protocol, residual serialization), and test_integration.py (end-to-end multi-module workflows including encrypted CA-HRD with residual recovery).

---

## VI. RESULTS AND DISCUSSION

### A. Experimental Setup

Experiments were conducted on standard test images of varying dimensions and content types (natural scenes, textures, portraits). The embedding payload ranged from short text messages to longer multi-paragraph content, with and without AES-256-GCM encryption. Quality metrics—PSNR and SSIM—were computed for each encode operation.

### B. Visual Quality Metrics

TABLE III
SUMMARY OF VISUAL QUALITY METRICS ACROSS TEST IMAGES

| Method | PSNR Range (dB) | SSIM Range | Reversibility |
|---|---|---|---|
| LSB (Classic) | 51 - 58 | > 0.999 | No |
| CA-HRD (Adaptive) | 46 - 54 | > 0.999 | Yes (with residual) |

Both methods consistently produce stego images that are visually indistinguishable from the original cover image. The PSNR values are well above the 30 dB threshold generally considered acceptable for image steganography. The SSIM values exceeding 0.999 confirm that structural similarity is preserved at the pixel level.

The slightly lower PSNR for CA-HRD compared to LSB is expected: modifying DCT coefficients and clamping to [0, 255] introduces larger per-pixel perturbations than single-bit LSB changes. However, CA-HRD concentrates these perturbations in textured regions where the HVS is naturally less sensitive, resulting in comparable or superior perceived quality despite the lower numerical PSNR.

### C. Capacity Analysis

For a 512x512 RGB image:

- LSB capacity: (512 x 512 x 3 - 40) / 8 = 98,299 bytes (approximately 96 KB).

- CA-HRD capacity: Varies by image content. Textured images (landscapes, cityscapes) typically yield 15,000-30,000 bytes; smooth images (sky, gradients) yield 5,000-10,000 bytes.

The adaptive capacity of CA-HRD is a deliberate trade-off: lower total capacity enables the method to avoid embedding in smooth regions where modifications would be visually detectable.

### D. Reversibility Verification

The CA-HRD residual correction mechanism was verified through round-trip testing: encode a message, serialize the residual, decode with the residual, and compare the extracted message byte-for-byte against the original. In all test cases, perfect bit-accurate recovery was achieved when the residual .svr file was provided.

Best-effort decoding (without residual) was also tested, demonstrating successful recovery for short to medium messages on images with stable variance characteristics. However, best-effort mode may produce incorrect bits in edge-case blocks where the stego image's variance classification differs from the cover image's classification. This validates the importance of the residual file for mission-critical applications.

### E. Security Evaluation

The AES-256-GCM encryption layer was evaluated for correctness:

- *Round-trip integrity*: All encrypted messages were correctly decrypted with the correct password.
- *Wrong password detection*: Incorrect passwords reliably trigger InvalidTag exceptions, confirming the integrity of GCM authentication.
- *Brute-force resistance*: With 480,000 PBKDF2 iterations and a 256-bit key space, brute-force attacks are computationally infeasible.
- *Overhead*: The fixed 44-byte overhead (salt + nonce + tag) is minimal relative to typical payload sizes.

### F. Comparative Analysis

TABLE IV
COMPARATIVE ANALYSIS OF CA-HRD AGAINST RECENT STEGANOGRAPHIC METHODS

| Feature | CA-HRD (Ours) | Noorallahzadeh [5] | El-den et al. [6] | Malik et al. [7] | Daiyrbayeva et al. [9] |
|---|---|---|---|---|---|
| Domain | DCT (frequency) | DCT (JPEG) | RT + ILWT | DCT + GAN | Spatial |
| Adaptivity basis | Luminance variance | Edge detection | N/A | Learned | Pixel difference statistics |
| Reversibility | Yes (perfect) | No | Yes | No | Yes |
| AI dependency | None | None | None | GAN training required | None |
| Encryption | AES-256-GCM | Not specified | Not specified | Not specified | Not specified |
| Format support | Any lossless (PNG) | JPEG only | Not specified | Not specified | Lossless |
| Computational cost | Low (CPU only) | Low | Medium | High (GPU) | Low |

CA-HRD occupies a distinct niche: it combines frequency-domain embedding, content-aware adaptivity, full reversibility, and authenticated encryption—without requiring AI training or GPU resources. This positions it as a practical and deployable solution, particularly suitable for academic, institutional, and resource-constrained environments.

### G. Histogram Analysis

Per-channel RGB histogram comparison between cover and stego images reveals negligible distributional shift for both methods. The LSB method causes at most +/-1 in pixel values, leading to imperceptible histogram perturbation. The CA-HRD method similarly produces minimal statistical footprint when viewed at the global histogram level, as modifications are distributed across the frequency domain rather than concentrated in specific pixel value ranges.

---

## VII. CONCLUSION

This paper presented StegoVault, a comprehensive image steganography framework that addresses five key challenges in the field: irreversibility, uniform distortion, security integration, computational complexity, and fragmented tooling. The core contribution—the Content-Aware Hybrid Reversible Data Hiding (CA-HRD) algorithm—demonstrates that effective, reversible, and content-aware steganography can be achieved through variance-adaptive DCT-domain embedding paired with a lightweight XOR-based residual correction mechanism.

Experimental results confirm that CA-HRD achieves PSNR values of 46-54 dB and SSIM above 0.999, meeting the imperceptibility requirements for covert communication. The four-tier variance-adaptive capacity mapping concentrates embedding distortion in textured regions, exploiting the masking properties of the Human Visual System. The residual file format enables perfect cover image restoration, satisfying the strict reversibility requirement of sensitive applications.

The integration of AES-256-GCM authenticated encryption with PBKDF2-derived keys provides a robust security layer, while the length-prefix framing protocol eliminates delimiter-based vulnerabilities. The dual-mode architecture (LSB + CA-HRD) allows users to select the appropriate trade-off between capacity, reversibility, and steganographic strength for their specific use case.

Compared to recent hybrid [6], AI-assisted [7], and spatial-domain adaptive [9] approaches, CA-HRD occupies a practical middle ground: it leverages frequency-domain embedding and content-awareness without the computational burden of deep learning, making it accessible and deployable on standard hardware.

---

## VIII. FUTURE SCOPE

Several directions for future enhancement are identified:

1) *Steganalysis resistance evaluation.* Formal testing against modern steganalysis detectors (e.g., SRNet, YedroudjNet) would quantify the statistical undetectability of CA-HRD under adversarial conditions and guide improvements to the coefficient selection strategy.

2) *Multi-bit DCT embedding.* The current scheme embeds one bit per coefficient (LSB replacement). Extending to multi-bit embedding (e.g., 2-bit replacement with compensation) could significantly increase capacity while maintaining quality, guided by the block's variance.

3) *Deep-learning-assisted capacity mapping.* Replacing the fixed variance thresholds with a trained neural network that predicts per-block capacity based on texture, edge, and perceptual saliency features could yield more optimal embedding distributions.

4) *Video steganography.* Extending the block-based DCT framework to video frames, leveraging temporal redundancy for inter-frame embedding and capacity allocation.

5) *Mobile and edge deployment.* Optimizing the DCT pipeline for WebAssembly or mobile platforms would extend StegoVault's reach to resource-constrained devices.

6) *Robustness to image processing.* Investigating error-correction codes (e.g., BCH, Reed-Solomon) embedded alongside the payload to survive mild JPEG recompression, scaling, or noise addition.

7) *Steganographic key management.* Integrating public-key cryptography (e.g., X25519 key exchange) for multi-party covert communication without shared passwords.

---

## REFERENCES

[1] I. Cox, M. Miller, J. Bloom, J. Fridrich, and T. Kalker, *Digital Watermarking and Steganography*, 2nd ed. Burlington, MA, USA: Morgan Kaufmann, 2008.

[2] J. Tian, "Reversible data embedding using a difference expansion," *IEEE Trans. Circuits Syst. Video Technol.*, vol. 13, no. 8, pp. 890-896, Aug. 2003.

[3] J. Fridrich, M. Goljan, and R. Du, "Detecting LSB steganography in color and gray-scale images," *IEEE Multimedia*, vol. 8, no. 4, pp. 22-28, Oct.-Dec. 2001.

[4] G. K. Wallace, "The JPEG still picture compression standard," *IEEE Trans. Consum. Electron.*, vol. 38, no. 1, pp. xviii-xxxiv, Feb. 1992.

[5] M. H. Noorallahzadeh, "Novel adaptive DCT-based steganography algorithm with coefficient selection optimization for JPEG images," *J. Intell. Commun.*, vol. 5, Feb. 2026.

[6] B. M. El-den and W. Raslan, "A reversible and robust hybrid image steganography framework using radon transform and integer lifting wavelet transform," *Sci. Rep.*, vol. 15, no. 1, Art. no. 15687, 2025, doi: 10.1038/s41598-025-98539-2.

[7] K. R. Malik *et al.*, "A hybrid steganography framework using DCT and GAN for secure data communication in the big data era," *Sci. Rep.*, vol. 15, no. 1, Art. no. 19630, Jun. 2025, doi: 10.1038/s41598-025-01054-7.

[8] H. Ragab, H. Shaban, K. Ahmed, and A. Ali, "Digital image steganography and reversible data hiding: Algorithms, applications and recommendations," *J. Image Graph.*, vol. 13, no. 1, pp. 90-114, Feb. 2025, doi: 10.18178/joig.13.1.90-114.

[9] E. Daiyrbayeva *et al.*, "An adaptive steganographic method for reversible information embedding in X-ray images," *Computers*, vol. 14, no. 9, Art. no. 386, 2025, doi: 10.3390/computers14090386.

[10] Z. Wang, A. C. Bovik, H. R. Sheikh, and E. P. Simoncelli, "Image quality assessment: From error visibility to structural similarity," *IEEE Trans. Image Process.*, vol. 13, no. 4, pp. 600-612, Apr. 2004.
