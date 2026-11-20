"""Build the Morning Update web page from a day's JSON and MP3.

Usage: python3 build_page.py <day.json> <audio.mp3> <out.html>

The MP3 is embedded as a data URI so the page is a single self-contained file.
"""
import base64
import json
import sys
from html import escape

TEMPLATE = open(__file__.replace("build_page.py", "page_template.html")).read()


def build(data: dict, mp3_path: str) -> str:
    audio = base64.b64encode(open(mp3_path, "rb").read()).decode()
    headlines = "\n".join(
        f'<li>'
        + (f'<p class="h-topic">{escape(h["topic"])}</p>' if h.get("topic") else "")
        + f'<p class="h-title">{escape(h["title"])}</p>'
        f'<p class="h-detail">{escape(h["detail"])} '
        f'<a href="{escape(h["url"])}" target="_blank" rel="noopener">{escape(h["source"])}</a></p></li>'
        for h in data["headlines"]
    )
    events = "\n".join(
        f'<li><div class="ev-time"><span>{escape(e["start"])}</span><span class="ev-end">{escape(e["end"])}</span></div>'
        f'<div class="ev-body"><p class="ev-title">{escape(e["title"])}</p>'
        + (f'<p class="ev-where">{escape(e["where"])}</p>' if e.get("where") else "")
        + (f'<p class="ev-note">{escape(e["note"])}</p>' if e.get("note") else "")
        + "</div></li>"
        for e in data["events"]
    ) or '<li class="ev-empty">Nothing on the calendar today.</li>'
    return (
        TEMPLATE.replace("{{DAY_LABEL}}", escape(data["day_label"]))
        .replace("{{DATE}}", escape(data["date"]))
        .replace("{{SUMMARY}}", escape(data["summary"]))
        .replace("{{HEADLINES}}", headlines)
        .replace("{{EVENTS}}", events)
        .replace("{{AUDIO_B64}}", audio)
    )


if __name__ == "__main__":
    day = json.load(open(sys.argv[1]))
    open(sys.argv[3], "w").write(build(day, sys.argv[2]))
