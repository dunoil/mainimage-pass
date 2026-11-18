"""End-to-end test: start the Flask app, POST the synthetic photo,
download the ZIP, and verify the output image properties.
Created 18 Nov 2026. Run with the project venv:
  .venv/bin/python tests/run_e2e_test.py
Writes evidence into test-evidence/ and prints a PASS/FAIL summary.
"""
import io
import json
import os
import sys
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image  # noqa: E402

BASE = "http://127.0.0.1:8123"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "test-evidence")
os.makedirs(EV, exist_ok=True)

failures = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        failures.append(name)


# 1. multipart POST -------------------------------------------------------
boundary = "----mip-test-boundary"
input_path = os.path.join(EV, "input_mug_beige.jpg")
with open(input_path, "rb") as fh:
    payload = fh.read()
body = (
    f"--{boundary}\r\n"
    'Content-Disposition: form-data; name="photos"; filename="input_mug_beige.jpg"\r\n'
    "Content-Type: image/jpeg\r\n\r\n"
).encode() + payload + f"\r\n--{boundary}--\r\n".encode()
req = urllib.request.Request(
    BASE + "/api/process", data=body, method="POST",
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
with urllib.request.urlopen(req, timeout=120) as resp:
    data = json.loads(resp.read())

check("API returns 1 result", len(data["results"]) == 1)
r = data["results"][0]
print(json.dumps(r, indent=2))
check("overall PASS", r["overall"] == "PASS", f"(got {r['overall']})")
check("bg method recorded", r["bg_method"] in ("rembg", "floodfill-fallback"),
      f"(method={r['bg_method']})")
with open(os.path.join(EV, "api_response.json"), "w") as fh:
    json.dump(data, fh, indent=2)

# 2. download ZIP ----------------------------------------------------------
with urllib.request.urlopen(BASE + data["download_url"], timeout=60) as resp:
    zip_bytes = resp.read()
zip_path = os.path.join(EV, "output.zip")
with open(zip_path, "wb") as fh:
    fh.write(zip_bytes)
zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
names = zf.namelist()
print("ZIP contents:", names)
check("ZIP has processed jpg", any(n.endswith("_main_2000.jpg") for n in names))
check("ZIP has report.html", "report.html" in names)

jpg_name = next(n for n in names if n.endswith(".jpg"))
out_path = os.path.join(EV, "output_main_2000.jpg")
with open(out_path, "wb") as fh:
    fh.write(zf.read(jpg_name))
with open(os.path.join(EV, "report_from_zip.html"), "wb") as fh:
    fh.write(zf.read("report.html"))

# 3. verify output image ----------------------------------------------------
img = Image.open(out_path)
check("output format JPEG", img.format == "JPEG", f"(got {img.format})")
check("output longest side == 2000", max(img.size) == 2000, f"(size={img.size})")
rgb = img.convert("RGB")
px = rgb.load()
W, H = rgb.size
corners = [px[0, 0], px[W - 1, 0], px[0, H - 1], px[W - 1, H - 1]]
check("all 4 corners pure white (255,255,255)",
      all(c == (255, 255, 255) for c in corners), f"(corners={corners})")
# product still present: center pixel should be mug-blue-ish, not white
center = px[W // 2, H // 2]
check("product present at center", center != (255, 255, 255) and center[2] > 120,
      f"(center={center})")

print("\nRESULT:", "ALL PASS" if not failures else f"FAILURES: {failures}")
sys.exit(1 if failures else 0)
