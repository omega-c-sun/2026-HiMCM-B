# Cooling Model V2 — Elementary Fluids + Sensitivity

Extends V1 dual-path `η_eff` with a closed-form fluid layer (no CFD) and reproducible parameter scans.  
Code: `model/fluids_elem.py`, `model/sensitivity.py`, `model/run_v2_experiments.py`  
Outputs: `outputs/` (CSV + PNG)  
V1 assumptions: `docs/model_assumptions_v1.md`

## 1. Goals

- Replace “dry” ACH / util knobs with interpretable multi-variable algebra: steady energy balance, unified wind+stack exchange, short-circuit mixing, fan jet decay, shade/MRT PET proxy.
- Keep dual-path `Q_eff` (fan = skin heat-loss; evaporative = air sensible cooling).
- Answer: are default rankings stable? which parameters move `η_eff` / comfort / safety most?

Precision target: **relative ranking and mechanism explanation**, not vendor-grade absolute prediction.

## 2. Symbol table

| Symbol | Meaning | Typical unit |
|---|---|---|
| `T_out`, `T_s`, `T_z` | Outdoor / supply / zone dry-bulb | °C |
| `V̇_sup`, `V̇_ex` | Supply / exchange volume flow | m³/s |
| `A_open`, `η_open` | Geometric opening area; opening efficiency | m²; — |
| `C_w`, `C_t`, `C_D` | Wind / stack coeffs; discharge scale | — |
| `η_mix` | Short-circuit / incomplete-mix factor | (0,1] |
| `k_sc` | Short-circuit strength (orientation proxy) | — |
| `u(x)`, `u_occ` | Jet speed at distance; occupancy-weighted | m/s |
| `L_jet` | Jet decay length | m |
| `f_util`, `f_occ`, `φ` | Util / occupancy / perception factors | — |
| `η_eff` | `Q_eff / P_input` | — |

Switch: `efficiency.evaluate(..., use_fluids_v2=True)` (default). Set `False` for V1 algebra.

## 3. Elementary fluid layer

### 3.1 Unified wind + stack exchange

\[
\dot V_{\mathrm{ex}} = C_D\,\eta_{\mathrm{open}}(o)\Big(C_w A_{\mathrm{open}} u + C_t A_{\mathrm{open}}\sqrt{2gh|\Delta T|/T}\Big)
\]

\[
\mathrm{ACH}=\max\!\big(\mathrm{ACH}_{\min},\; \dot V_{\mathrm{ex}}\cdot 3600 / V\big)
\]

`η_open = 0.35 + 0.65·openness`.  
`C_D = 0.02` maps geometric façade area onto a hydraulic orifice so open-bus ACH lands in tens of 1/h (same order as V1 empirical open-bus ACH), not thousands.

### 3.2 Steady zone energy balance

\[
T_z = \frac{\dot V_{\mathrm{sup}} T_s + \dot V_{\mathrm{ex}} T_{\mathrm{out}} + Q_{\mathrm{gain}}/(\rho c_p)}{\dot V_{\mathrm{sup}}+\dot V_{\mathrm{ex}}}
\]

Supply drop: `T_s = T_out − ΔT_supply` with `ΔT_supply = ΔT_nom · g(RH)`.

### 3.3 Short-circuit / mixing

\[
\eta_{\mathrm{mix}} = \frac{1}{1 + k_{\mathrm{sc}}\,(A_{\mathrm{open}}/A_{\mathrm{zone}})\,(\dot V_{\mathrm{ex}}/\dot V_{\mathrm{sup}})}
\]

\[
Q_{\mathrm{path}}=\rho c_p \dot V_{\mathrm{sup}}(T_{\mathrm{out}}-T_s),\quad
Q_{\mathrm{util}}=Q_{\mathrm{path}}\,\eta_{\mathrm{mix}},\quad
f_{\mathrm{util}}=\eta_{\mathrm{mix}}
\]

`k_sc` is a supply-orientation proxy: large when discharge faces the dominant opening.

### 3.4 Fan jet decay

\[
u(x)=\frac{u_0}{1+x/L_{\mathrm{jet}}},\quad
u_{\mathrm{occ}}=\sum_i w_i u(x_i)/\sum_i w_i
\]

Default stations (bus): (0.8 m, 0.45), (1.8 m, 0.35), (3.2 m, 0.20).  
`u_occ` (+ mild ambient wind) enters `fan_delta_t_eq(T, RH, u)`.

### 3.5 Shade / MRT PET proxy

\[
T_{\mathrm{mrt}}\approx T_{\mathrm{out}}+a\,I_{\mathrm{solar}}(1-\mathrm{shade})
\]

`ΔPET` proxy adds shade bonus + enclosure bonus + air/fan ΔT terms (still elementary).

### 3.6 Wiring into `η_eff`

- **Evaporative:** `Q_eff = Q_util · f_occ · φ` with zone balance + `η_mix`; `f_occ` intensity uses supply `ΔT` (near-device), not fully mixed zone ΔT.
- **Fan:** `Q_eff` unchanged in form; `ΔT_eq` uses jet-weighted `u_occ`.

## 4. Experiment design (E1–E6)

Run: `python model/run_v2_experiments.py` → `outputs/`.

