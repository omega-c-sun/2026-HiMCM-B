"""M2: Steadman-style apparent temperature with ASHRAE elevated-air-speed cap."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from .m1_fluids import M1Result
from .units import Unit

WIND_COEF = 2.1
WIND_CAP = 3.2
V_REF = 0.15


@dataclass
class M2Result:
    at_ambient_c: float
    at_zone_c: float
    delta_teq_k: float
    wind_credit_k: float
    t_felt_c: float


def wind_credit(v_m_s: float) -> float:
    return min(WIND_COEF * max(v_m_s - V_REF, 0.0), WIND_CAP)


def apparent_temp(tdb_c: float, v_m_s: float) -> float:
    return tdb_c - wind_credit(v_m_s)


def jet_speed(u0: float, x_m: float, l_jet: float = 2.5) -> float:
    return u0 / (1.0 + max(x_m, 0.0) / max(l_jet, 1e-6))


def feel(unit: Unit, m1: M1Result, ta_c: float, ambient_v: float = 0.2) -> M2Result:
    at_a = apparent_temp(ta_c, ambient_v)
    if unit.kind == "fan":
        if m1.delta_tz_k < 0:
            t_zone = ta_c + abs(m1.delta_tz_k)
            at_z = apparent_temp(t_zone, unit.v_seat_m_s)
            d_teq = at_a - at_z
        else:
            d_teq = wind_credit(unit.v_seat_m_s)
            at_z = ta_c - d_teq
        wc = wind_credit(unit.v_seat_m_s)
    else:
        wc = wind_credit(unit.v_seat_m_s)
        d_teq = max(m1.delta_tz_k, 0.0) + wc
        at_z = ta_c - d_teq
    t_felt = ta_c - d_teq
    return M2Result(at_a, at_z, d_teq, wc, t_felt)


def feel_at_stations(
    unit: Unit,
    m1: M1Result,
    ta_c: float,
    stations: Sequence[Tuple[float, float]],
) -> List[Tuple[float, float, float, bool]]:
    """
    Per-station (x, weight) -> (x, weight, delta_teq, safe).
    Evaporative: scale zone depression by jet survival proxy; fan: decay seat speed.
    """
    from .units import T_SAFETY_MAX_C

    rows = []
    u0 = unit.v_seat_m_s * 1.4 if unit.kind == "fan" else max(unit.v_seat_m_s * 2.0, 0.6)
    for x, w in stations:
        if unit.kind == "fan":
            v = jet_speed(u0, x)
            # local feel from wind; zone heating if any
            d = wind_credit(v)
            if m1.delta_tz_k < 0:
                d = d - abs(m1.delta_tz_k)
            t_felt = ta_c - d
        else:
            # delivery decays mildly with distance from device
            surv = 1.0 / (1.0 + x / 4.0)
            d = max(m1.delta_tz_k, 0.0) * surv + wind_credit(unit.v_seat_m_s * surv)
            t_felt = ta_c - d
        rows.append((x, w, d, t_felt <= T_SAFETY_MAX_C and d > 0))
    return rows


def rar_safety_weighted(
    unit: Unit,
    m1: M1Result,
    ta_c: float,
    stations: Sequence[Tuple[float, float]],
) -> float:
    seats = feel_at_stations(unit, m1, ta_c, stations)
    num = sum(w for _x, w, _d, ok in seats if ok)
    den = sum(w for _x, w, _d, _ok in seats)
    return num / den if den > 0 else 0.0
