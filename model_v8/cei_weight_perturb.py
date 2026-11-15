"""Perturb CEI weights ±20% and report A vs B win rate (Tianjin bus)."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from .m3_cei import (
    cei_from_matrix,
    cei_matrix_and_weights,
    evaluate_units,
    minmax_normalize,
)
from .units import BUS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs_v8"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = evaluate_units(33.5, 55.0, BUS, mode="fluids", site_label="Tianjin")
    x, sign, names, cei0, w0, xn = cei_matrix_and_weights(rows, drop_rated_power=True)
    rng = np.random.default_rng(42)
    n = 400
    a_wins = 0
    b_wins = 0
    ties = 0
    for _ in range(n):
        jitter = rng.uniform(0.8, 1.2, size=len(w0))
        w = w0 * jitter
        w = w / w.sum()
        score = (xn * w).sum(axis=1)
        a = np.where(x[:, 2] >= 0.90, 1.0, x[:, 2])
        score = score * a
        # only among feasible
        feas = [i for i, r in enumerate(rows) if r.feasible]
        if not feas:
            continue
        best = max(feas, key=lambda i: score[i])
        uid = rows[best].unit_id
        if uid == "A":
            a_wins += 1
        elif uid == "B":
            b_wins += 1
        else:
            ties += 1  # C or other

    path = OUT / "cei_weight_perturb.csv"
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["n_trials", n])
        w.writerow(["A_wins", a_wins])
        w.writerow(["B_wins", b_wins])
        w.writerow(["other_wins", ties])
        w.writerow(["A_win_rate", a_wins / n])
        w.writerow(["B_win_rate", b_wins / n])
        for name, wi in zip(names, w0):
            w.writerow([f"w0_{name}", f"{wi:.4f}"])
        for name, ci in zip(["A", "B", "C"], cei0):
            w.writerow([f"cei0_{name}", f"{ci:.4f}"])
    print("weights", dict(zip(names, np.round(w0, 3))))
    print(f"A win rate {a_wins/n:.1%}  B win rate {b_wins/n:.1%}")
    print("Wrote", path)


if __name__ == "__main__":
    main()
