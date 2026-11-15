= Results

Devices: A fan 0.25 kW; B evaporative 1.2 kW; C evaporative 2.5 kW. Fluids M1 with $epsilon_p("RH")$; electricity \$0.13/kWh; bus budget \$3000; rail \$8000.

== Task 1 — Valid metric

*Question.* What goes wrong when we rank by catalogue outlet drop alone?

*Output.* Nominal drops favor C (8 K) over B (5 K). Seat delivery gives $D_n$ of about 0.58 for B and 0.47 for C at Tianjin; felt benefits are close while C burns far more power and water.

*Baseline contrast.* Ranking by *nominal outlet temperature drop* picks C. Ranking by seat benefit per resource and lifecycle gates picks A.

*Limit.* We make no claim about a catalogue COP without capacity and flow data.

== Task 2 — Open shelter (Tianjin)

*Question.* Which unit clears physics and money at the open stop?

#figure(
  caption: [Task 2, Tianjin open shelter ($T_a=33.5$ °C, RH 55%).],
)[
  #set text(size: 8.5pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, auto, auto, auto, auto, auto, auto),
    align: (left, right, right, right, right, right, left),
    stroke: 0.4pt,
    inset: 3.5pt,
    [*Unit*], [*$Delta T_"eq"$*], [*$D_n$*], [*Cost kUSD/yr*], [*$C_"LCC"$*], [*CEI*], [*Feasible*],
    [A], [3.20], [1.00], [0.098], [730], [0.599], [yes],
    [B], [3.11], [0.58], [0.468], [4248], [0.165], [budget fail],
    [C], [3.67], [0.47], [0.975], [9386], [0.165], [budget fail],
  )
] <tab:task2>

*Baseline contrast.* Unconstrained CEI still ranks A first; the \$3000 gate leaves *only A*.

*Limit.* Absolute felt relief can still favor C; the purchase question is gated.

== Task 3 — Semi-open transfer and single-factor flip

*Question.* What actually moves the ranking when the site becomes a platform?

#figure(
  caption: [Single-factor ablation from bus baseline toward rail. Margin is felt benefit of B minus A.],
)[
  #set text(size: 8pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, auto, auto, auto, auto, auto),
    align: (left, right, right, right, left, left),
    stroke: 0.4pt,
    inset: 3.5pt,
    [*Case*], [*Margin*], [*$D_n$ B*], [*$D_n$ C*], [*Feasible*], [*CEI winner*],
    [Bus baseline], [−0.09], [0.58], [0.47], [A], [A],
    [Gain only], [+1.02], [0.58], [0.47], [A,B], [A],
    [Exchange only], [−0.64], [0.78], [0.69], [A,B], [A],
    [Higher $k_"sc"$ only], [−0.09], [0.44], [0.56], [A,B], [A],
    [Rail combined], [−0.03], [0.78], [0.69], [A,B], [A],
  )
] <tab:flip>

*Output.* Raising internal gain alone taxes the fan asymmetrically, since the fan has no air depression to pay the penalty. The B−A margin can therefore widen, even though a common subtractive $L$ would cancel in a pure air temperature comparison. Exchange raises evaporative $D_n$. Combined rail admits A and B under \$8000; A still leads CEI while B's retention improves.

#figure(
  image("../figures/v8_platform_flip.png", width: 85%),
  caption: [CEI before and after transfer to the semi-open platform.],
) <fig:flip>

*Limit.* A full piston-wind field is not resolved; exchange is algebraic.

== Task 4 — Eight cities

*Question.* Does humidity still organize the world after fluids and $epsilon_p("RH")$?

#figure(
  image("../figures/v8_eight_cities.png", width: 92%),
  caption: [Felt margin of B over A; labels are feasible CEI winners (empty = none).],
) <fig:eight>

*Output.* Physics margins follow humidity. On the open-bus budget, B/C usually fail LCC, so the feasible winner is the fan wherever safety holds. Dubai at 42 °C yields an *empty* feasible set.

*Limit.* Design hours are curated; one Open-Meteo day is illustration only.

== Task 5 — Feasible set and four-objective balance

#figure(
  caption: [Hard gates at Tianjin (open bus).],
)[
  #set text(size: 9pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, auto, auto, auto, auto),
    align: (left, left, left, left, left),
    stroke: 0.4pt,
    inset: 4pt,
    [*Unit*], [*Safety*], [*Budget*], [*Water*], [*Feasible*],
    [A], [pass], [pass], [pass], [yes],
    [B], [pass], [fail], [pass], [no],
    [C], [pass], [fail], [pass], [no],
  )
] <tab:feasible>

#figure(
  caption: [Four-objective reading (model output).],
)[
  #set text(size: 8.5pt)
  #set par(first-line-indent: 0pt)
  #table(
    columns: (auto, 1fr, 1fr),
    align: (left, left, left),
    stroke: 0.4pt,
    inset: 4pt,
    [*Objective*], [*Open shelter*], [*Semi-open platform*],
    [Effectiveness], [C high $Delta T_"eq"$ but gated out], [B retention up; A,B feasible],
    [Experience], [Multi-seat RAR under 35 °C], [Gain taxes fan feel],
    [Energy / water], [A lowest], [Same meters, better mix],
    [Cost], [Only A ≤ \$3000], [A,B ≤ \$8000],
  )
] <tab:balance>
