# E1–E6 grids + OAT elasticities → CSV
import csv, math
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple, Any
from core.a import SYS, H0, O0, H, L, O, S
from score import d as ef, e as ex
from fluid import c as fl


@dataclass
class M:
    exp: str
    sid: str
    lab: str
    eta: float
    qe: float
    fu: float
    fo: float
    phi: float
    dt: float
    tf: float
    ach: float
    cv: float
    safe: int
    m: float
    u: float
    mode: str
    x1: float = float("nan")
    x2: float = float("nan")
    x3: float = float("nan")
    n1: str = ""
    n2: str = ""
    n3: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _m(exp, sid, s, h, c, o, *, lab="", so=False, v2=True, k=1.0, sh=0.55, st=None,
       x1=float("nan"), x2=float("nan"), x3=float("nan"), n1="", n2="", n3="") -> M:
    r = ef.eval(sid, s, h, c, o, so=so, v2=v2, k=k, sh=sh, st=st)
    x = ex.fx(r, c)
    return M(exp, sid, lab or sid, r.eta, r.qe, r.fu, r.fo, r.phi, r.dt, x.tf, r.ach, x.cv,
             1 if x.ok else 0, r.m, r.u, r.mode, x1, x2, x3, n1, n2, n3)


def ls(a: float, b: float, n: int) -> List[float]:
    if n <= 1:
        return [a]
    d = (b - a) / (n - 1)
    return [a + i * d for i in range(n)]


def wcsv(p: Path, rows: Sequence[M]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        p.write_text("", encoding="utf-8")
        return
    ks = list(rows[0].to_dict().keys())
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ks)
        w.writeheader()
        for r in rows:
            w.writerow(r.to_dict())


@dataclass
class OA:
    p: str
    b: float
    pct: float
    v: float
    be: float
    ne: float
    el: float
    bc: float
    nc: float
    bs: int
    ns: int
    sid: str


def _el(b: float, n: float, pct: float) -> float:
    if abs(pct) < 1e-12 or abs(b) < 1e-12:
        return float("nan")
    return ((n - b) / abs(b)) / pct


def oat(sid, h, c, o, *, so=False, v2=True, k=1.0, pcts=(-0.5, -0.2, 0.2, 0.5)) -> List[OA]:
    s = SYS[sid]
    base = _m("oat0", sid, s, h, c, o, so=so, v2=v2, k=k)
    sp = [
        ("openness", h.o, lambda v: (replace(h, o=max(0.05, min(1.0, v))), c, o, k)),
        ("a_open", h.ao, lambda v: (replace(h, ao=max(0.5, v)), c, o, k)),
        ("height", h.h, lambda v: (replace(h, h=max(1.5, v), ho=max(1.0, h.ho * v / h.h)), c, o, k)),
        ("t_out", c.t, lambda v: (h, replace(c, t=v), o, k)),
        ("rh", c.rh, lambda v: (h, replace(c, rh=max(0.05, min(0.99, v))), o, k)),
        ("wind", c.w, lambda v: (h, replace(c, w=max(0.0, v)), o, k)),
        ("cover", o.cf, lambda v: (h, c, O(o.n, max(0.05, min(1.0, v)), o.th), k)),
        ("k_sc", k, lambda v: (h, c, o, max(0.0, v))),
        ("power", s.p, lambda v: (h, c, o, k)),
    ]
    out: List[OA] = []
    for name, bv, ap in sp:
        for pct in pcts:
            nv = bv * (1.0 + pct)
            sh, cl, oc, kk = ap(nv)
            if name == "power":
                sp2 = replace(s, p=max(0.05, nv))
                if s.k == "evaporative" and s.q > 0:
                    sp2 = replace(sp2, q=s.q * math.sqrt(max(0.05, nv) / s.p))
                m = _m("oat", sid, sp2, sh, cl, oc, so=so, v2=v2, k=kk)
                pv = max(0.05, nv)
            else:
                m = _m("oat", sid, s, sh, cl, oc, so=so, v2=v2, k=kk)
                pv = nv
            out.append(OA(name, bv, pct, pv, base.eta, m.eta, _el(base.eta, m.eta, pct),
                          base.cv, m.cv, base.safe, m.safe, sid))
    return out


def woat(p: Path, rows: Sequence[OA]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        p.write_text("", encoding="utf-8")
        return
    ks = list(asdict(rows[0]).keys())
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ks)
        w.writeheader()
        for r in rows:
            w.writerow(asdict(r))


def e1(c: L, h: H = H0, o: O = O0, *, ids=("A", "B", "C"), ov=None, av=None, hv=None, so=False) -> List[M]:
    ov = list(ov or ls(0.2, 1.0, 9))
    av = list(av or ls(4.0, 28.0, 7))
    hv = list(hv or [2.0, 2.5, 3.5])
    rows = []
    for sid in ids:
        s = SYS[sid]
        for oo in ov:
            for a in av:
                for hh in hv:
                    sh = replace(h, o=oo, ao=a, h=hh, ho=min(hh * 0.9, h.ho * hh / h.h))
                    rows.append(_m("E1", sid, s, sh, c, o, so=so or oo < 0.7,
                                   x1=oo, x2=a, x3=hh, n1="openness", n2="a_open", n3="height"))
    return rows


def e2(h: H, o: O, *, ids=("A", "B", "C"), tv=None, rv=None, w=1.8, so=False) -> List[M]:
    tv = list(tv or ls(28.0, 44.0, 9))
    rv = list(rv or ls(0.15, 0.90, 8))
    rows = []
    for sid in ids:
        s = SYS[sid]
        for t in tv:
            for rh in rv:
                cl = L("plane", t, rh, w)
                rows.append(_m("E2", sid, s, h, cl, o, so=so, x1=t, x2=rh, n1="t_out", n2="rh"))
    return rows


def e3(h: H, c: L, o: O, *, ids=("B", "C"), wv=None, kv=None, so=False) -> List[M]:
    wv = list(wv or ls(0.2, 5.0, 10))
    kv = list(kv or ls(0.0, 3.0, 7))
    rows = []
    for sid in ids:
        s = SYS[sid]
        for w in wv:
            for k in kv:
                cl = replace(c, w=w)
                rows.append(_m("E3", sid, s, h, cl, o, so=so, k=k, x1=w, x2=k, n1="wind", n2="k_sc"))
    return rows


def e4(h: H, c: L, *, sid="A", cv=None, sv=None, n=8.0, so=False) -> List[M]:
    cv = list(cv or ls(0.3, 1.0, 8))
    sv = list(sv or ls(0.5, 2.5, 9))
    base = fl.st_for(h)
    s = SYS[sid]
    rows = []
    for cf in cv:
        for st in sv:
            pts = [(x * st, w) for x, w in base]
            rows.append(_m("E4", sid, s, h, c, O(n, cf), so=so, st=pts,
                           x1=cf, x2=st, n1="cover", n2="stretch"))
    return rows


def e5(h: H, c: L, o: O, *, ids=("A", "B", "C"), so=False) -> List[OA]:
    xs = []
    for sid in ids:
        xs.extend(oat(sid, h, c, o, so=so, v2=True))
    return xs


def e6(h: H, c: L, o: O, *, ids=("A", "B", "C"), so=False, lab="") -> List[M]:
    rows = []
    for sid in ids:
        s = SYS[sid]
        for mode, flag in (("v1", False), ("v2", True)):
            rows.append(_m("E6", sid, s, h, c, o, lab=f"{lab}:{mode}" if lab else mode,
                           so=so, v2=flag, x1=0.0 if flag else 1.0, n1="is_v2"))
    return rows
