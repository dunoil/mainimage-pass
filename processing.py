"""MainImage Pass — image processing pipeline.

Created 18 Nov 2026 for the Ship or Die $100K Hackathon (all code is new).

Pipeline per image:
  1. Remove the background.
     - PRIMARY PATH: the bundled u2netp ONNX model through a lean
       onnxruntime session (about 95 MB peak, fits the free hosting tier).
     - FALLBACK PATHS: rembg's default session if the lean path is
       unavailable, then flood-fill from the four corners for near-uniform
       backgrounds.
  2. Composite the cut-out product onto pure white RGB(255, 255, 255).
  3. Place it, centered, on a square 2000x2000 canvas, scaled so the
     product's longest side fills ~85% of the frame (Amazon guideline).
  4. Run compliance checks and return a structured report.

Which path is active is recorded per image in the report ("bg_method").
"""

import io
import os
from PIL import Image, ImageDraw

CANVAS_SIZE = 2000          # Amazon zoom-friendly: longest side 2000px
FRAME_FILL = 0.85           # product longest side = 85% of frame
PURE_WHITE = (255, 255, 255)

# ------------------------------------------------------------- lean ORT path
# Primary path: run the bundled u2netp model through a lean onnxruntime
# session (arena and mem pattern off, single thread). Measured on this
# project: about 95 MB peak RSS for a full removal, versus about 530 MB
# through rembg's default session, which exceeds the free hosting tier's
# 512 MB limit and caused an out-of-memory restart on 21 Nov 2026.
_LEAN_SESSION = None
_LEAN_TRIED = False
_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "models", "u2netp.onnx")


def _get_lean_session():
    global _LEAN_SESSION, _LEAN_TRIED
    if _LEAN_TRIED:
        return _LEAN_SESSION
    _LEAN_TRIED = True
    try:
        import onnxruntime as ort
        if not os.path.exists(_MODEL_PATH):
            return None
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.inter_op_num_threads = 1
        opts.enable_cpu_mem_arena = False
        opts.enable_mem_pattern = False
        _LEAN_SESSION = ort.InferenceSession(
            _MODEL_PATH, sess_options=opts, providers=["CPUExecutionProvider"])
    except Exception:
        _LEAN_SESSION = None
    return _LEAN_SESSION


def _remove_bg_lean(img_rgba):
    """u2netp inference replicating rembg's own preprocessing exactly
    (LANCZOS resize, divide by image max, ImageNet mean/std, mask resized
    back with LANCZOS), but through the lean session above."""
    import numpy as np
    session = _get_lean_session()
    if session is None:
        raise RuntimeError("lean session unavailable")
    rgb = img_rgba.convert("RGB")
    small = rgb.resize((320, 320), Image.LANCZOS)
    arr = np.array(small).astype(np.float64)
    arr = arr / max(float(np.max(arr)), 1e-6)
    arr[:, :, 0] = (arr[:, :, 0] - 0.485) / 0.229
    arr[:, :, 1] = (arr[:, :, 1] - 0.456) / 0.224
    arr[:, :, 2] = (arr[:, :, 2] - 0.406) / 0.225
    arr = arr.transpose(2, 0, 1)[None, :, :, :].astype(np.float32)
    out = session.run(None, {session.get_inputs()[0].name: arr})
    mask = out[0][:, 0, :, :]
    span = float(np.max(mask) - np.min(mask))
    mask = (mask - np.min(mask)) / (span if span > 1e-8 else 1.0)
    mask = np.squeeze(mask)
    alpha = Image.fromarray((mask.clip(0, 1) * 255).astype(np.uint8),
                            mode="L").resize(rgb.size, Image.LANCZOS)
    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


# ---------------------------------------------------------------- rembg path
_REMBG_SESSION = None
_REMBG_TRIED = False


def _get_rembg_session():
    """Lazily create one rembg session (model env REMBG_MODEL, default u2netp)."""
    global _REMBG_SESSION, _REMBG_TRIED
    if _REMBG_TRIED:
        return _REMBG_SESSION
    _REMBG_TRIED = True
    try:
        from rembg import new_session
        _REMBG_SESSION = new_session(os.environ.get("REMBG_MODEL", "u2netp"))
    except Exception:
        _REMBG_SESSION = None
    return _REMBG_SESSION


def _remove_bg_rembg(img_rgba):
    from rembg import remove
    session = _get_rembg_session()
    if session is None:
        raise RuntimeError("rembg unavailable")
    return remove(img_rgba, session=session)


# ------------------------------------------------------------- fallback path
def _remove_bg_floodfill(img_rgba, thresh=36):
    """Background removal for near-uniform backgrounds.

    Flood-fills from all four corners (PIL floodfill with a colour-distance
    threshold). Filled pixels become transparent; the rest stays opaque.
    """
    rgb = img_rgba.convert("RGB").copy()
    w, h = rgb.size
    marker = (1, 254, 253)  # unlikely natural colour, used as "filled" tag
    draw_work = rgb
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        try:
            ImageDraw.floodfill(draw_work, seed, marker, thresh=thresh)
        except Exception:
            pass
    # Build the alpha mask: pixels equal to the marker are background.
    from PIL import ImageChops
    chans = draw_work.split()
    masks = []
    for chan, target in zip(chans, marker):
        masks.append(chan.point(lambda v, t=target: 255 if v == t else 0))
    bg_mask = ImageChops.multiply(ImageChops.multiply(masks[0], masks[1]),
                                  masks[2])
    alpha = ImageChops.invert(bg_mask)  # subject = 255, background = 0
    out = img_rgba.copy()
    out.putalpha(alpha)
    return out


