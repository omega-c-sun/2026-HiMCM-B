"""M3: entropy-weighted CEI (deduped), TOPSIS, safety + budget gates."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .m1_fluids import deliver
from .m2_feel import feel, rar_safety_weighted
from .units import (
    BUS,
    BUS_STATIONS,
    CAPEX,
    DISCOUNT,
    ELEC_USD_PER_KWH,
    HOURS_YR_CEI,
    HOURS_YR_LCC,
    LIFETIME_YR,
    MAINT,
    RAIL,
    RAIL_STATIONS,
    T_SAFETY_MAX_C,
    UNITS,
    WATER_USD_PER_M3,
    ShelterGeom,
    Unit,
)

# v7 Listing 3 matrix — regression only (includes rated P)
V7_X = np.array(
    [
        [3.20, 13.9, 1.00, 0.25, 0.98, 0.0],
        [3.93, 5.9, 1.00, 1.20, 4.70, 260.0],
        [4.36, 4.2, 0.86, 2.50, 9.80, 540.0],
    ],
    dtype=float,
)
V7_SIGN = np.array([1, 1, 1, -1, -1, -1], dtype=float)
V7_CEI_TARGET = np.array([0.849, 0.541, 0.130])


def _pv_factor(rate: float, years: int) -> float:
    if years <= 0:
        return 0.0
    if rate > 0:
        return (1.0 - (1.0 + rate) ** (-years)) / rate
    return float(years)


def annual_energy_cost_kusd(power_kw: float) -> float:
    return power_kw * HOURS_YR_CEI * ELEC_USD_PER_KWH / 1000.0


def lifecycle_usd(unit: Unit) -> float:
    e_annual = unit.power_kw * HOURS_YR_LCC
    water = unit.water_m3_yr * (HOURS_YR_LCC / HOURS_YR_CEI)
    maint = MAINT[unit.id]
    annual = e_annual * ELEC_USD_PER_KWH + water * WATER_USD_PER_M3 + maint
    return CAPEX[unit.id] + annual * _pv_factor(DISCOUNT, LIFETIME_YR)


def entropy_weights(x_norm: np.ndarray) -> np.ndarray:
    n = x_norm.shape[0]
    p = x_norm / np.maximum(x_norm.sum(axis=0), 1e-12)
    e = -(p * np.log(p + 1e-12)).sum(axis=0) / math.log(n)
    d = 1.0 - e
    return d / max(d.sum(), 1e-12)


def minmax_normalize(x: np.ndarray, sign: np.ndarray) -> np.ndarray:
    xmin = x.min(axis=0)
    xmax = x.max(axis=0)
    span = np.maximum(xmax - xmin, 1e-12)
    xn = (x - xmin) / span
    return np.where(sign > 0, xn, 1.0 - xn)


def cei_from_matrix(
    x: np.ndarray,
    sign: np.ndarray,
    rar: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    xn = minmax_normalize(x, sign)
    w = entropy_weights(xn)
    score = (xn * w).sum(axis=1)
    if rar is None:
        rar = x[:, 2]
    a = np.where(rar >= 0.90, 1.0, rar)
    return score * a, w, xn


def topsis(x_norm: np.ndarray, w: np.ndarray) -> np.ndarray:
    v = x_norm * w
    ideal = v.max(axis=0)
    nadir = v.min(axis=0)
    dp = np.sqrt(((v - ideal) ** 2).sum(axis=1))
    dn = np.sqrt(((v - nadir) ** 2).sum(axis=1))
    return dn / np.maximum(dn + dp, 1e-12)


def reproduce_v7_cei() -> Dict[str, np.ndarray]:
    cei, w, xn = cei_from_matrix(V7_X, V7_SIGN)
    t = topsis(xn, w)
    return {"cei": cei, "weights": w, "topsis": t, "target": V7_CEI_TARGET}


@dataclass
class EvalRow:
    unit_id: str
    mode: str
    site: str
    shelter: str
    ta_c: float
    rh_pct: float
    dn: float
    delta_tz_k: float
    delta_teq_k: float
    scd: float
    rar: float
    rar_dteq3: float
    power_kw: float
    cost_kusd_yr: float
    water_m3_yr: float
    f_occ: float
    t_felt_c: float
    safety_ok: bool
    lcc_usd: float
    budget_ok: bool
    water_ok: bool
    feasible: bool
    k_sc: float = 1.0
    eps: float = 0.78
    condensed: bool = False
    cei: float = float("nan")
    topsis: float = float("nan")


def _scd(delta_teq: float, vdot: float, power_kw: float) -> float:
    if power_kw <= 1e-9:
        return 0.0
    q_kw = 1.2 * 1006.0 * max(vdot, 0.05) * max(delta_teq, 0.0) / 1000.0
    return q_kw / power_kw


def rar_dteq3(delta_teq: float, target: float = 3.0) -> float:
    if delta_teq >= target:
        return 1.0
    if delta_teq <= 0:
        return 0.0
    return max(0.0, min(1.0, delta_teq / target))


def _stations_for(shelter: ShelterGeom):
    return BUS_STATIONS if shelter.openness >= 0.8 else RAIL_STATIONS


def evaluate_units(
    ta_c: float,
    rh_pct: float,
    shelter: ShelterGeom,
    *,
    mode: str = "fluids",
    use_claimed_dn: bool = False,
    k_sc: float | None = None,
    site_label: str = "",
    use_eps_rh: bool = True,
    use_latent: bool = True,
    drop_rated_power: bool = True,
) -> List[EvalRow]:
    rows: List[EvalRow] = []
    stations = _stations_for(shelter)
    for uid, unit in UNITS.items():
        m1 = deliver(
            unit,
            shelter,
            ta_c,
            rh_pct,
            mode=mode,  # type: ignore[arg-type]
            use_claimed_dn=use_claimed_dn,
            k_sc=k_sc if k_sc is not None else unit.k_sc,
            use_eps_rh=use_eps_rh,
            use_latent=use_latent,
        )
        m2 = feel(unit, m1, ta_c)
        vdot = unit.vdot_sup_m3_s if unit.kind == "evaporative" else 0.35
        scd = _scd(m2.delta_teq_k, vdot, unit.power_kw)
        rar = rar_safety_weighted(unit, m1, ta_c, stations)
        rar3 = rar_dteq3(m2.delta_teq_k)
        cost = annual_energy_cost_kusd(unit.power_kw)
        lcc = lifecycle_usd(unit)
        safety = m2.t_felt_c <= T_SAFETY_MAX_C and m2.delta_teq_k > 0
        budget = lcc <= shelter.budget_usd + 1e-6
        water_ok = True  # optional cap inactive
        rows.append(
            EvalRow(
                unit_id=uid,
                mode=mode,
                site=site_label,
                shelter=shelter.name,
                ta_c=ta_c,
                rh_pct=rh_pct,
                dn=m1.dn,
                delta_tz_k=m1.delta_tz_k,
                delta_teq_k=m2.delta_teq_k,
                scd=scd,
                rar=rar,
                rar_dteq3=rar3,
                power_kw=unit.power_kw,
                cost_kusd_yr=cost,
                water_m3_yr=unit.water_m3_yr,
                f_occ=unit.f_occ,
                t_felt_c=m2.t_felt_c,
                safety_ok=safety,
                lcc_usd=lcc,
                budget_ok=budget,
                water_ok=water_ok,
                feasible=bool(safety and budget and water_ok),
                k_sc=unit.k_sc if k_sc is None else k_sc,
                eps=m1.eps,
                condensed=m1.condensed,
            )
        )

    if drop_rated_power:
        # ΔTeq, SCD, RAR, energy_cost, water, f_occ
        x = np.array(
            [
                [r.delta_teq_k, r.scd, r.rar, r.cost_kusd_yr, r.water_m3_yr, r.f_occ]
                for r in rows
            ],
            dtype=float,
        )
        sign = np.array([1, 1, 1, -1, -1, 1], dtype=float)
    else:
        x = np.array(
            [
                [
                    r.delta_teq_k,
                    r.scd,
                    r.rar,
                    r.power_kw,
                    r.cost_kusd_yr,
                    r.water_m3_yr,
                    r.f_occ,
                ]
                for r in rows
            ],
            dtype=float,
        )
        sign = np.array([1, 1, 1, -1, -1, -1, 1], dtype=float)

    cei, w, xn = cei_from_matrix(x, sign, rar=x[:, 2])
    t = topsis(xn, entropy_weights(minmax_normalize(x, sign)))
    for i, r in enumerate(rows):
        r.cei = float(cei[i])
        r.topsis = float(t[i])
    return rows


def rank_feasible(rows: Sequence[EvalRow]) -> List[EvalRow]:
    return sorted([r for r in rows if r.feasible], key=lambda r: r.cei, reverse=True)


def cei_matrix_and_weights(rows: Sequence[EvalRow], drop_rated_power: bool = True):
    if drop_rated_power:
        x = np.array(
            [
                [r.delta_teq_k, r.scd, r.rar, r.cost_kusd_yr, r.water_m3_yr, r.f_occ]
                for r in rows
            ],
            dtype=float,
        )
        sign = np.array([1.0, 1.0, 1.0, -1.0, -1.0, 1.0])
        names = ["dTeq", "SCD", "RAR", "energy", "water", "f_occ"]
    else:
        x = np.array(
            [
                [
                    r.delta_teq_k,
                    r.scd,
                    r.rar,
                    r.power_kw,
                    r.cost_kusd_yr,
                    r.water_m3_yr,
                    r.f_occ,
                ]
                for r in rows
            ],
            dtype=float,
        )
        sign = np.array([1.0, 1.0, 1.0, -1.0, -1.0, -1.0, 1.0])
        names = ["dTeq", "SCD", "RAR", "P", "energy", "water", "f_occ"]
    cei, w, xn = cei_from_matrix(x, sign, rar=x[:, 2])
    return x, sign, names, cei, w, xn
