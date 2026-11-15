# comfort cover + safety flag
from dataclasses import dataclass
from core.a import L
from score.d import R0


@dataclass
class X:
    cv: float
    ok: bool
    tf: float
    tc: float
    ts: float


def fx(r: R0, c: L) -> X:
    t = r.tf
    if t <= c.tc:
        cv = 1.0
    elif t >= c.ts:
        cv = 0.0
    else:
        cv = max(0.0, 1.0 - (t - c.tc) / (c.ts - c.tc))
    cv *= (0.5 + 0.5 * min(1.0, r.fo / 0.75)) if r.fo > 0 else 0.15 * cv
    ok = t <= c.ts and r.dt > 0
    return X(max(0.0, min(1.0, cv)), ok, t, c.tc, c.ts)
