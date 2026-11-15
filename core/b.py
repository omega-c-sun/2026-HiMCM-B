# V1 physics: RH penalty, fan dT, ACH, util, phi
import math
from .a import R, C, G, S, H, L


def gr(rh: float) -> float:
    rh = max(0.0, min(1.0, rh))
    return max(0.05, 1.15 - rh)


def fdt(dt: float, t: float, rh: float, u: float = 2.0) -> float:
    sk = 34.0
    uf = min(1.3, 0.65 + 0.22 * max(u, 0.3))
    dry = 1.0 - max(0.0, min(1.0, rh))
    if t < sk:
        tf = 0.75 + 0.25 * min(1.0, (sk - t) / 10.0)
        rf = max(0.35, 0.55 + 0.55 * dry)
        x = dt * uf * tf * rf
    else:
        ov = (t - sk) / 12.0
        x = dt * uf * dry * max(0.0, 1.0 - 0.55 * ov)
        if rh >= 0.75:
            x = min(x, 0.0) - 0.4 * (rh - 0.75)
    return x


def edt(s: S, c: L) -> float:
    return s.dt * gr(c.rh)


def ach_s(h: H, c: L, dt: float) -> float:
    cw, ct = 0.55, 0.40
    tk = c.t + 273.15
    w = cw * h.ao * c.w
    st = ct * h.ao * math.sqrt(max(0.0, 2.0 * G * h.ho * abs(dt) / tk))
    a = (w + st) / h.v * (0.4 + 0.6 * h.o)
    return max(h.am, a)


def ach_o(h: H, c: L) -> float:
    return max(h.am, 12.0 + 18.0 * c.w * h.o)


def vex(h: H, a: float) -> float:
    return a * h.v / 3600.0


def qv(v: float, t0: float, tt: float) -> float:
    return R * C * v * max(0.0, t0 - tt)


def fu(qc: float, qvent: float) -> float:
    if qc <= 0:
        return 0.0
    return qc / (qc + max(0.0, qvent))


def phi_t(de: float, dn: float) -> float:
    if dn <= 0:
        return 0.0
    return max(0.0, de / dn)


def phi_p(dp: float, dn: float = 5.0) -> float:
    if dn <= 0:
        return 0.0
    x = max(0.0, dp) / dn
    return min(1.0, x) if x <= 1.0 else min(1.0, x) / (1.0 + 0.5 * (x - 1.0))


def dpet(c: L, da: float, df: float, h: H) -> float:
    return 1.5 * (1.0 - h.o) + abs(da) + 0.7 * abs(df)
