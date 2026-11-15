# scenario runners Req2a/2b/3
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from core.a import SYS, H0, H1, L0, L1, L2, O0, O1, E0, E1, H, L, O, E
from score import d as ef, e as ex, f as lc


@dataclass
class Row:
    case: str
    climate: str
    shelter: str
    sid: str
    sn: str
    eta: float
    qe: float
    fu: float
    fo: float
    phi: float
    dt: float
    tf: float
    ach: float
    nb: float
    cv: float
    safe: bool
    lcc: float
    co2: float
    bud: float
    bok: bool
    wok: bool
    ok: bool
    cps: float
    note: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _eco(so: bool, e: Optional[E] = None) -> E:
    return e if e is not None else (E1 if so else E0)


def one(case, sid, h: H, c: L, o: O, *, so: bool, v2: bool = True, e: Optional[E] = None) -> Row:
    s = SYS[sid]
    eco = _eco(so, e)
    r = ef.eval(sid, s, h, c, o, so=so, v2=v2)
    x = ex.fx(r, c)
    y = lc.lc(s, r, eco)
    return Row(
        case, c.n, h.n, sid, s.n, r.eta, r.qe, r.fu, r.fo, r.phi, r.dt, x.tf, r.ach, r.nb,
        x.cv, x.ok, y.lcc, y.co2, y.bud, y.bok, y.wok, x.ok and y.ok, y.cps, r.note,
    )


def bus(c: L = L2, *, e: Optional[E] = None) -> List[Row]:
    return [one("bus", i, H0, c, O0, so=False, e=e) for i in ("A", "B", "C")]


def rail(c: L = L2, *, e: Optional[E] = None) -> List[Row]:
    return [one("rail", i, H1, c, O1, so=True, e=e) for i in ("A", "B", "C")]


def phx(*, e: Optional[E] = None) -> List[Row]:
    return [one("phx", i, H0, L0, O0, so=False, e=e) for i in ("A", "B", "C")]


def sgp(*, e: Optional[E] = None) -> List[Row]:
    return [one("sgp", i, H1, L1, O1, so=True, e=e) for i in ("A", "B", "C")]


def rank_eta(rows: List[Row]) -> List[str]:
    return [r.sid for r in sorted(rows, key=lambda x: x.eta, reverse=True)]


def rank_ok(rows: List[Row]) -> List[str]:
    xs = lc.rank_cps(rows, g=lambda r: r.ok, cps=lambda r: r.cps)
    return [r.sid for r in xs if r.ok]


def ok_ids(rows: List[Row]) -> List[str]:
    return [r.sid for r in rows if r.ok]


def all() -> Dict[str, List[Row]]:
    return {"bus": bus(), "rail": rail(), "phx": phx(), "sgp": sgp()}
