"""MainImage Pass — preflight compliance report (HTML) generation.
Created 18 Nov 2026 for the Ship or Die $100K Hackathon (all code is new).
"""

import html
from datetime import datetime, timezone

STATUS_ICON = {"PASS": "✅ PASS", "WARN": "⚠️ WARN", "FAIL": "❌ FAIL"}


def build_report(results):
    """results: list of dicts from processing.process_image plus 'source_name'.
    Returns a standalone HTML string (also embedded in the delivered ZIP)."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    passed = sum(1 for r in results if r["overall"] == "PASS")
    rows = []
    for r in results:
        check_rows = "".join(
            f"<tr><td>{html.escape(c['name'])}</td>"
            f"<td class='s-{c['status'].lower()}'>{STATUS_ICON[c['status']]}</td>"
            f"<td>{html.escape(c['detail'])}</td></tr>"
            for c in r["checks"]
        )
        rows.append(f"""
        <section class="card">
          <h2>{html.escape(r['source_name'])} &rarr; {html.escape(r['output_name'])}
              <span class="badge b-{r['overall'].lower()}">{r['overall']}</span></h2>
          <p class="meta">Source size: {r['source_size']} &middot;
             Background removal: {html.escape(r['bg_method'])} &middot;
             Frame fill: {r['fill_pct']}%</p>
          <table>{check_rows}</table>
        </section>""")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>MainImage Pass — Preflight Compliance Report</title>
<style>
 body{{font-family:system-ui,Arial,sans-serif;margin:2rem auto;max-width:860px;padding:0 1rem;color:#1a1a1a}}
 h1{{font-size:1.5rem}} .card{{border:1px solid #ddd;border-radius:10px;padding:1rem 1.25rem;margin:1rem 0}}
 table{{width:100%;border-collapse:collapse}} td{{padding:.4rem .5rem;border-top:1px solid #eee;vertical-align:top}}
 .badge{{color:#fff;padding:.15rem .6rem;border-radius:999px;font-size:.8rem}}
 .b-pass{{background:#1a9e54}} .b-fail{{background:#d33}}
 .s-pass{{color:#1a9e54;font-weight:600}} .s-warn{{color:#c78100;font-weight:600}} .s-fail{{color:#d33;font-weight:600}}
 .meta{{color:#666;font-size:.9rem}}
</style></head><body>
<h1>MainImage Pass — Preflight Compliance Report</h1>
<p>Generated {now}. <strong>{passed}/{len(results)} image(s) PASS</strong> all
critical Amazon main-image checks. Checks cover: pure-white background
RGB(255,255,255), 2000px longest side for zoom, JPEG delivery, source
resolution, and product frame fill (~85% guideline).</p>
<p><em>Note: this is an automated preflight. Amazon's final acceptance also
depends on content rules (no text, props, or lifestyle elements in the main
image) that only you can confirm for your listing.</em></p>
{''.join(rows)}
</body></html>"""
