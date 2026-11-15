"""Fetch design-hour and diurnal humidity from Open-Meteo (no API key).

Writes overlays next to the curated CSV; does not silently replace Table-11
values unless --apply is passed.
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITES = ROOT / "sites_design_hour.csv"
OUT_VALIDATE = ROOT / "sites_open_meteo_check.csv"
DIURNAL_DIR = ROOT / "diurnal"


def _get(url: str, timeout: float = 30.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Conditioner-HiMCM/v8"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def archive_day(lat: float, lon: float, date: str, tz: str) -> dict:
    q = urllib.parse.urlencode(
        {
            "latitude": lat,
            "longitude": lon,
            "start_date": date,
            "end_date": date,
            "hourly": "temperature_2m,relative_humidity_2m,dew_point_2m",
            "timezone": tz,
        }
    )
    return _get(f"https://archive-api.open-meteo.com/v1/archive?{q}")


def nearest_14(hourly: dict) -> tuple[float, float, float, str]:
    times = hourly["time"]
    # prefer 14:00 local
    idx = 14 if len(times) > 14 else len(times) // 2
    for i, t in enumerate(times):
        if t.endswith("T14:00"):
            idx = i
            break
    return (
        float(hourly["temperature_2m"][idx]),
        float(hourly["relative_humidity_2m"][idx]),
        float(hourly["dew_point_2m"][idx]),
        times[idx],
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="2023-07-15", help="representative mid-summer day")
    ap.add_argument("--apply", action="store_true", help="overwrite sites_design_hour Ta/RH from API")
    args = ap.parse_args()

    DIURNAL_DIR.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(SITES.open(encoding="utf-8")))
    checks = []

    tz_map = {
        "Dubai": "Asia/Dubai",
        "Cairo": "Africa/Cairo",
        "Los_Angeles": "America/Los_Angeles",
        "Tianjin": "Asia/Shanghai",
        "London": "Europe/London",
        "Atlanta": "America/New_York",
        "Mumbai": "Asia/Kolkata",
        "Singapore": "Asia/Singapore",
    }

    for r in rows:
        site = r["site"]
        try:
            payload = archive_day(float(r["lat"]), float(r["lon"]), args.date, tz_map[site])
            ta, rh, td, stamp = nearest_14(payload["hourly"])
            # diurnal CSV
            times = payload["hourly"]["time"]
            rhs = payload["hourly"]["relative_humidity_2m"]
            tas = payload["hourly"]["temperature_2m"]
            dpath = DIURNAL_DIR / f"{site.lower()}.csv"
            with dpath.open("w", encoding="utf-8", newline="") as f:
                w = csv.writer(f)
                w.writerow(["time", "ta_c", "rh_pct"])
                for t, a, h in zip(times, tas, rhs):
                    w.writerow([t, a, h])
            checks.append(
                {
                    "site": site,
                    "date": args.date,
                    "stamp": stamp,
                    "ta_api": round(ta, 2),
                    "rh_api": round(rh, 1),
                    "td_api": round(td, 2),
                    "ta_table11": r["ta_c"],
                    "rh_table11": r["rh_pct"],
                    "ok": "1",
                }
            )
            if args.apply:
                r["ta_c"] = f"{ta:.1f}"
                r["rh_pct"] = f"{rh:.0f}"
                r["td_c"] = f"{td:.1f}"
                r["source_note"] = f"Open-Meteo archive {args.date} {stamp}"
                r["source_tier"] = "2"
            print(f"{site}: API {ta:.1f}C / {rh:.0f}% vs Table11 {r['ta_c']}C / {r['rh_pct']}%")
        except Exception as e:
            checks.append({"site": site, "ok": "0", "error": str(e)})
            print(f"{site}: FAIL {e}")

    with OUT_VALIDATE.open("w", encoding="utf-8", newline="") as f:
        fields = sorted({k for c in checks for k in c})
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(checks)

    if args.apply:
        with SITES.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print("Wrote updated", SITES)
    else:
        print("Validation only →", OUT_VALIDATE)
        print("Diurnal curves →", DIURNAL_DIR)


if __name__ == "__main__":
    main()
