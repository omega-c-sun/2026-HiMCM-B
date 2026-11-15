# params: systems A/B/C, shelters, climates, occ, economy
from dataclasses import dataclass, field
from typing import Dict

R = 1.2  # rho air
C = 1005.0  # cp air
G = 9.81
QS = 12.0  # W/K/person skin proxy


@dataclass(frozen=True)
class S:
    n: str
    k: str  # fan|evaporative
    p: float  # kW
    dt: float  # nominal dT
    q: float = 0.0  # supply m3/s


SYS: Dict[str, S] = {
    "A": S("Fan", "fan", 0.25, 3.0, 0.0),
    "B": S("Evap", "evaporative", 1.2, 5.0, 0.55),
    "C": S("EvapL", "evaporative", 2.5, 8.0, 1.10),
}


@dataclass(frozen=True)
class H:
    n: str
    a: float  # area
    h: float  # height
    o: float  # openness
    ao: float  # A_open
    ho: float  # h_open
    am: float = 5.0  # ACH min

    @property
    def v(self) -> float:
        return self.a * self.h


H0 = H("bus", 12.0, 2.5, 0.95, 18.0, 2.2, 8.0)
H1 = H("rail", 120.0, 4.0, 0.45, 40.0, 3.0, 4.0)


@dataclass(frozen=True)
class L:
    n: str
    t: float
    rh: float
    w: float
    hr: int = 12
    tc: float = 30.0
    ts: float = 35.0


L0 = L("Phoenix", 42.0, 0.20, 2.5)
L1 = L("Singapore", 33.0, 0.80, 1.2)
L2 = L("generic", 36.0, 0.45, 1.8)


@dataclass
class O:
    n: float
    cf: float = 0.75
    th: float = 0.15


O0 = O(8.0, 0.70)
O1 = O(60.0, 0.55)


@dataclass(frozen=True)
class E:
    ek: float = 0.15
    wk: float = 1.5
    wm: float = 0.004
    eg: float = 0.45
    ew: float = 0.3
    cap: Dict[str, float] = field(default_factory=lambda: {"A": 400.0, "B": 1800.0, "C": 4500.0})
    mnt: Dict[str, float] = field(default_factory=lambda: {"A": 25.0, "B": 150.0, "C": 280.0})
    yr: int = 8
    r: float = 0.05
    hrs: float = 800.0
    bud: float = 3000.0
    wb: float = 0.0


E0 = E()
E1 = E(bud=8000.0)
