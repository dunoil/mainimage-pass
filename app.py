"""MainImage Pass — Flask backend.
Created 18 Nov 2026 for the Ship or Die $100K Hackathon (all code is new).

Routes:
  GET  /                  landing page + upload tool (templates/index.html)
  GET  /privacy           privacy policy (templates/privacy.html)
  GET  /terms             terms of service (templates/terms.html)
  POST /api/process       multipart field "photos" (up to 10 JPG/PNG)
                          -> JSON {job_id, results:[...], download_url}
  GET  /download/<job_id> ZIP of processed images + report.html

Run:  .venv/bin/python app.py   (port from env PORT, default 8000)
"""

import io
import os
import uuid
import zipfile

from flask import Flask, jsonify, request, send_file, render_template

from processing import process_image
from report import build_report

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 60 * 1024 * 1024  # 60 MB total upload cap

MAX_FILES = 10
ALLOWED_EXT = {".jpg", ".jpeg", ".png"}

# In-memory job store: job_id -> {"zip": bytes, "results": [...]}
# MVP only — no persistence, jobs vanish on restart (documented in README).
JOBS = {}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/privacy")
def privacy():
    return render_template("privacy.html")


@app.get("/terms")
def terms():
    return render_template("terms.html")


@app.post("/api/process")
def api_process():
    files = [f for f in request.files.getlist("photos") if f.filename]
    if not files:
        return jsonify({"error": "No files uploaded. Choose up to 10 JPG/PNG photos."}), 400
    if len(files) > MAX_FILES:
        return jsonify({"error": f"Too many files: {len(files)}. Max is {MAX_FILES} per listing."}), 400

    results = []
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            ext = os.path.splitext(f.filename)[1].lower()
            if ext not in ALLOWED_EXT:
                results.append({
                    "source_name": f.filename, "output_name": "-",
                    "overall": "FAIL", "bg_method": "-", "source_size": "-",
                    "fill_pct": 0,
                    "checks": [{"name": "File format", "status": "FAIL",
                                "detail": f"{ext or 'unknown'} is not supported. Upload JPG or PNG."}],
                })
                continue
            r = process_image(f.read(), f.filename)
            r["source_name"] = f.filename
            results.append(r)
            zf.writestr(r["output_name"], r["output_bytes"])
        report_html = build_report(results)
        zf.writestr("report.html", report_html)

    job_id = uuid.uuid4().hex[:12]
    public_results = [{k: v for k, v in r.items() if k != "output_bytes"}
                      for r in results]
    JOBS[job_id] = {"zip": zip_buf.getvalue(), "results": public_results}
    return jsonify({
        "job_id": job_id,
        "download_url": f"/download/{job_id}",
        "results": public_results,
    })


@app.get("/download/<job_id>")
def download(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found (jobs are kept in memory only)."}), 404
    return send_file(
        io.BytesIO(job["zip"]),
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"mainimage-pass-{job_id}.zip",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
