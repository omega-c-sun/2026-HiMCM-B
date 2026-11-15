"""Crossover ablation: baseline eps vs eps(RH) vs eps(RH)+latent."""

from __future__ import annotations

import csv
from pathlib import Path

from .crossover import crossover_fluids_coupled
from .m2_feel import wind_credit
from .m3_cei import evaluate_units
from .psychro import scan_crossover_rh, wet_bulb_depression
from .psychro_latent import eps_pad
from .units import BUS, EPS_PAD, UNITS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs_v8"


def coupled_crossover(use_eps_rh: bool, use_latent: bool, label: str):
    from .m1_fluids import deliver
    from .m2_feel import feel

    ta = 33.5
    wf = wind_credit(UNITS["A"].v_seat_m_s)
    rows = []
    best_rh, best_err, dn_ref = 55.0, 1e9, 0.0
    for rh in range(15, 96):
        m1 = deliver(
            UNITS["B"],
            BUS,
            ta,
            float(rh),
            mode="fluids",
            use_eps_rh=use_eps_rh,
            use_latent=use_latent,
        )
        m2 = feel(UNITS["B"], m1, ta)
        rows.append((float(rh), wf, m2.delta_teq_k))
        err = abs(m2.delta_teq_k - wf)
        if err < best_err:
            best_err = err
            best_rh = float(rh)
            dn_ref = m1.dn
    return {
        "label": label,
        "dn": round(dn_ref, 4),
        "rh_star_pct": best_rh,
        "use_eps_rh": int(use_eps_rh),
        "use_latent": int(use_latent),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    out = [
        coupled_crossover(False, False, "fixed_eps_no_latent"),
        coupled_crossover(True, False, "eps_rh_only"),
        coupled_crossover(True, True, "eps_rh_plus_latent"),
    ]
    # Singapore stress
    for label, eps_rh, lat in [
        ("singapore_fixed", False, False),
        ("singapore_full", True, True),
    ]:
        rows = evaluate_units(
            31.0,
            82.0,
            BUS,
            mode="fluids",
            site_label="Singapore",
            use_eps_rh=eps_rh,
            use_latent=lat,
        )
        by = {r.unit_id: r for r in rows}
        out.append(
            {
                "label": label,
                "dn": round(by["B"].dn, 4),
                "rh_star_pct": "",
                "use_eps_rh": int(eps_rh),
                "use_latent": int(lat),
                "dTeq_A": round(by["A"].delta_teq_k, 3),
                "dTeq_B": round(by["B"].delta_teq_k, 3),
                "margin": round(by["B"].delta_teq_k - by["A"].delta_teq_k, 3),
                "eps_B": round(by["B"].eps, 3),
                "condensed_B": int(by["B"].condensed),
            }
        )

    path = OUT / "latent_ablation.csv"
    # unify keys
    keys = sorted({k for r in out for k in r})
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r)
    print("Wrote", path)


if __name__ == "__main__":
    main()
