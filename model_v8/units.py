"""Device and site archetypes for v8/v9."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict


@dataclass(frozen=True)
class Unit:
    id: str
    name: str
    kind: str  # fan | evaporative
    power_kw: float
    delta_t0_k: float  # nominal outlet depression (0 for fan)
    v_seat_m_s: float
    vdot_sup_m3_s: float
    water_m3_yr: float
    f_occ: float  # coverage fraction of waiting people served
    k_sc: float = 1.0  # short-circuit orientation; larger = more path loss


UNITS: Dict[str, Unit] = {
    "A": Unit("A", "Fan", "fan", 0.25, 0.0, 1.75, 0.0, 0.0, 0.85, 1.0),
    "B": Unit("B", "Evaporative 1.2 kW", "evaporative", 1.2, 5.0, 0.30, 0.9, 260.0, 0.70, 1.0),
    # Larger supply but stronger short-circuit (aiming / detrainment) so Dn_C can fall below Dn_B
    "C": Unit("C", "Evaporative 2.5 kW", "evaporative", 2.5, 8.0, 0.35, 1.5, 540.0, 0.65, 2.6),
}


@dataclass(frozen=True)
class ShelterGeom:
    name: str
    area_m2: float
    height_m: float
    openness: float
    a_open_m2: float
    h_open_m: float
    ach_min: float
    q_gain_kw: float
    wind_m_s: float
    shade: float
    budget_usd: float

    @property
    def volume_m3(self) -> float:
        return self.area_m2 * self.height_m


def shelter_variant(base: ShelterGeom, **kwargs) -> ShelterGeom:
    return replace(base, **kwargs)


BUS = ShelterGeom(
    name="Open bus shelter",
    area_m2=12.0,
    height_m=2.5,
    openness=0.95,
    a_open_m2=18.0,
    h_open_m=2.2,
    ach_min=8.0,
    q_gain_kw=0.20,
    wind_m_s=1.8,
    shade=0.55,
    budget_usd=3000.0,
)

RAIL = ShelterGeom(
    name="Semi-open rail platform",
    area_m2=120.0,
    height_m=4.0,
    openness=0.45,
    a_open_m2=40.0,
    h_open_m=3.0,
    ach_min=4.0,
    q_gain_kw=0.60,
    wind_m_s=2.2,
    shade=0.70,
    budget_usd=8000.0,
)

# Seat stations for multi-point compliance (distance_m, weight)
BUS_STATIONS = [(0.8, 0.45), (1.8, 0.35), (3.2, 0.20)]
RAIL_STATIONS = [(1.5, 0.40), (4.0, 0.35), (8.0, 0.25)]

ELEC_USD_PER_KWH = 0.13
HOURS_YR_CEI = 3000.0
HOURS_YR_LCC = 800.0
CAPEX = {"A": 400.0, "B": 1800.0, "C": 4500.0}
MAINT = {"A": 25.0, "B": 150.0, "C": 280.0}
LIFETIME_YR = 8
DISCOUNT = 0.05
WATER_USD_PER_M3 = 1.5
T_SAFETY_MAX_C = 35.0
T_COMFORT_MAX_C = 30.0
EPS_PAD = 0.78
