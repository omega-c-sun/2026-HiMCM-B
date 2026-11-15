# elementary fluids: wind+stack, eta_mix, zone balance, jet
import math
from typing import List, Sequence, Tuple
from dataclasses import dataclass
from core.a import R, C, G, H, L

CW, CT, CD = 0.55, 0.40, 0.02


def eo(o: float) -> float:
    o = max(0.0, min(1.0, o))
    return 0.35 + 0.65 * o


def vx(h: H, c: L, dt: float, cw=CW, ct=CT, cd=CD) -> float:
    tk = c.t + 273.15
    w = cw * h.ao * max(c.w, 0.0)
    st = ct * h.ao * math.sqrt(max(0.0, 2.0 * G * h.ho * abs(dt) / tk))
    return (w + st) * eo(h.o) * cd


def ach_v(h: H, v: float) -> float:
    return max(h.am, v * 3600.0 / max(h.v, 1e-6))


def uach(h: H, c: L, dt: float, cw=CW, ct=CT):
    v = vx(h, c, dt, cw=cw, ct=ct)
    a = ach_v(h, v)
    return a, a * h.v / 3600.0


def em(h: H, ve: float, vs: float, k: float = 1.0) -> float:
    if vs <= 1e-9:
        return 0.0
    ar = h.ao / max(h.a, 1e-6)
    return 1.0 / (1.0 + max(0.0, k) * ar * (ve / vs))


@dataclass
class Z:
    tz: float
    ts: float
    vs: float
    ve: float
    m: float
    qp: float
    qu: float
    fu: float
    ach: float
    dtz: float


def bal(c: L, h: H, vs: float, dts: float, qg: float = 0.0, k: float = 1.0) -> Z:
    dts = max(0.0, dts)
    ts = c.t - dts
    _, ve = uach(h, c, dts)
    m = em(h, ve, vs, k=k)
    d = max(vs + ve, 1e-9)
    tz = (vs * ts + ve * c.t + qg / (R * C)) / d
    ach, ve = uach(h, c, abs(c.t - tz))
    m = em(h, ve, vs, k=k)
    d = max(vs + ve, 1e-9)
    tz = (vs * ts + ve * c.t + qg / (R * C)) / d
    qp = R * C * vs * dts
    qu = qp * m
    return Z(tz, ts, vs, ve, m, qp, qu, m if qp > 0 else 0.0, ach, max(0.0, c.t - tz))


def ux(x: float, u0: float, lj: float) -> float:
    return u0 / (1.0 + max(x, 0.0) / max(lj, 1e-6))


def uo(st: Sequence[Tuple[float, float]], u0: float, lj: float) -> float:
    if not st:
        return u0
    num = den = 0.0
    for x, w in st:
        ww = max(0.0, w)
        num += ux(x, u0, lj) * ww
        den += ww
    return num / den if den > 0 else u0


B0: List[Tuple[float, float]] = [(0.8, 0.45), (1.8, 0.35), (3.2, 0.20)]
B1: List[Tuple[float, float]] = [(1.5, 0.40), (4.0, 0.35), (8.0, 0.25)]


def u0p(p: float, o: float) -> float:
    return (1.2 + 3.5 * math.sqrt(max(p, 0.05))) * (0.9 + 0.1 * o)


def lj(h: H) -> float:
    return max(1.2, 0.45 * math.sqrt(max(h.a, 1.0)))


def tmrt(c: L, sh: float = 0.5, I: float = 800.0, a: float = 0.018) -> float:
    s = max(0.0, min(1.0, sh))
    return c.t + a * max(I, 0.0) * (1.0 - s)


def dpet(c: L, h: H, da: float, df: float, sh: float = 0.55, I: float = 800.0) -> float:
    return max(0.0, tmrt(c, 0.0, I) - tmrt(c, sh, I)) * 0.35 + 1.2 * (1.0 - h.o) + abs(da) + 0.7 * abs(df)


def st_for(h: H):
    return list(B0 if h.a <= 30 else B1)