| ID | Sweep | Main question | Artifacts |
|---|---|---|---|
| E1 | `openness × A_open × height` | Geometry / ACH floor / util shape | `e1_geometry.csv`, heatmaps |
| E2 | `T_out × RH` for A/B/C | Fan boundary; evaporative `g(RH)` collapse | `e2_climate_plane.csv`, η & safety heatmaps |
| E3 | `wind × k_sc` | Why open-station evaporative is unstable | `e3_wind_shortcircuit.csv` |
| E4 | `covered_fraction × station_stretch` | Fan jet × occupancy | `e4_occupancy_jet.csv` |
| E5 | OAT ±20% / ±50% | Elasticities; tornado | `e5_oat_*.csv`, tornado PNGs |
| E6 | V1 vs V2 same cases | When fluids layer moves rankings | `e6_v1_vs_v2.csv`, bar chart |

Default sites: open bus A/B/C; semi-open rail; Phoenix bus; Singapore rail. Climates: generic summer / Phoenix / Singapore.

## 5. Main findings (from `outputs/findings_summary.txt` + E6 table)

### 5.1 Default-case rankings (η_eff) — order stable

| Case | V1 | V2 |
|---|---|---|
| Open bus (generic) | C > B > A | C > B > A |
| Semi-open rail | A > C > B | A > C > B |
| Phoenix open bus | C > B > A | C > B > A |
| Singapore semi-open | A > C > B | A > C > B |

**Magnitudes do move.** Examples (generic summer):

| Case / sys | V1 η_eff | V2 η_eff | V2 notes |
|---|---:|---:|---|
| Bus B | 0.575 | 0.443 | `η_mix≈0.47` (short-circuit) |
| Bus C | 1.100 | 0.904 | still leads; util down |
| Rail B | 0.273 | 0.458 | mix model retains more than V1 soft util |
| Rail C | 0.744 | 0.883 | same direction |
| Singapore B | 0.041 | 0.101 | humid still collapses vs fan A (~2.4) |

### 5.2 Ranking *does* flip under short-circuit / wind (E3 / mechanism)

Open bus, generic summer, vary `k_sc` (orientation proxy):

| `k_sc` | Order | A / B / C η_eff |
|---:|---|---|
| 0 | C > B > A | 0.44 / 0.95 / 1.46 |
| 1 (default) | C > B > A | 0.44 / 0.44 / 0.90 |
| 2 | C > A > B | 0.44 / 0.29 / 0.66 |
| ≥4 | **A > C > B** | 0.44 / 0.17 / 0.42 |

High wind + elevated `k_sc` (e.g. 4 m/s, `k_sc=2.5`) likewise yields **A > C > B**.  
E3 aggregate: system B mean `η_mix` ≈ **0.70** at low wind vs **0.33** at high wind.

**Interpretation:** open evaporative ranking is not intrinsic to nameplate kW; it is fragile to opening/orientation/wind. Fan path is immune to `η_mix` (`f_util=1`).

### 5.3 Climate plane (E2)

Near 33 °C, system B: dry RH≈0.2 → `η_eff≈0.80`; humid RH≈0.8 → `η_eff≈0.12`.  
Fan A retains a usable band until hot-humid collapse of `fan_delta_t_eq`. Safety heatmaps show Phoenix-like corners fail regardless of efficiency rank.

### 5.4 OAT elasticities (E5, open bus, system B, ±20%)

Largest |elasticity| of `η_eff`: **RH ≈ 1.26**, **`A_open` ≈ 1.05**, **`covered_fraction` = 1**, **`k_sc` ≈ 0.54**, **wind ≈ 0.43**.  
Tornado plots: `outputs/e5_tornado_bus_*.png`, `e5_tornado_rail_*.png`.

### 5.5 Occupancy × jet (E4)

Stretching dwell distances lowers `u_occ` and fan `η_eff`; raising `covered_fraction` scales almost linearly (elasticity ~1) until intensity threshold binds.

## 6. V1 vs V2 takeaway for the paper

1. Dual-path structure is unchanged; V2 supplies physical origins for `f_util` (`η_mix` + balance) and fan intensity (`u_occ`).
2. Default A/B/C order is robust across the four named cases — good for a stable baseline narrative.
3. Sensitivity, not the baseline point estimate, carries the design message: **open evaporative cooling is wind/orientation-limited**; enclosure + ACH floor changes the util surface (E1); humidity dominates evaporative elasticity (E5).
4. Explicit crossover: large `k_sc` or strong wind makes fan A beat large evaporative C on open bus — a clean “fluids layer changes ranking” figure for E6.

## 7. Budget constraint (with lifecycle)

Hard economic filter alongside safety (see `lifecycle.py` / `params.Economy`):

- `C_LCC = Capex + PV(elec + water + annual O&M)` over `lifetime_years`
- `budget_ok ⇔ C_LCC ≤ budget_usd` (bus default $3000; rail $8000)
- optional `water_budget_m3_year`; inactive when ≤ 0
- `feasible = safety ∧ budget ∧ water`, then rank by `cost_per_service = LCC / (lifetime · Q_eff·hours)`

Baseline printout: `python model/run_v1.py`. Under the bus $3000 ceiling, unconstrained η-leader C is often **infeasible**; only A clears the envelope on Req2a.

## 8. Explicitly out of scope (still)

CFD/OpenFOAM, full PET numerical solvers, hourly TMY optimal control, device aging trajectories.

## 9. How to reproduce

```text
cd D:\Conditioner
python model/run_v2_experiments.py
python model/run_v1.py
```

Optional: `efficiency.evaluate(..., use_fluids_v2=False)` for side-by-side V1.
