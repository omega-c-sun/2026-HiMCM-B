# Cooling Model V1 — Assumptions & Scheme Check

Problem PDF: `D:\Conditioner\2026_HiMCM_Problem_B.pdf`  
Idea list: `D:\Conditioner\2026_HiMCM_B_设想清单.txt`  
Code: `D:\Conditioner\model\`

> **V2 appendix:** elementary fluids + sensitivity experiments — see [`model_v2_fluids_sensitivity.md`](model_v2_fluids_sensitivity.md). Default `use_fluids_v2=True` in `efficiency.evaluate`; set `False` for this V1 algebra.

## 1. Problem alignment

| Requirement | V1 implementation | Status |
|---|---|---|
| Req1 efficiency ≠ energy alone | `eta_eff = Q_eff / P` with `f_util`, `f_occ`, `phi_percept` | Done |
| Req2a bus stop A/B/C | `cases.req2a_bus_stop` + nameplate from problem | Done |
| Req2b semi-open revision | ACH(geometry, wind, ΔT), PET-proxy `phi`, larger zone | Done |
| Req3 two climates | Phoenix hot-dry bus; Singapore hot-humid semi-open | Done |
| Req4 efficiency ≠ effectiveness | comfort cover + safety flag + LCC/CO2 stubs | Skeleton |
| Req5 memo / blog | not in code | Deferred |

## 2. Hard fix: dual-path `Q_eff`

The problem states:

- Fan: feels up to 3 °C cooler (does **not** claim air temperature drop), 0.25 kW
- Evaporative: lowers air temperature up to 5 / 8 °C, 1.2 / 2.5 kW

If efficiency used only air sensible cooling `Q_cool = ρ cp V̇ ΔT_air`, the fan path has `Q_cool ≈ 0` and collapses.

**V1 rule**

- **Evaporative (B/C):** `Q_cool` of supply stream → × `f_util` × `f_occ` × `phi` (`phi` includes `g(RH)`).
- **Fan (A):** equivalent skin heat-loss gain `Q_path = ΔT_eq × q_skin × n_people` with `f_util = 1` (benefit rides on people, not on chilled air that is exchanged away) → × `f_occ`.
- `ΔT_eq` for fans depends on `T`, `RH`, relative speed; can go ≤ 0 in hot-humid extremes.

## 3. Other modeling choices

- Problem unit `kW/hr` treated as continuous electrical power in **kW**.
- Default open bus stop cooled footprint **12 m²**, height 2.5 m.
- Open-bus ACH: wind-driven empirical high exchange; semi-open ACH: wind + stack formula with `ach_min` floor.
- `f_util = Q_cool / (Q_cool + Q_vent)` for evaporative only (soft form; open high-ACH still heavily discounted).
- Comfort / safety: representative-afternoon felt temperature vs 30 °C / 35 °C thresholds (not full PET solver).
- LCC / CO2: constant tariff and grid factor; evaporative water use proportional to path cooling; annual O&M annuity to hold lifetime-average η; no explicit year-by-year aging trajectory yet.
- **Budget constraint (hard):** `C_LCC ≤ budget_usd` (bus default $3000, rail $8000). Optional annual water cap via `water_budget_m3_year`. Selection: `feasible = safety ∧ budget ∧ water`, then rank by `cost_per_service = LCC / lifetime useful cooling-kWh`.
- Capex placeholders: A $400, B $1800, C $4500; 800 cooling hours/year; 8-year life; 5% discount.

## 4. What changed for semi-open (Req2b)

| Piece | Open bus | Semi-open rail |
|---|---|---|
| Geometry | high openness, small volume | larger volume, lower openness |
| ACH | high → low `f_util` for evap | lower ACH → higher `f_util` |
| Perception | `ΔT` / `g(RH)` | PET-proxy with enclosure bonus |
| Occupancy | few people, higher cover fraction | many people, lower cover fraction |

Revision purpose: enclosure and occupancy distribution matter; “more enclosure” is not automatically “higher efficiency” once ACH floor and perception saturation apply.

## 5. Known limitations (V1)

- No CFD; airflow rates for B/C are assumed nameplate-like constants.
- No real hourly TMY weather; comfort cover is a threshold proxy.
- Fan `q_skin` (12 W/K·person) is a calibration constant for path comparability, not a lab measurement.
- Device aging, time-of-use carbon, fairness, and control schedules are interface-only / future work.
- Absolute `eta_eff` magnitudes are for **relative ranking** within a case, not vendor claims.

## 6. How to run

```text
cd D:\Conditioner
python -m model.run_v1
```

## 7. V1 numerical scheme-check (after calibration)

Observed from `python -m model.run_v1`:

- Open bus (generic): large evaporative can lead on `eta_eff` when airflow is high enough to keep some `f_util`.
- Semi-open rail: fan often leads on `eta_eff` because `f_util=1` and body-attached cooling is not flushed.
- Phoenix hot-dry: evaporative `phi` high (`g(RH)`~0.95); fan still positive via sweat path; **all systems may fail safety** at ~42 °C felt — efficiency ≠ effectiveness.
- Singapore hot-humid: evaporative `eta_eff` collapses (`g(RH)`~0.35); fan ranks first.

## 8. Literature used only as qualitative support

See `papers/对照.txt`. V1 does not fit coefficients to those PDFs.
