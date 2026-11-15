"""Plot diurnal RH for Tianjin / Singapore / Atlanta from Open-Meteo cache."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIURNAL = ROOT / "data" / "diurnal"
FIG = ROOT / "paper" / "figures"
OUT = ROOT / "outputs_v8"


def load(site: str):
    p = DIURNAL / f"{site}.csv"
    if not p.exists():
        return [], []
    hours, rhs = [], []
    with p.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t = r["time"]
            hours.append(int(t[11:13]))
            rhs.append(float(r["rh_pct"]))
    return hours, rhs


def main() -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        print("skip", e)
        return
    FIG.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for site, label in [
        ("tianjin", "Tianjin"),
        ("singapore", "Singapore"),
        ("atlanta", "Atlanta"),
    ]:
        h, rh = load(site)
        if h:
            ax.plot(h, rh, label=label)
    ax.axhline(63, color="0.4", ls="--", lw=1, label="v7 RH* = 63%")
    ax.axhline(64, color="0.2", ls=":", lw=1, label="fluids RH* ≈ 64%")
    ax.set_xlabel("Local hour")
    ax.set_ylabel("RH (%)")
    ax.set_title("Diurnal humidity (Open-Meteo 2023-07-15) vs crossover")
    ax.set_xlim(0, 23)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "v8_diurnal_rh.png", dpi=160)
    fig.savefig(OUT / "v8_diurnal_rh.png", dpi=160)
    plt.close(fig)
    print("Wrote diurnal figure")


if __name__ == "__main__":
    main()
