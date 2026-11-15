= Sensitivity and Robustness <sec:sens>

== Structure: delivery and humidity

#figure(
  caption: [Crossover RH under delivery and humidity-model changes.],
)[
  #set text(size: 9pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, auto, auto),
    align: (left, right, right),
    stroke: 0.4pt,
    inset: 5pt,
    [*Model*], [*$D_n$*], [*RH\* (%)* ],
    [Claimed seat fraction 0.64], [0.640], [63],
    [Decay station 0.47], [0.472], [52],
    [Fluids, fixed $epsilon_p$], [0.581], [64],
    [Fluids + $epsilon_p("RH")$], [0.581], [54],
    [Fluids + $epsilon_p$ + latent switch], [0.581], [54],
  )
] <tab:e6>

#figure(
  image("../figures/v8_e6_rh_star.png", width: 82%),
  caption: [Structural sensitivity of the crossover humidity.],
) <fig:e6rh>

At Singapore's RH of 82%, the evaporative felt margin relative to the fan shifts from about −1.6 K (fixed $epsilon_p$) to about −2.2 K with $epsilon_p("RH")$. The humid-side preference for fans grows sharper.

== Multi-seat compliance

At the Tianjin open shelter, all three dwell stations (0.8, 1.8, 3.2 m) clear $T_"felt" <= 35$ °C for A/B/C on the design hour. Fan feel decays with distance, while evaporative seats track zone delivery. RAR in CEI uses this seat-weighted safety share; the older $Delta T_"eq" >= 3$ K rule serves only as a side check.

== Weight perturbation

With rated power removed from CEI, entropy weights on the Tianjin bus case place the largest mass on RAR and SCD. Uniform ±20% weight jitter over 400 draws keeps the feasible winner at A in 100% of trials under the \$3000 gate.

== Diurnal humidity

#figure(
  image("../figures/v8_diurnal_rh.png", width: 88%),
  caption: [Open-Meteo sample-day RH versus crossover lines.],
) <fig:diurnal>
