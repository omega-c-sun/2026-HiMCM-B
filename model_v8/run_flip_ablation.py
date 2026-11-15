"""Single-factor ablation: bus → rail flip causes."""

from __future__ import annotations

import csv
from pathlib import Path

from .m3_cei import evaluate_units
from .units import BUS, RAIL, shelter_variant

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs_v8"

TA, RH = 33.5, 55.0


def _summary(label: str, shelter, rows):
    by = {r.unit_id: r for r in rows}
    margin = by["B"].delta_teq_k - by["A"].delta_teq_k
    feas = [u for u in ("A", "B", "C") if by[u].feasible]
    winner = max(feas, key=lambda u: by[u].cei) if feas else "empty"
    return {
        "case": label,
        "q_gain_kw": shelter.q_gain_kw,
        "openness": shelter.openness,
        "wind_m_s": shelter.wind_m_s,
        "a_open_m2": shelter.a_open_m2,
        "budget_usd": shelter.budget_usd,
        "dTeq_A": round(by["A"].delta_teq_k, 3),
        "dTeq_B": round(by["B"].delta_teq_k, 3),
        "dTeq_C": round(by["C"].delta_teq_k, 3),
        "margin_B_minus_A": round(margin, 3),
        "dn_B": round(by["B"].dn, 3),
        "dn_C": round(by["C"].dn, 3),
        "cei_A": round(by["A"].cei, 3),
        "cei_B": round(by["B"].cei, 3),
        "cei_C": round(by["C"].cei, 3),
        "feasible": ",".join(feas) if feas else "empty",
        "cei_winner": winner,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = [
        ("bus_baseline", BUS, None),
        (
            "gain_only",
            shelter_variant(BUS, q_gain_kw=RAIL.q_gain_kw, budget_usd=RAIL.budget_usd),
            None,
        ),
        (
            "exchange_only",
            shelter_variant(
                BUS,
                openness=RAIL.openness,
                a_open_m2=RAIL.a_open_m2,
                h_open_m=RAIL.h_open_m,
                wind_m_s=RAIL.wind_m_s,
                ach_min=RAIL.ach_min,
                area_m2=RAIL.area_m2,
                height_m=RAIL.height_m,
                budget_usd=RAIL.budget_usd,
            ),
            None,
        ),
        (
            "ksc_boost_only",
            shelter_variant(BUS, budget_usd=RAIL.budget_usd),
            1.8,
        ),
        ("rail_combined", RAIL, None),
    ]

    out_rows = []
    for label, sh, ksc in cases:
        rows = evaluate_units(
            TA, RH, sh, mode="fluids", site_label="Tianjin", k_sc=ksc
        )
        out_rows.append(_summary(label, sh, rows))

    path = OUT / "flip_ablation.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    for r in out_rows:
        print(
            f"{r['case']}: margin={r['margin_B_minus_A']} dnB={r['dn_B']} dnC={r['dn_C']} "
            f"winner={r['cei_winner']} feas={r['feasible']}"
        )
    print("Wrote", path)


if __name__ == "__main__":
    main()
