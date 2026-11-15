"""Load curated design-hour site table."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

DATA = Path(__file__).resolve().parents[1] / "data" / "sites_design_hour.csv"


@dataclass(frozen=True)
class Site:
    key: str
    city: str
    country: str
    koppen: str
    lat: float
    lon: float
    ta_c: float
    td_c: float
    rh_pct: float
    twb_c: float
    p_hpa: float
    source_tier: int
    source_note: str

    @property
    def rh(self) -> float:
        return self.rh_pct / 100.0


def load_sites(path: Path | None = None) -> List[Site]:
    p = path or DATA
    out: List[Site] = []
    with p.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append(
                Site(
                    key=r["site"],
                    city=r["city"],
                    country=r["country"],
                    koppen=r["koppen"],
                    lat=float(r["lat"]),
                    lon=float(r["lon"]),
                    ta_c=float(r["ta_c"]),
                    td_c=float(r["td_c"]),
                    rh_pct=float(r["rh_pct"]),
                    twb_c=float(r["twb_c"]),
                    p_hpa=float(r["p_hpa"]),
                    source_tier=int(r["source_tier"]),
                    source_note=r.get("source_note", ""),
                )
            )
    return out


def sites_by_key(path: Path | None = None) -> Dict[str, Site]:
    return {s.key: s for s in load_sites(path)}
