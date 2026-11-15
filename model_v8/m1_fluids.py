"""M1: does the cold arrive?

Two modes:
  - legacy: v7 composite jet decay with fixed Dn (for ablation baseline / regression)
  - fluids: 18388 elementary exchange + short-circuit mixing (physical delivery fraction)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from .psychro import wet_bulb_depression
from .psychro_latent import evaporative_outlet
from .units import EPS_PAD, ShelterGeom, Unit

Mode = Literal["legacy", "fluids"]

RHO = 1.2
CP = 1006.0
CW, CT, CD = 0.55, 0.40, 0.02
G = 9.81


@dataclass
class M1Result:
    mode: str
    delta_t0_k: float
    dn: float
    delta_t_path_k: float
    gain_penalty_k: float
    delta_tz_k: float
    vdot_ex: float
    eta_mix: float
    ach: float
    notes: str = ""
    eps: float = EPS_PAD
    q_lat_w: float = 0.0
    condensed: bool = False


def _eta_open(o: float) -> float:
    o = max(0.0, min(1.0, o))
    return 0.35 + 0.65 * o


def _vdot_ex(shelter: ShelterGeom, ta_c: float, delta_t: float) -> float:
    t_k = ta_c + 273.15
    wind = CW * shelter.a_open_m2 * max(shelter.wind_m_s, 0.0)
    stack = CT * shelter.a_open_m2 * math.sqrt(
        max(0.0, 2.0 * G * shelter.h_open_m * abs(delta_t) / t_k)
    )
    return (wind + stack) * _eta_open(shelter.openness) * CD


def _ach(shelter: ShelterGeom, vdot: float) -> float:
    return max(shelter.ach_min, vdot * 3600.0 / max(shelter.volume_m3, 1e-6))


def _eta_mix(shelter: ShelterGeom, vdot_ex: float, vdot_sup: float, k_sc: float) -> float:
    if vdot_sup <= 1e-9:
        return 1.0
    a_ratio = shelter.a_open_m2 / max(shelter.area_m2, 1e-6)
    return 1.0 / (1.0 + max(0.0, k_sc) * a_ratio * (vdot_ex / vdot_sup))


def legacy_decay(r: float, b: float = 0.219, lb_dimless: float = 18.1) -> float:
    return (1.0 / math.sqrt(1.0 + b * r)) * math.exp(-r / lb_dimless)


def legacy_dn_claimed() -> float:
    return 0.64


def gain_penalty_k(shelter: ShelterGeom, vdot_sup: float, n_ach: float | None = None) -> float:
    if vdot_sup > 1e-6:
        vdot = vdot_sup
    else:
        ach = n_ach if n_ach is not None else shelter.ach_min
        vdot = ach * shelter.volume_m3 / 3600.0
    return (shelter.q_gain_kw * 1000.0) / (RHO * CP * max(vdot, 1e-6))


def deliver_legacy(
    unit: Unit,
    shelter: ShelterGeom,
    ta_c: float,
    rh_pct: float,
    *,
    use_claimed_dn: bool = False,
    x_over_h0: float = 6.0,
) -> M1Result:
    if unit.kind == "fan":
        pen = gain_penalty_k(
            shelter, 0.9, n_ach=12.0 if shelter.openness >= 0.8 else 15.0
        )
        d_tz = -pen if shelter.q_gain_kw >= 0.5 else 0.0
        return M1Result("legacy", 0.0, 1.0, 0.0, pen, d_tz, 0.9, 1.0, 12.0, "fan thermal=0")

    d_t0 = unit.delta_t0_k
    dn = legacy_dn_claimed() if use_claimed_dn else legacy_decay(x_over_h0)
    path = d_t0 * dn
    pen = gain_penalty_k(shelter, unit.vdot_sup_m3_s or 0.9, n_ach=12.0)
    d_tz = path - pen if path > 0 else -pen
    return M1Result(
        "legacy", d_t0, dn, path, pen, d_tz, unit.vdot_sup_m3_s or 0.9, dn, 12.0, "legacy jet+gain"
    )


def deliver_fluids(
    unit: Unit,
    shelter: ShelterGeom,
    ta_c: float,
    rh_pct: float,
    *,
    k_sc: float | None = None,
    use_eps_rh: bool = True,
    use_latent: bool = True,
) -> M1Result:
    k = unit.k_sc if k_sc is None else k_sc
    if unit.kind == "fan":
        vdot_ex0 = _vdot_ex(shelter, ta_c, 1.0)
        ach = _ach(shelter, vdot_ex0)
        vdot_ex = ach * shelter.volume_m3 / 3600.0
        pen = (shelter.q_gain_kw * 1000.0) / (RHO * CP * max(vdot_ex, 1e-6))
        d_tz = -pen if shelter.q_gain_kw >= 0.5 else 0.0
        return M1Result("fluids", 0.0, 1.0, 0.0, pen, d_tz, vdot_ex, 1.0, ach, "fan f_util=1")

    out = evaporative_outlet(
        ta_c,
        rh_pct,
        unit.delta_t0_k,
        unit.vdot_sup_m3_s,
        use_eps_rh=use_eps_rh,
        use_latent=use_latent,
    )
    d_t0 = out.delta_t0_k
    vdot_sup = max(unit.vdot_sup_m3_s, 1e-6)
    vdot_ex = _vdot_ex(shelter, ta_c, max(d_t0, 0.5))
    ach = _ach(shelter, vdot_ex)
    vdot_ex = ach * shelter.volume_m3 / 3600.0
    mix = _eta_mix(shelter, vdot_ex, vdot_sup, k)
    t_s = out.t_s_c
    q_gain = shelter.q_gain_kw * 1000.0 + out.q_lat_w  # condensed heat enters zone budget
    denom = vdot_sup + vdot_ex
    t_z = (vdot_sup * t_s + vdot_ex * ta_c + q_gain / (RHO * CP)) / max(denom, 1e-9)
    vdot_ex = _vdot_ex(shelter, ta_c, abs(ta_c - t_z))
    ach = _ach(shelter, vdot_ex)
    vdot_ex = ach * shelter.volume_m3 / 3600.0
    mix = _eta_mix(shelter, vdot_ex, vdot_sup, k)
    denom = vdot_sup + vdot_ex
    t_z = (vdot_sup * t_s + vdot_ex * ta_c + q_gain / (RHO * CP)) / max(denom, 1e-9)
    d_tz = max(0.0, ta_c - t_z)
    path = d_t0 * mix
    pen = max(0.0, path - d_tz)
    return M1Result(
        "fluids",
        d_t0,
        mix,
        path,
        pen,
        d_tz,
        vdot_ex,
        mix,
        ach,
        out.notes,
        eps=out.eps,
        q_lat_w=out.q_lat_w,
        condensed=out.condensed,
    )


def deliver(
    unit: Unit,
    shelter: ShelterGeom,
    ta_c: float,
    rh_pct: float,
    *,
    mode: Mode = "fluids",
    use_claimed_dn: bool = False,
    k_sc: float | None = None,
    use_eps_rh: bool = True,
    use_latent: bool = True,
) -> M1Result:
    if mode == "legacy":
        return deliver_legacy(unit, shelter, ta_c, rh_pct, use_claimed_dn=use_claimed_dn)
    return deliver_fluids(
        unit,
        shelter,
        ta_c,
        rh_pct,
        k_sc=k_sc,
        use_eps_rh=use_eps_rh,
        use_latent=use_latent,
    )
