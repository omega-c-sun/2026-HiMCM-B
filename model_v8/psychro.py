"""Psychrometrics helpers (Stull wet-bulb approximation used in v7 appendix)."""

from __future__ import annotations

import math
from typing import Iterable, List, Tuple


def wet_bulb_stull(ta_c: float, rh_pct: float) -> float:
    """Stull (2011) wet-bulb approximation; RH in percent 0–100."""
    rh = max(0.0, min(100.0, rh_pct))
    ta = ta_c
    return (
        ta * math.atan(0.151977 * (rh + 8.313659) ** 0.5)
        + math.atan(ta + rh)
        - math.atan(rh - 1.676331)
        + 0.00391838 * rh**1.5 * math.atan(0.023101 * rh)
        - 4.686035
    )


def wet_bulb_depression(ta_c: float, rh_pct: float) -> float:
    return max(0.0, ta_c - wet_bulb_stull(ta_c, rh_pct))


def rh_for_twb_target(ta_c: float, dtwb_target: float, rh_lo: float = 5.0, rh_hi: float = 99.0) -> float:
    """Invert Stull: find RH (%) such that (Ta - Twb) ≈ dtwb_target."""
    target_twb = ta_c - dtwb_target
    lo, hi = rh_lo, rh_hi
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        tw = wet_bulb_stull(ta_c, mid)
        if tw > target_twb:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def scan_crossover_rh(
    ta_c: float,
    *,
    eps: float,
    dn: float,
    w_fan: float,
    w_evap_wind: float,
    rh_grid: Iterable[float] | None = None,
) -> Tuple[float, List[Tuple[float, float, float]]]:
    """
    Find RH where evaporative felt ≈ fan felt:
      We + eps*(Ta-Twb)*Dn  ==  Wf
    Returns (rh_star_pct, rows of (rh, felt_fan, felt_evap)).
    """
    grid = list(rh_grid) if rh_grid is not None else list(range(15, 96))
    rows: List[Tuple[float, float, float]] = []
    best_rh = grid[0]
    best_err = 1e9
    for rh in grid:
        dtwb = wet_bulb_depression(ta_c, float(rh))
        felt_e = w_evap_wind + eps * dtwb * dn
        felt_f = w_fan
        rows.append((float(rh), felt_f, felt_e))
        err = abs(felt_e - felt_f)
        if err < best_err:
            best_err = err
            best_rh = float(rh)
    return best_rh, rows
