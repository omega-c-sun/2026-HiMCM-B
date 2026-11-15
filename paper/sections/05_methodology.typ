= Methodology: Three Delivery Layers

== Architecture

M1 returns delivery fraction and net seat depression; M2 returns felt cooling $Delta T_"eq"$; M3 returns CEI inside a feasible set after hard gates.

== M1 — Arrival (fluids + humidity)

Exchange $dot(V)_"ex"$ and short-circuit
$
eta_"mix" = 1 / (1 + k_"sc" (A_"open"/A_"zone")(dot(V)_"ex"/dot(V)_"sup"))
$
identify $D_n$. Unit C uses a higher $k_"sc"$ so its delivery fraction can fall below B despite larger supply. Pad effectiveness $epsilon_p("RH")$ declines in humidity; when $T_s < T_"dp"$ or RH $>= 85%$, a latent offset reduces the usable outlet drop.

#figure(
  image("../figures/v8_delivery_bars.png", width: 88%),
  caption: [Tianjin open shelter: catalogue drop, delivered zone drop, and felt benefit.],
) <fig:delivery>

== M2 — Feel

Wind credit capped at 3.2 K (ASHRAE elevated-air-speed). Felt temperature $T_"felt" = T_a - Delta T_"eq"$ feeds safety.

== M3 — Decision

Indicators (no rated-power column; it duplicated annual energy cost): $Delta T_"eq"$, SCD, RAR, energy cost, water, $f_"occ"$. RAR is the seat-weighted share with $T_"felt" <= 35$ °C. Adequacy gate and TOPSIS cross-check remain. Hard gates: safety, lifecycle budget, optional water. Coverage enters CEI as a benefit, never as a watts numerator.

== Crossover

Equating fan and evaporative felt benefits yields a crossover near 64% RH with fixed $epsilon_p$, and near *54%* once $epsilon_p("RH")$ is on—humidity then favors the fan earlier.
