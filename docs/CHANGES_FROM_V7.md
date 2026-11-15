# From HiMCM B v7 → this repo (v9)

Short note on what changed relative to the teammate **v7 delivery paper** (three-layer M1→M2→M3 + CEI + RH\*≈63%).

## Kept from v7

- Three-layer chain: **M1 arrival → M2 feel → M3 decision (CEI)**
- Fan vs evaporative on the same felt ruler (wind credit + ASHRAE cap)
- Analytic **humidity crossover** as the signature story
- Eight-city design-hour narrative, memo + blog
- Entropy weights + adequacy gate + TOPSIS as a cross-check

## Fixed / replaced

| v7 issue | What we did |
|---|---|
| \(L_b=18.1\,\mathrm{m}\) told two incompatible stories; CFD point 0.47 vs prose \(D_n=0.64\) | Delivery fraction from **fluids** \(V_\mathrm{ex}\), \(\eta_\mathrm{mix}\), \(k_\mathrm{sc}\) |
| Annual cost table ≈×10 vs stated \$0.13/kWh | Costs use **\$0.13/kWh**; LCC uses 800 h/yr for budget |
| Table “margin recommend” vs CEI winner conflict | Separate **physics margin** vs **feasible CEI winner** |
| Rated power + annual energy both in CEI (redundant) | Dropped rated **P**; kept energy cost |
| Platform flip blamed only on internal gain | **Single-factor flip table** (gain / exchange / \(k_\mathrm{sc}\) / combined) |
| Same `decay(6)` for B and C while text said C loses more | Unit **C** has higher \(k_\mathrm{sc}\) → lower \(D_n\) than B |
| RAR = “\(\Delta T_\mathrm{eq}\ge3\,\mathrm{K}\)” only | Seat-weighted **\(T_\mathrm{felt}\le35^\circ\mathrm{C}\)** (+ old rule as side check) |
| No Capex / empty feasible set | **Safety + LCC budget** hard gates; empty set allowed |

## Added

- \(\varepsilon_p(\mathrm{RH})\) and optional latent/dew-point switch → crossover **~64% → ~54%** with humidity-aware pad efficiency
- Occupancy coverage \(f_\mathrm{occ}\) in CEI (not in a watts numerator)
- Weight perturbation (±20%); task map; claims–evidence table
- Reproducible code: `model_v8/`, curated `data/sites_design_hour.csv`, Typst paper under `paper/`
- Built PDF: `paper/18388_v9.pdf`

## Not copied from v7 (on purpose)

- Do not treat CEI as \(\eta_\mathrm{eff}=Q_\mathrm{eff}/P\) wholesale
- Do not restore the fitted \(L_b\) jet story as the decision path
- Do not invent COP rankings without capacity/flow data

## How to regenerate numbers

```text
cd D:\Conditioner
python -m model_v8.run_all_v9
cd paper
python compile_v8.py
```
