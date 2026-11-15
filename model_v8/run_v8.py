"""Run v8 baseline cases, eight cities, write CSV + figures."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from .crossover import (
    crossover_fluids_coupled,
    crossover_legacy_decay,
    crossover_v7_claimed,
)
from .m3_cei import evaluate_units, reproduce_v7_cei
from .sites import load_sites
from .units import BUS, RAIL

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs_v8"
FIG = ROOT / "paper" / "figures"


def _write_rows(path: Path, rows: list) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].__dict__.keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r.__dict__)


def _try_plot():
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None
    return plt


def fig_crossover(plt) -> None:
    c0 = crossover_v7_claimed()
    c1 = crossover_legacy_decay()
    c2 = crossover_fluids_coupled()
    FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for c, ls in [(c0, "-"), (c1, "--"), (c2, "-.")]:
        rh = [r[0] for r in c.rows]
        fan = [r[1] for r in c.rows]
        ev = [r[2] for r in c.rows]
        ax.plot(rh, ev, ls, label=f"Evap ({c.label}, RH*={c.rh_star_pct:.0f}%)")
    ax.plot([15, 95], [c0.rows[0][1], c0.rows[0][1]], "k:", label="Fan feel")
    ax.axvline(c0.rh_star_pct, color="0.5", lw=0.8)
    ax.axvline(c2.rh_star_pct, color="0.2", lw=0.8, ls="--")
    ax.set_xlabel("Relative humidity (%)")
    ax.set_ylabel("Felt benefit ΔTeq (K)")
    ax.set_title("Crossover ablation at Ta = 33.5 °C")
    ax.legend(fontsize=8)
    ax.set_xlim(15, 95)
    fig.tight_layout()
    fig.savefig(FIG / "v8_crossover.png", dpi=160)
    fig.savefig(OUT / "v8_crossover.png", dpi=160)
    plt.close(fig)

    with (OUT / "crossover_summary.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "dn", "rh_star_pct", "dtwb_star_k"])
        for c in (c0, c1, c2):
            w.writerow([c.label, f"{c.dn:.4f}", f"{c.rh_star_pct:.1f}", f"{c.dtwb_star_k:.3f}"])


def fig_eight_cities(plt, city_rows: list) -> None:
    # one row per city for unit B margin vs fan
    by = {}
    for r in city_rows:
        by.setdefault(r.site, {})[r.unit_id] = r
    names, margins, winners = [], [], []
    for site, d in by.items():
        if "A" not in d or "B" not in d:
            continue
        names.append(site.replace("_", " "))
        margins.append(d["B"].delta_teq_k - d["A"].delta_teq_k)
        feas = [u for u in ("A", "B", "C") if d[u].feasible]
        if not feas:
            winners.append("empty")
        else:
            winners.append(max(feas, key=lambda u: d[u].cei))
    FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    colors = ["#2a6f97" if m >= 0 else "#b23a48" for m in margins]
    ax.bar(range(len(names)), margins, color=colors)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=30, ha="right")
    ax.set_ylabel("Margin ΔTeq(B)−ΔTeq(A) (K)")
    ax.set_title("Eight cities: evaporative vs fan felt margin (fluids M1)")
    for i, w in enumerate(winners):
        ax.text(i, margins[i] + (0.08 if margins[i] >= 0 else -0.15), w, ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "v8_eight_cities.png", dpi=160)
    fig.savefig(OUT / "v8_eight_cities.png", dpi=160)
    plt.close(fig)


def fig_platform_flip(plt, bus_rows, rail_rows) -> None:
    labels = ["A", "B", "C"]
    bcei = [next(r.cei for r in bus_rows if r.unit_id == u) for u in labels]
    rcei = [next(r.cei for r in rail_rows if r.unit_id == u) for u in labels]
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.bar(x - 0.18, bcei, 0.36, label="Open bus")
    ax.bar(x + 0.18, rcei, 0.36, label="Semi-open rail")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("CEI")
    ax.set_title("Site transfer: CEI before/after (fluids)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "v8_platform_flip.png", dpi=160)
    fig.savefig(OUT / "v8_platform_flip.png", dpi=160)
    plt.close(fig)


def fig_delivery_bars(plt, rows) -> None:
    labels = ["A", "B", "C"]
    d0 = []
    dz = []
    deq = []
    for u in labels:
        r = next(x for x in rows if x.unit_id == u)
        # reconstruct nominal
        from .units import UNITS

        d0.append(UNITS[u].delta_t0_k)
        dz.append(max(r.delta_tz_k, 0.0))
        deq.append(r.delta_teq_k)
    x = np.arange(3)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.bar(x - 0.25, d0, 0.25, label="ΔT0 catalogue")
    ax.bar(x, dz, 0.25, label="ΔTz delivered")
    ax.bar(x + 0.25, deq, 0.25, label="ΔTeq felt")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("K")
    ax.set_title("Tianjin open shelter: outlet → seat → feel (fluids)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "v8_delivery_bars.png", dpi=160)
    fig.savefig(OUT / "v8_delivery_bars.png", dpi=160)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    reg = reproduce_v7_cei()
    print("V7 CEI regression:", np.round(reg["cei"], 3), "target", reg["target"])
    assert np.allclose(reg["cei"], reg["target"], atol=0.02), reg["cei"]

    tianjin = next(s for s in load_sites() if s.key == "Tianjin")
    bus = evaluate_units(
        tianjin.ta_c, tianjin.rh_pct, BUS, mode="fluids", site_label="Tianjin"
    )
    rail = evaluate_units(
        tianjin.ta_c, tianjin.rh_pct, RAIL, mode="fluids", site_label="Tianjin"
    )
    _write_rows(OUT / "task2_bus_tianjin.csv", bus)
    _write_rows(OUT / "task3_rail_tianjin.csv", rail)

    city_rows = []
    for s in load_sites():
        city_rows.extend(
            evaluate_units(s.ta_c, s.rh_pct, BUS, mode="fluids", site_label=s.key)
        )
    _write_rows(OUT / "task4_eight_cities.csv", city_rows)

    # Phoenix-like empty feasible check
    phoenix = evaluate_units(42.0, 20.0, BUS, mode="fluids", site_label="Phoenix_demo")
    _write_rows(OUT / "phoenix_safety_demo.csv", phoenix)
    print(
        "Phoenix feasible:",
        [r.unit_id for r in phoenix if r.feasible],
        "felt",
        [round(r.t_felt_c, 1) for r in phoenix],
    )

    plt = _try_plot()
    if plt:
        fig_crossover(plt)
        fig_eight_cities(plt, city_rows)
        fig_platform_flip(plt, bus, rail)
        fig_delivery_bars(plt, bus)
        print("Figures →", FIG)
    else:
        # still write crossover summary
        with (OUT / "crossover_summary.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["label", "dn", "rh_star_pct", "dtwb_star_k"])
            for c in (
                crossover_v7_claimed(),
                crossover_legacy_decay(),
                crossover_fluids_coupled(),
            ):
                w.writerow([c.label, f"{c.dn:.4f}", f"{c.rh_star_pct:.1f}", f"{c.dtwb_star_k:.3f}"])
        print("matplotlib missing; CSV only")

    print("Bus CEI:", [(r.unit_id, round(r.cei, 3), r.feasible) for r in bus])
    print("Rail CEI:", [(r.unit_id, round(r.cei, 3), r.feasible) for r in rail])


if __name__ == "__main__":
    main()
