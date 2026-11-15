# lifecycle cost / CO2 / budget∧water
from dataclasses import dataclass
from typing import List, Sequence, TypeVar
from core.a import S, E
from score.d import R0


@dataclass
class LC:
    lcc: float
    co2: float
    ek: float
    wa: float
    mpv: float
    opv: float
    cap: float
    bud: float
    bok: bool
    wok: bool
    cps: float
    qk: float
    ok: bool


def pv(r: float, n: int) -> float:
    if n <= 0:
        return 0.0
    return (1.0 - (1.0 + r) ** (-n)) / r if r > 0 else float(n)


def lc(s: S, r: R0, e: E) -> LC:
    ek = s.p * e.hrs
    wa = ((r.qp / 1000.0) * e.hrs * e.wm) if s.k == "evaporative" else 0.0
    cap = e.cap.get(r.sid, 1000.0)
    mnt = e.mnt.get(r.sid, 0.0)
    ao = ek * e.ek + wa * e.wk + mnt
    f = pv(e.r, e.yr)
    opv = ao * f
    lcc = cap + opv
    co2 = ek * e.eg * e.yr + wa * e.ew * e.yr
    qk = (r.qe / 1000.0) * e.hrs
    cps = lcc / (qk * e.yr) if qk > 1e-9 else float("inf")
    bok = True if e.bud <= 0 else lcc <= e.bud + 1e-9
    wok = True if e.wb <= 0 else wa <= e.wb + 1e-9
    return LC(lcc, co2, ek, wa, mnt * f, opv, cap, e.bud, bok, wok, cps, qk, bok and wok)


T = TypeVar("T")


def filt(rows: Sequence[T], g=lambda r: getattr(r, "ok", True)) -> List[T]:
    return [r for r in rows if g(r)]


def rank_cps(rows: Sequence[T], g=None, cps=lambda r: r.cps) -> List[T]:
    def key(r):
        ok = True if g is None else bool(g(r))
        x = cps(r)
        x = float("inf") if x != x or x == float("inf") else float(x)
        return (0 if ok else 1, x)

    return sorted(rows, key=key)
