"""Analytic / numeric RH crossover between fan and evaporative felt benefit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from .m1_fluids import deliver, legacy_decay, legacy_dn_claimed
from .m2_feel import wind_credit
from .psychro import scan_crossover_rh, wet_bulb_depression
from .units import BUS, EPS_PAD, UNITS


@dataclass
class CrossoverResult:
    label: str
    ta_c: float
    dn: float
    rh_star_pct: float
    dtwb_star_k: float
    rows: List[Tuple[float, float, float]]  # rh, fan, evap


def crossover_v7_claimed(ta_c: float = 33.5) -> CrossoverResult:
    """Reproduce v7 signature: Dn=0.64, Wf=3.20, We=0.32 → ~63%."""
    dn = legacy_dn_claimed()
    wf = wind_credit(UNITS["A"].v_seat_m_s)
    we = wind_credit(UNITS["B"].v_seat_m_s)
    rh, rows = scan_crossover_rh(ta_c, eps=EPS_PAD, dn=dn, w_fan=wf, w_evap_wind=we)
    dtwb = (wf - we) / (EPS_PAD * dn)
    return CrossoverResult("v7_claimed_Dn0.64", ta_c, dn, rh, dtwb, rows)


def crossover_legacy_decay(ta_c: float = 33.5) -> CrossoverResult:
    """Same algebra but Dn from dimensionless decay(6) ≈ 0.47."""
    dn = legacy_decay(6.0)
    wf = wind_credit(UNITS["A"].v_seat_m_s)
    we = wind_credit(UNITS["B"].v_seat_m_s)
    rh, rows = scan_crossover_rh(ta_c, eps=EPS_PAD, dn=dn, w_fan=wf, w_evap_wind=we)
    dtwb = (wf - we) / (EPS_PAD * dn)
    return CrossoverResult("legacy_decay_Dn", ta_c, dn, rh, dtwb, rows)


def crossover_fluids(ta_c: float = 33.5, k_sc: float = 1.0) -> CrossoverResult:
    """
    Use fluids-layer Dn = η_mix at a representative mid RH, then scan.
    (Full coupling would recompute mix each RH; mid-RH Dn is the ablation proxy.)
    """
    unit = UNITS["B"]
    m1 = deliver(unit, BUS, ta_c, 55.0, mode="fluids", k_sc=k_sc)
    dn = max(m1.dn, 0.05)
    wf = wind_credit(UNITS["A"].v_seat_m_s)
    we = wind_credit(unit.v_seat_m_s)
    rh, rows = scan_crossover_rh(ta_c, eps=EPS_PAD, dn=dn, w_fan=wf, w_evap_wind=we)
    dtwb = (wf - we) / (EPS_PAD * dn)
    return CrossoverResult("fluids_eta_mix", ta_c, dn, rh, dtwb, rows)


def crossover_fluids_coupled(ta_c: float = 33.5, k_sc: float = 1.0) -> CrossoverResult:
    """Recompute evaporative felt at each RH via M1+M2 delivery."""
    from .m2_feel import feel

    rows: List[Tuple[float, float, float]] = []
    wf = wind_credit(UNITS["A"].v_seat_m_s)
    best_rh, best_err = 55.0, 1e9
    dn_ref = 0.0
    for rh in range(15, 96):
        m1 = deliver(UNITS["B"], BUS, ta_c, float(rh), mode="fluids", k_sc=k_sc)
        m2 = feel(UNITS["B"], m1, ta_c)
        felt_e = m2.delta_teq_k
        rows.append((float(rh), wf, felt_e))
        err = abs(felt_e - wf)
        if err < best_err:
            best_err = err
            best_rh = float(rh)
            dn_ref = m1.dn
    dtwb = wet_bulb_depression(ta_c, best_rh)
    return CrossoverResult("fluids_coupled", ta_c, dn_ref, best_rh, dtwb, rows)
