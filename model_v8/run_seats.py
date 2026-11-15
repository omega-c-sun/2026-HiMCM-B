"""Multi-seat compliance table at Tianjin open shelter."""

from __future__ import annotations

import csv
from pathlib import Path

from .m1_fluids import deliver
from .m2_feel import feel, feel_at_stations
from .units import BUS, BUS_STATIONS, T_SAFETY_MAX_C, UNITS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs_v8"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for uid, unit in UNITS.items():
        m1 = deliver(unit, BUS, 33.5, 55.0, mode="fluids")
        m2 = feel(unit, m1, 33.5)
        seats = feel_at_stations(unit, m1, 33.5, BUS_STATIONS)
        for x, w, dteq, ok in seats:
            rows.append(
                {
                    "unit": uid,
                    "x_m": x,
                    "weight": w,
                    "delta_teq_k": round(dteq, 3),
                    "t_felt_c": round(33.5 - dteq, 3),
                    "safe_le_35": int(ok),
                    "aggregate_t_felt": round(m2.t_felt_c, 3),
                    "safety_line_c": T_SAFETY_MAX_C,
                }
            )
    path = OUT / "seat_compliance.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("Wrote", path)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
