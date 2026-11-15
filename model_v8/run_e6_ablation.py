"""E6 ablation: claimed-Dn chain vs fluids-coupled chain."""

from __future__ import annotations

import csv
from pathlib import Path

from .crossover import (
    crossover_fluids_coupled,
    crossover_legacy_decay,
    crossover_v7_claimed,
)
from .m3_cei import evaluate_units
from .sites import load_sites
from .units import BUS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs_v8"
FIG = ROOT / "paper" / "figures"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    rows = []
    for label, mode, claimed in [
        ("chain_claimed_Dn", "legacy", True),
        ("chain_legacy_decay", "legacy", False),
        ("chain_fluids", "fluids", False),
    ]:
        for s in load_sites():
            for r in evaluate_units(
                s.ta_c,
                s.rh_pct,
                BUS,
                mode=mode,
                use_claimed_dn=claimed,
                site_label=s.key,
            ):
                rows.append(
                    {
                        "ablation": label,
                        "site": s.key,
                        "unit": r.unit_id,
                        "dn": r.dn,
                        "delta_teq_k": r.delta_teq_k,
                        "cei": r.cei,
                        "feasible": int(r.feasible),
                        "safety_ok": int(r.safety_ok),
                        "budget_ok": int(r.budget_ok),
                        "t_felt_c": r.t_felt_c,
                    }
                )

    with (OUT / "e6_ablation_cities.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    crosses = [
        crossover_v7_claimed(),
        crossover_legacy_decay(),
        crossover_fluids_coupled(),
    ]
    with (OUT / "e6_crossover.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "dn", "rh_star_pct", "dtwb_star_k"])
        for c in crosses:
            w.writerow([c.label, f"{c.dn:.4f}", f"{c.rh_star_pct:.1f}", f"{c.dtwb_star_k:.3f}"])
            print(f"{c.label}: Dn={c.dn:.3f} RH*={c.rh_star_pct:.0f}%")

    try:
        import matplotlib.pyplot as plt
        import numpy as np

        # winner flip counts
        sites = sorted({r["site"] for r in rows})
        modes = ["chain_claimed_Dn", "chain_legacy_decay", "chain_fluids"]
        winners = {m: [] for m in modes}
        for m in modes:
            for s in sites:
                sub = [r for r in rows if r["ablation"] == m and r["site"] == s and r["feasible"]]
                if not sub:
                    winners[m].append("∅")
                else:
                    winners[m].append(max(sub, key=lambda r: r["cei"])["unit"])

        fig, ax = plt.subplots(figsize=(8.0, 3.6))
        x = np.arange(len(sites))
        for i, m in enumerate(modes):
            y = [ {"A": 3, "B": 2, "C": 1, "∅": 0}[w] for w in winners[m] ]
            ax.plot(x, y, "o-", label=m)
        ax.set_xticks(x)
        ax.set_xticklabels([s.replace("_", " ") for s in sites], rotation=30, ha="right")
        ax.set_yticks([0, 1, 2, 3])
        ax.set_yticklabels(["empty", "C", "B", "A"])
        ax.set_title("E6 ablation: CEI winner by site (feasible set)")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(FIG / "v8_e6_ablation.png", dpi=160)
        fig.savefig(OUT / "v8_e6_ablation.png", dpi=160)
        plt.close(fig)

        # crossover bars
        fig, ax = plt.subplots(figsize=(6.0, 3.6))
        ax.bar(range(3), [c.rh_star_pct for c in crosses], color=["#6c757d", "#adb5bd", "#2a6f97"])
        ax.set_xticks(range(3))
        ax.set_xticklabels([c.label for c in crosses], rotation=15, ha="right")
        ax.set_ylabel("Crossover RH* (%)")
        ax.set_title("E6: how much does RH* depend on delivery model?")
        fig.tight_layout()
        fig.savefig(FIG / "v8_e6_rh_star.png", dpi=160)
        fig.savefig(OUT / "v8_e6_rh_star.png", dpi=160)
        plt.close(fig)
    except Exception as e:
        print("plot skip:", e)

    print("Wrote", OUT / "e6_ablation_cities.csv")


if __name__ == "__main__":
    main()
