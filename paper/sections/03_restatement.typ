= Problem Restatement and Task Map

HiMCM 2026 Problem B asks how to measure cooling efficiency for open or semi-open public space, how three named systems compare at an open bus stop, how the measure revises for a larger semi-open waiting area, how the framework travels across climates, and how efficiency relates to effectiveness, experience, energy, and cost.

#figure(
  caption: [Task–layer–output map. Each requirement ends in a table or figure the reader can audit.],
)[
  #set text(size: 8.5pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, auto, auto, auto),
    align: (left, left, left, left),
    stroke: 0.4pt,
    inset: 4pt,
    [*Task*], [*Layers used*], [*Primary output*], [*Decision claim*],
    [1 Valid metric], [M1–M3], [Counter-example table], [Catalogue drop ≠ seat value],
    [2 Open shelter], [M1–M3 + gates], [Task 2 table], [CEI ranks; budget may empty set],
    [3 Semi-open], [M1–M3 + flip ablation], [Flip table + CEI], [Which single factor moves ranks],
    [4 Climates], [M1–M3 + crossover], [Eight-city figure], [Humidity sorts physics; gates sort buys],
    [5 Balance / memo], [Gates + CEI], [Four-objective + memo], [Safety and budget before score],
  )
] <tab:taskmap>

We keep the delivery chain M1 (arrival) → M2 (feel) → M3 (CEI), and separate *ranking* from *feasible set* (safety ∧ budget ∧ water).
