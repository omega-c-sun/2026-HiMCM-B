# Conditioner — HiMCM 2026 Problem B (Team 18388)

Open / semi-open public-space cooling: **delivery chain M1→M2→M3**, CEI ranking, safety & budget gates.

| Path | Role |
|---|---|
| `model_v8/` | Reproducible v9 engine (fluids, CEI, ablations) |
| `data/` | Design-hour sites + Open-Meteo fetch helper |
| `paper/` | Typst manuscript → `18388_v9.pdf` |
| `upload/` | Short-named contest upload package (v1/v2 sweeps) |
| `model/` | Earlier dual-path \(\eta_\mathrm{eff}\) experiments |
| `docs/CHANGES_FROM_V7.md` | What changed vs the v7 paper |

## Quick start

```text
python -m model_v8.run_all_v9
cd paper
python compile_v8.py
```

See `docs/CHANGES_FROM_V7.md` for the v7 → v9 delta. Git push steps: `docs/GIT_PUSH.md`.
