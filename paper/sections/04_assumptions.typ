= Assumptions and Data Inputs

== Modelling assumptions

#figure(
  caption: [Assumptions with failure direction and how we check them.],
)[
  #set text(size: 8.5pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, 1fr, auto, auto),
    align: (left, left, left, left),
    stroke: 0.4pt,
    inset: 3.5pt,
    [*Assumption*], [*If wrong, bias*], [*Direction*], [*Check*],
    [Design hour, not full TMY], [Miss shoulder hours], [Schedule risk], [Diurnal RH figure],
    [Electricity \$0.13/kWh], [Cost scale], [± proportional], [Stated tariff],
    [LCC uses 800 h/yr], [Budget tightness], [Higher hours → fewer feasible], [Sensitivity note],
    [$epsilon_p("RH")$ soft decay], [Evap optimism if flat], [High RH favors fan more], [Latent ablation],
    [Safety at 35 °C felt], [Gate strictness], [Empty sets in extremes], [Phoenix/Dubai demos],
    [Coverage $f_"occ"$ in CEI only], [Avoids inflating W-efficiency], [Neutral to path watts], [Indicator list],
  )
] <tab:assumptions>

== Data and inputs

Six site inputs: $T_a$, RH, geometry class, internal gain, tariff/budget, unit nameplates. Design-hour rows are curated station-class targets (Tier 1 intent). Open-Meteo archive for 2023-07-15 validates order of magnitude and supplies diurnal RH for three cities; we do not overwrite decision hours with one calendar day.

#figure(
  caption: [Eight design-hour sites. Margin is B−A felt benefit; feasible CEI winner uses hard gates.],
)[
  #set text(size: 8.5pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (left, right, right, right, left, left),
    stroke: 0.4pt,
    inset: 4pt,
    [*City*], [*$T_a$*], [*RH%*], [*Margin B−A*], [*Feasible*], [*Note*],
    [Dubai], [42.0], [22], [physics+], [empty], [Safety fails],
    [Cairo], [38.0], [30], [~0], [A], [Budget kills B/C],
    [Los Angeles], [30.0], [40], [~0], [A], [],
    [Tianjin], [33.5], [55], [−0.09], [A], [Baseline],
    [London], [28.0], [60], [neg.], [A], [],
    [Atlanta], [32.0], [65], [neg.], [A], [Near crossover],
    [Mumbai], [33.0], [75], [neg.], [A], [],
    [Singapore], [31.0], [82], [−2.2], [A], [$epsilon_p$ cut],
  )
] <tab:sites>

== Principal symbols

$D_n$ / $eta_"mix"$ delivery fraction; $Delta T_0$ outlet drop; $Delta T_z$ zone drop; $Delta T_"eq"$ felt benefit; $f_"occ"$ coverage; CEI composite index; $C_"LCC"$ lifecycle cost; $B_"site"$ budget.
