# -*- coding: utf-8 -*-
"""Polish HiMCM English sections via DeepSeek; keep science + contest constraints."""
from __future__ import annotations

import json
import os
import re
import urllib.request
from pathlib import Path

KEY = os.environ.get("DEEPSEEK_API_KEY", "")
BACKUP = os.environ.get("DEEPSEEK_API_KEY_BACKUP", "")
BASE = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

SECTIONS = Path(__file__).resolve().parents[1] / "sections"
TARGETS = [
    "01_summary.typ",
    "02_intro.typ",
    "07_results.typ",
    "08_sensitivity.typ",
    "09_strengths.typ",
    "11_memorandum.typ",
    "12_blog.typ",
]

STYLE = """
You are polishing English for a HiMCM contest paper (high-school math modeling).

Goals:
- Clear, natural, readable contest prose (like strong O-award papers).
- Warm enough to read aloud; avoid dry stacked contrasts.
- Strongly reduce "not X, but Y" / "however/nevertheless" stacking and AI-flavored antithesis.
- Prefer positive or direct statements; short–medium sentences; concrete nouns.

Hard constraints (do NOT violate):
- Keep all Typst markup exactly: #commands, $...$ math, @citations, #figure blocks, tables, labels like <fig:...>.
- Keep Control Number 18388 / Problem B facts if present.
- Keep numerical claims, rankings (A/B/C), dollar amounts, temperatures, Greek symbols, CEI values.
- Do NOT invent new results or citations.
- Do NOT mention local file paths, .py modules, GitHub, or code filenames.
- Do NOT add an AI-use disclosure in the body.
- Return ONLY the full revised Typst file content, no markdown fences.
"""


def chat(key: str, content: str) -> str:
    if not key:
        raise RuntimeError("Set DEEPSEEK_API_KEY in the environment or .env")
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": STYLE},
            {
                "role": "user",
                "content": "Polish this Typst section file:\n\n" + content,
            },
        ],
        "temperature": 0.35,
        "max_tokens": 8192,
    }
    req = urllib.request.Request(
        BASE,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


def strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:typst|typc)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip() + "\n"


def main() -> None:
    if not KEY and not BACKUP:
        raise SystemExit("Missing DEEPSEEK_API_KEY (see .env.example)")
    for name in TARGETS:
        path = SECTIONS / name
        raw = path.read_text(encoding="utf-8")
        print("polish", name, "...")
        try:
            out = chat(KEY or BACKUP, raw)
        except Exception as e:
            print(" primary fail", e, "-> backup")
            out = chat(BACKUP, raw)
        out = strip_fences(out)
        if "#figure" in raw and "#figure" not in out and "image(" in raw:
            print("  SKIP (lost figures):", name)
            continue
        if len(out) < 0.4 * len(raw):
            print("  SKIP (too short):", name)
            continue
        if name == "07_results.typ":
            for token in ("0.599", "4248", "0.47"):
                if token in raw and token not in out:
                    print("  WARN missing token", token, "- keeping original")
                    out = raw
                    break
        path.write_text(out, encoding="utf-8")
        print("  wrote", len(out), "chars")


if __name__ == "__main__":
    main()