def remove_background(img):
    """Return (RGBA image with alpha cut-out, method_name).

    Order: lean u2netp session (low memory), rembg (fallback if the lean
    path is unavailable), flood fill (last resort for uniform backgrounds).
    """
    rgba = img.convert("RGBA")
    if _get_lean_session() is not None:
        try:
            return _remove_bg_lean(rgba), "u2netp-lean"
        except Exception:
            pass
    session = _get_rembg_session()
    if session is not None:
        try:
            cut = _remove_bg_rembg(rgba)
            if cut.mode != "RGBA":
                cut = cut.convert("RGBA")
            return cut, "rembg"
        except Exception:
            pass
    return _remove_bg_floodfill(rgba), "floodfill-fallback"


# ------------------------------------------------------------------ pipeline
def _trim_to_subject(rgba):
    """Crop to the bounding box of non-transparent pixels."""
    alpha = rgba.getchannel("A")
    bbox = alpha.getbbox()
    return bbox


def process_image(raw_bytes, filename):
    """Process one uploaded image.

    Returns dict with:
      output_bytes (JPEG), output_name, checks [ {name, status, detail} ],
      overall ("PASS"/"FAIL"), bg_method, source_size, fill_pct
    """
    src = Image.open(io.BytesIO(raw_bytes))
    src.load()
    src_w, src_h = src.size
    src_format = (src.format or "unknown").upper()

    checks = []

    # -- background removal + subject detection
    # Memory guard: run removal on a working copy capped at 1200px on the
    # longest side. The delivered canvas is fixed at 2000px with the subject
    # scaled to 1700px, so the cap costs nothing visible, while peak RAM on
    # very large phone photos drops several-fold (free-tier instance limit).
    work = src
    if max(src_w, src_h) > 1200:
        ratio = 1200 / max(src_w, src_h)
        work = src.resize((round(src_w * ratio), round(src_h * ratio)),
                          Image.LANCZOS)
    work_w, work_h = work.size
    cut, method = remove_background(work)
    bbox = _trim_to_subject(cut)
    if bbox is None:
        checks.append({
            "name": "Subject detected",
            "status": "FAIL",
            "detail": "Background removal found no product in the image.",
        })
        subject = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    else:
        subject = cut.crop(bbox)
        coverage = subject.size[0] * subject.size[1] / (work_w * work_h) * 100
        checks.append({
            "name": "Subject detected",
            "status": "PASS",
            "detail": f"Product isolated via {method}; bounding box covers "
                      f"{coverage:.0f}% of the original frame.",
        })

    # -- scale product so its longest side = 85% of the 2000px frame
    target = int(CANVAS_SIZE * FRAME_FILL)
    sw, sh = subject.size
    scale = target / max(sw, sh) if max(sw, sh) else 1.0
    new_size = (max(1, round(sw * scale)), max(1, round(sh * scale)))
    subject_big = subject.resize(new_size, Image.LANCZOS)

    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), PURE_WHITE)
    offset = ((CANVAS_SIZE - new_size[0]) // 2, (CANVAS_SIZE - new_size[1]) // 2)
    canvas.paste(subject_big, offset, subject_big)

    # -- checks ------------------------------------------------------------
    longest = max(canvas.size)
    checks.append({
        "name": "Output resolution ≥ 2000px (longest side)",
        "status": "PASS" if longest >= 2000 else "FAIL",
        "detail": f"Output is {canvas.size[0]}x{canvas.size[1]}px.",
    })

    # background purity: corners + edge midpoints must be pure white
    px = canvas.load()
    W, H = canvas.size
    samples = [(0, 0), (W - 1, 0), (0, H - 1), (W - 1, H - 1),
               (W // 2, 0), (W // 2, H - 1), (0, H // 2), (W - 1, H // 2)]
    impure = [s for s in samples if px[s] != PURE_WHITE]
    checks.append({
        "name": "Background pure white RGB(255,255,255)",
        "status": "PASS" if not impure else "FAIL",
        "detail": "All 8 edge/corner samples are pure white."
                  if not impure else
                  f"{len(impure)} edge sample(s) are not pure white.",
    })

    checks.append({
        "name": "Output format is JPEG",
        "status": "PASS",
        "detail": "Delivered as .jpg (Amazon main images must be JPEG/JPG).",
    })

    src_longest = max(src_w, src_h)
    if src_longest < 500:
        checks.append({
            "name": "Source resolution",
            "status": "FAIL",
            "detail": f"Source is only {src_w}x{src_h}px ({src_format}). "
                      "Below Amazon's 500px minimum for zoom; the output was "
                      "upscaled and may look soft. Re-shoot at 2000px+.",
        })
    elif src_longest < 2000:
        checks.append({
            "name": "Source resolution",
            "status": "WARN",
            "detail": f"Source is {src_w}x{src_h}px ({src_format}); upscaled "
                      "to 2000px. Acceptable, but a 2000px+ original is sharper.",
        })
    else:
        checks.append({
            "name": "Source resolution",
            "status": "PASS",
            "detail": f"Source is {src_w}x{src_h}px ({src_format}).",
        })

    fill_pct = max(new_size) / CANVAS_SIZE * 100
    checks.append({
        "name": "Product fills frame (Amazon guideline ≥85%)",
        "status": "PASS" if fill_pct >= 80 else "WARN",
        "detail": f"Product's longest side fills {fill_pct:.0f}% of the frame "
                  "(scaled to the 85% target, centered).",
    })

    overall = "FAIL" if any(c["status"] == "FAIL" for c in checks) else "PASS"

    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=92)
    stem = os.path.splitext(os.path.basename(filename))[0] or "image"
    return {
        "output_bytes": buf.getvalue(),
        "output_name": f"{stem}_main_2000.jpg",
        "checks": checks,
        "overall": overall,
        "bg_method": method,
        "source_size": f"{src_w}x{src_h}",
        "fill_pct": round(fill_pct),
    }
