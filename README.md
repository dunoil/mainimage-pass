# MainImage Pass

**Suppressed listing? Get your main image compliant today.**

A web tool for Amazon sellers: upload raw product photos → get Amazon
main-image compliant images (pure white RGB 255,255,255, 2000px, product
centered at ~85% frame fill) plus a per-image preflight PASS/FAIL compliance
report → download everything as a ZIP.

Built new on 18 Nov 2026 for the Ship or Die $100K Hackathon (solo entry,
Contestant #1560). Pricing: Single $39 (1 listing / 10 photos), Bundle $99
(5 listings), Agency $199 (20 listings), one-time.

## Run locally

```bash
cd ~/workspace/mainimage-pass
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # flask, pillow, rembg[cpu]
.venv/bin/python app.py                     # http://localhost:8000
```

Port override: `PORT=8123 .venv/bin/python app.py`

First run downloads the rembg u2netp model (~4.6 MB) to `~/.rembg/`.

## Architecture

| File | Role |
|---|---|
| `app.py` | Flask server. `GET /` landing+tool, `POST /api/process` (multipart field `photos`, max 10 JPG/PNG, 60 MB total) → JSON results + download URL, `GET /download/<job_id>` → ZIP (processed JPGs + `report.html`). Jobs are kept **in memory only**. |
| `processing.py` | Pipeline: background removal → composite on pure white → scale/center on a 2000×2000 canvas → compliance checks (resolution, background purity via 8 edge samples, JPEG format, source-resolution FAIL <500px / WARN <2000px, frame fill, subject detection). |
| `report.py` | Generates the standalone `report.html` included in the ZIP. |
| `templates/index.html` | Single-page landing + tool UI (inline CSS/JS, drag & drop, no external assets). Before/after visual is pure CSS shapes — no product photos. |
| `tests/` | `make_test_image.py` (synthetic Pillow mug on beige) and `run_e2e_test.py` (starts against a running server on port 8123, verifies ZIP + output pixels). |
| `test-evidence/` | Input/output images, API response JSON, report HTML, ZIP, and test logs from the 18 Nov 2026 verification run. |

## Background removal — which path is active

**ACTIVE: rembg** (u2netp ONNX model, verified end-to-end in this VM on
18 Nov 2026 — see `test-evidence/e2e_test.log`; every processed image records
`bg_method` in its report).

**Fallback (implemented and unit-tested):** if rembg is unavailable or errors
on an image, `processing._remove_bg_floodfill` flood-fills from the four
corners with a colour-distance threshold — works on near-uniform backgrounds
(typical studio shots), weaker on busy/lifestyle backgrounds.

Model can be upgraded via env `REMBG_MODEL=u2net` (larger, higher quality).

## Placeholders (NOT wired yet — do not go live until done)

- **Payments:** the three pricing buttons are `href="#"` with
  `data-plan="single|bundle|agency"` and HTML comments marked
  `CHECKOUT PLACEHOLDER: TO BE WIRED to Creem/Polar`. No payment products
  exist yet; the upload tool currently processes without payment gating.
- **Ship or Die tracker:** `templates/index.html` `<head>` contains
  `<!-- SHIP_OR_DIE_TRACKER: paste before </head> -->` where the real tracker
  snippet must be pasted **before the site receives any traffic**.
- **TrustMRR:** not connected yet; must be connected **before the first
  payment** (contest rules).

## Known limitations

- Jobs are in-memory: restarting the server loses download links.
- No accounts, no payment gating, no persistent storage (out of MVP scope).
- Square 2000×2000 canvas for every image; no per-category Amazon rules
  beyond main-image technical rules.
- The preflight checks technical rules only. Content rules (no text, props,
  lifestyle elements, watermarks in the main image) cannot be auto-verified
  and are flagged as the seller's responsibility in the report.
- rembg u2netp is the lightweight model — fast, but edge quality on complex
  products (fur, glass, reflective) is weaker than u2net; test before launch.
- Flood-fill fallback fails on non-uniform backgrounds (by design it is a
  fallback, not the primary path).
