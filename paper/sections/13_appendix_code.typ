#import "../template.typ": no-indent

#pagebreak()
= Appendix

== A. Data

Curated design hours and Open-Meteo checks live under the project data folder. Diurnal RH curves support the sensitivity figure; decision tables use curated hours.

== B. Derived crossover and ablation

#figure(
  caption: [Key regenerated quantities.],
)[
  #set text(size: 9pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, auto, auto),
    align: (left, left, right),
    stroke: 0.4pt,
    inset: 5pt,
    [*Quantity*], [*Setting*], [*Value*],
    [RH\*], [Fixed $epsilon_p$], [64 %],
    [RH\*], [$epsilon_p("RH")$], [54 %],
    [Tianjin $D_n$ B / C], [Fluids], [0.58 / 0.47],
    [Weight A win rate], [±20%, 400 draws], [100 %],
    [Fan wind credit], [capped], [3.20 K],
  )
] <tab:derived>

== C. Reproduction commands

#raw(block: true, "python -m model_v8.run_all_v9
python paper/compile_v8.py")

Legacy CEI regression on the published six-indicator matrix still returns (0.849, 0.541, 0.130).

== D. Use of AI tools

AI assistance helped with English prose polishing under contest constraints. Numeric tables were regenerated from the model scripts. Structural choices (fluids M1, hard gates, CEI without rated power, single-factor flip) were made by the team.
