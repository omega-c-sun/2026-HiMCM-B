# Open / semi-open cooling model (HiMCM Problem B)

Simulation + numeric experiments for comparing fan vs evaporative coolers at open bus stops and semi-open waiting areas.

**What it does:** score each system with effective efficiency `eta`, then comfort/safety and lifecycle cost under a budget; sweep geometry / climate / wind / occupancy to see ranking stability.

## Folders

| Folder | Role |
|--------|------|
| `core/` | Constants, default systems/shelters/climates, V1 physics discounts |
| `fluid/` | Elementary fluids (exchange, short-circuit mix, jet decay, zone balance) |
| `score/` | `eta` paths, comfort/safety, lifecycle + budget/water |
| `case/` | Fixed scenarios (bus / rail / Phoenix / Singapore) |
| `sweep/` | Experiments E1–E6 + one-at-a-time elasticity |
| `run/` | Entry scripts that print tables or write CSV/plots |
| `out/` | Generated tables and figures |

## Run

From this directory (needs Python 3.10+):

```text
python run/v1.py
python run/v2.py
```

`v1` prints baseline case tables. `v2` writes `out/e1.csv` … `out/e6.csv` (and PNGs if matplotlib is installed).

```text
pip install -r requirements.txt
```

## Experiments (v2)

| ID | Sweep | Main outputs |
|----|-------|----------------|
| E1 | openness × opening area × height | `out/e1.csv` |
| E2 | outdoor T × RH | `out/e2.csv` |
| E3 | wind × short-circuit strength | `out/e3.csv` |
| E4 | occupancy cover × jet stretch | `out/e4.csv` |
| E5 | ±% OAT elasticities | `out/e5_bus.csv`, `out/e5_rail.csv` |
| E6 | V1 algebra vs V2 fluids | `out/e6.csv` |

## Short names (cheat sheet)

| Token | Meaning |
|-------|---------|
| `S` / `SYS` | cooling system / A·B·C map |
| `H` / `H0`·`H1` | shelter; bus / rail defaults |
| `L` / `L0`·`L1`·`L2` | climate; Phoenix / Singapore / generic |
| `O` / `O0`·`O1` | occupancy |
| `E` / `E0`·`E1` | economy + budget |
| `R`·`C`·`G`·`QS` | air density, cp, g, skin W/K |
| `eta`·`fu`·`fo`·`phi`·`m` | efficiency, util, occupancy frac, percept, mix |
| `lcc`·`cps`·`ok` | lifecycle $, $/service, feasible |

Files: `core/a.py` params, `core/b.py` V1 physics, `fluid/c.py` fluids, `score/d|e|f.py` eta / comfort / cost, `case/g.py` scenarios, `sweep/h.py` E1–E6.

## Notes

- Names are short on purpose; headers say what each file does.
- Paper / Typst / API keys / local drafts are **not** in this tree.
