# dual-path eta_eff (v1 algebra + v2 fluids)
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
from core.a import R, C, QS, S, H, L, O
from core import b as ph
from fluid import c as fl


@dataclass
class R0:
    sid: str
    sn: str
    k: str
    pw: float
    dt: float
    qp: float
    fu: float
    fo: float
    phi: float
    qe: float
    eta: float
    ach: float
    nb: float
    tf: float
    note: str = ""
    m: float = 1.0
    u: float = 0.0
    mode: str = "v1"


def fo(o: O, de: float, dn: float) -> float:
    if dn <= 0 or de <= 0:
        return 0.0
    if de / dn < o.th:
        return 0.0
    return max(0.0, min(1.0, o.cf))


def eval(
    sid: str,
    s: S,
    h: H,
    c: L,
    o: O,
    *,
    so: bool = False,
    v2: bool = True,
    k: float = 1.0,
    sh: float = 0.55,
    I: float = 800.0,
    st: Optional[Sequence[Tuple[float, float]]] = None,
    qg: float = 0.0,
) -> R0:
    pw = s.p * 1000.0
    if s.k == "fan":
        return _fv2(sid, s, h, c, o, pw, so, st) if v2 else _fv1(sid, s, h, c, o, pw, so)
    return _ev2(sid, s, h, c, o, pw, so, k, sh, I, qg) if v2 else _ev1(sid, s, h, c, o, pw, so)


def _fv1(sid, s, h, c, o, pw, so) -> R0:
    u = 2.0 + 0.5 * c.w
    dt = ph.fdt(s.dt, c.t, c.rh, u) * ((0.85 + 0.15 * h.o) if so else 1.0)
    ach = ph.ach_s(h, c, abs(max(dt, 0.1))) if so else ph.ach_o(h, c)
    if dt <= 0:
        return R0(sid, s.n, s.k, pw, dt, 0, 1, 0, 0, 0, 0, ach, 0, c.t - dt, "fan1", u=u)
    phi = ph.phi_t(dt, s.dt)
    f = fo(o, dt, s.dt)
    qp = dt * QS * o.n
    qe = qp * f
    return R0(sid, s.n, s.k, pw, dt, qp, 1, f, phi, qe, qe / pw if pw else 0, ach, o.n * f, c.t - dt, "fan1", u=u)


def _fv2(sid, s, h, c, o, pw, so, st) -> R0:
    pts = list(st) if st is not None else fl.st_for(h)
    u = fl.uo(pts, fl.u0p(s.p, h.o), fl.lj(h)) + 0.25 * c.w
    dt = ph.fdt(s.dt, c.t, c.rh, u)
    if so:
        dt *= 0.85 + 0.15 * h.o
    ach, _ = fl.uach(h, c, abs(max(dt, 0.1)))
    if dt <= 0:
        return R0(sid, s.n, s.k, pw, dt, 0, 1, 0, 0, 0, 0, ach, 0, c.t - dt, "fan2", u=u, mode="v2")
    phi = ph.phi_t(dt, s.dt)
    f = fo(o, dt, s.dt)
    qp = dt * QS * o.n
    qe = qp * f
    return R0(sid, s.n, s.k, pw, dt, qp, 1, f, phi, qe, qe / pw if pw else 0, ach, o.n * f, c.t - dt, "fan2", u=u, mode="v2")


def _ev1(sid, s, h, c, o, pw, so) -> R0:
    dt = ph.edt(s, c)
    phi = ph.phi_t(dt, s.dt)
    ach = ph.ach_s(h, c, dt) if so else ph.ach_o(h, c)
    ve = ph.vex(h, ach)
    qc = R * C * s.q * dt
    fu = ph.fu(qc, ph.qv(ve, c.t, c.t - dt))
    f = fo(o, dt, s.dt)
    if so:
        phi = ph.phi_p(ph.dpet(c, dt, 0.0, h), 6.0) * max(0.05, phi)
    qe = qc * fu * f * phi
    return R0(sid, s.n, s.k, pw, dt, qc, fu, f, phi, qe, qe / pw if pw else 0, ach, o.n * f, c.t - dt * fu, "ev1", m=fu)


def _ev2(sid, s, h, c, o, pw, so, k, sh, I, qg) -> R0:
    dt = ph.edt(s, c)
    z = fl.bal(c, h, s.q, dt, qg=qg, k=k)
    phi = ph.phi_t(dt, s.dt)
    if so or h.o < 0.85:
        phi = ph.phi_p(fl.dpet(c, h, z.dtz, 0.0, sh, I), 6.0) * max(0.05, phi)
    f = fo(o, dt, s.dt)
    qe = z.qu * f * phi
    return R0(sid, s.n, s.k, pw, z.dtz, z.qp, z.fu, f, phi, qe, qe / pw if pw else 0, z.ach, o.n * f, z.tz, "ev2", m=z.m, mode="v2")
