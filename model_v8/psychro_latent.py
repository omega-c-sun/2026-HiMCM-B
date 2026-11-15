"""Humidity-dependent pad efficiency and latent/condensation correction."""

from __future__ import annotations

import math
from dataclasses import dataclass

from .psychro import wet_bulb_depression, wet_bulb_stull

H_FG = 2501e3  # J/kg latent heat approx at 0 C
RHO = 1.2
CP = 1006.0
EPS0 = 0.78


def dew_point_c(ta_c: float, rh_pct: float) -> float:
    """Magnus approximation from dry-bulb and RH%."""
    rh = max(1e-3, min(100.0, rh_pct)) / 100.0
    a, b = 17.625, 243.04
    gamma = (a * ta_c / (b + ta_c)) + math.log(rh)
    return b * gamma / (a - gamma)


def humidity_ratio(ta_c: float, rh_pct: float, p_hpa: float = 1013.25) -> float:
    """W ≈ 0.622 * e / (p - e); e from RH * es(T)."""
    rh = max(0.0, min(100.0, rh_pct)) / 100.0
    # Buck saturation vapor pressure (hPa)
    es = 6.1121 * math.exp((18.678 - ta_c / 234.5) * (ta_c / (257.14 + ta_c)))
    e = rh * es
    p = max(p_hpa, e + 1.0)
    return 0.622 * e / (p - e)


def eps_pad(rh_pct: float, *, eps0: float = EPS0) -> float:
    """
    Weak RH penalty on pad effectiveness.
    Near-dry ≈ eps0; declines toward high humidity (still >0.35).
    """
    rh = max(0.0, min(100.0, rh_pct)) / 100.0
    # g(RH) = 1 - 0.55*rh^1.4  → at RH=0.85 ≈ 0.58 of eps0 scale factor
    g = 1.0 - 0.55 * (rh**1.4)
    return max(0.35, eps0 * g)


@dataclass
class OutletState:
    delta_t0_k: float
    eps: float
    t_s_c: float
    t_dp_c: float
    q_lat_w: float
    condensed: bool
    notes: str


def evaporative_outlet(
    ta_c: float,
    rh_pct: float,
    delta_t_nom_k: float,
    vdot_sup_m3_s: float,
    *,
    use_eps_rh: bool = True,
    use_latent: bool = True,
    p_hpa: float = 1013.25,
) -> OutletState:
    """
    Catalogue-capped wet-bulb-limited supply drop, optionally reduced by latent release
    when supply would sit below dew point or RH is extreme.
    """
    eps = eps_pad(rh_pct) if use_eps_rh else EPS0
    dtwb = wet_bulb_depression(ta_c, rh_pct)
    d_t0 = min(delta_t_nom_k, eps * dtwb)
    t_s = ta_c - d_t0
    t_dp = dew_point_c(ta_c, rh_pct)
    q_lat = 0.0
    condensed = False
    notes = "sensible"

    if use_latent and (t_s < t_dp - 0.1 or rh_pct >= 85.0):
        condensed = True
        # Assume leaving air near saturation at Ts → W_out from RH≈95% at Ts
        w_in = humidity_ratio(ta_c, rh_pct, p_hpa)
        w_out = humidity_ratio(t_s, 95.0, p_hpa)
        dw = max(0.0, w_in - w_out)
        m_a = RHO * max(vdot_sup_m3_s, 1e-6)  # kg/s
        q_lat = m_a * dw * H_FG  # W
        # Latent release offsets sensible cooling of the supply stream
        d_offset = q_lat / (m_a * CP) if m_a > 1e-9 else 0.0
        d_t0 = max(0.0, d_t0 - d_offset)
        t_s = ta_c - d_t0
        notes = f"latent offset {d_offset:.2f}K"

    return OutletState(d_t0, eps, t_s, t_dp, q_lat, condensed, notes)
