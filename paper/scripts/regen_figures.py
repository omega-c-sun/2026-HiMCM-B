"""Regenerate paper figures: intuitive line charts + mathtext labels."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

# Mathtext works when launched from a .py file (not PowerShell -c).
rcParams["mathtext.fontset"] = "dejavusans"
rcParams["font.family"] = "DejaVu Sans"
rcParams["font.size"] = 11
rcParams["axes.titlesize"] = 12
rcParams["axes.labelsize"] = 11
rcParams["legend.fontsize"] = 10

from model.params import BUS_OCC, BUS_STOP_OPEN, GENERIC_SUMMER, SYSTEMS
from model import efficiency
from model.sensitivity import (
    e1_geometry_scan,
    e2_climate_plane,
    e3_wind_shortcircuit,
)
from dataclasses import replace

FIG = ROOT / "paper" / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def main():
    from model.sensitivity import linspace

    # ----- E1: slopegraph — small vs large opening (geometry leak story) -----
    rows = e1_geometry_scan(GENERIC_SUMMER, BUS_STOP_OPEN, BUS_OCC)
    heights = sorted({r.x3 for r in rows})
    h_mid = heights[len(heights) // 2]
    openness_show = [0.3, 0.5, 0.7, 1.0]
    colors_o = ["#4c72b0", "#55a868", "#dd8452", "#c44e52"]
    # pick nearest available A_open endpoints
    a_all = sorted({r.x2 for r in rows if r.system_id == "B" and abs(r.x3 - h_mid) < 1e-9})
    a_lo, a_hi = a_all[0], a_all[-1]

    def _f_util(o: float, a: float) -> float:
        hit = [
            r.f_util
            for r in rows
            if r.system_id == "B"
            and abs(r.x3 - h_mid) < 1e-9
            and abs(r.x1 - o) < 1e-9
            and abs(r.x2 - a) < 1e-9
        ]
        return hit[0] if hit else float("nan")

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.8), gridspec_kw={"width_ratios": [1.05, 1.2]})
    ax = axes[0]
    for o, col in zip(openness_show, colors_o):
        y0, y1 = _f_util(o, a_lo), _f_util(o, a_hi)
        ax.plot([0, 1], [y0, y1], "-o", color=col, lw=2.4, ms=8, label=rf"openness $= {o:.2f}$")
        ax.annotate(
            f"{y1:.2f}",
            xy=(1, y1),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            color=col,
        )
    ax.set_xticks([0, 1])
    ax.set_xticklabels(
        [rf"Small opening{chr(10)}$A_{{\mathrm{{open}}}}={a_lo:.0f}$ m$^2$",
         rf"Large opening{chr(10)}$A_{{\mathrm{{open}}}}={a_hi:.0f}$ m$^2$"]
    )
    ax.set_ylabel(r"Utilization $f_{\mathrm{util}}$")
    ax.set_title("Leak story: small → large opening")
    ax.set_ylim(0, 1.08)
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend(loc="lower left", fontsize=9, frameon=True)
    ax.annotate(
        "larger openings\ncut useful cooling",
        xy=(0.72, 0.55),
        xycoords="axes fraction",
        fontsize=9,
        color="#444444",
        ha="center",
        style="italic",
    )

    ax = axes[1]
    for o, col in zip(openness_show, colors_o):
        pts = sorted(
            (r.x2, r.f_util)
            for r in rows
            if r.system_id == "B" and abs(r.x3 - h_mid) < 1e-9 and abs(r.x1 - o) < 1e-9
        )
        if not pts:
            continue
        xs, ys = zip(*pts)
        ax.plot(xs, ys, "-", color=col, lw=2.0, alpha=0.95)
        ax.fill_between(xs, ys, 0, color=col, alpha=0.08)
    ax.set_xlabel(r"Opening area $A_{\mathrm{open}}$ (m$^2$)")
    ax.set_ylabel(r"$f_{\mathrm{util}}$")
    ax.set_title(rf"Full scan ($h={h_mid:.1f}$ m)")
    ax.set_ylim(0, 1.08)
    ax.grid(True, alpha=0.35)
    fig.suptitle(
        r"E1 system B: geometry leak — openness and $A_{\mathrm{open}}$ shrink $f_{\mathrm{util}}$",
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(FIG / "e1_B_f_util_h2.5.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # ----- E2: dry vs humid ranking bars (climate flip at a glance) -----
    rh_dry, rh_humid = 0.20, 0.80
    rh_vals = linspace(0.15, 0.90, 16)
    series = {sid: [] for sid in ("A", "B", "C")}
    for rh in rh_vals:
        cl = replace(GENERIC_SUMMER, t_out_c=36.0, rh=rh, name="slice")
        for sid in ("A", "B", "C"):
            r = efficiency.evaluate(
                sid, SYSTEMS[sid], BUS_STOP_OPEN, cl, BUS_OCC, semi_open=False
            )
            series[sid].append(r.eta_eff)

    def _eta_at(sid: str, rh_target: float) -> float:
        cl = replace(GENERIC_SUMMER, t_out_c=36.0, rh=rh_target, name="slice")
        return efficiency.evaluate(
            sid, SYSTEMS[sid], BUS_STOP_OPEN, cl, BUS_OCC, semi_open=False
        ).eta_eff

    bar_colors = {"A": "#4c72b0", "B": "#55a868", "C": "#c44e52"}
    names = {"A": "A fan", "B": "B evaporative", "C": "C large evaporative"}
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.6), sharey=True)
    for ax, rh, title, face in (
        (axes[0], rh_dry, rf"Drier air (RH $= {rh_dry:.2f}$)", "#f6e8c3"),
        (axes[1], rh_humid, rf"Humid air (RH $= {rh_humid:.2f}$)", "#d9e8fb"),
    ):
        vals = [_eta_at(sid, rh) for sid in ("A", "B", "C")]
        x = np.arange(3)
        bars = ax.bar(x, vals, color=[bar_colors[s] for s in ("A", "B", "C")], width=0.62, edgecolor="white")
        ax.set_xticks(x)
        ax.set_xticklabels([names[s] for s in ("A", "B", "C")], fontsize=9)
        ax.set_title(title)
        ax.set_facecolor(face)
        ax.grid(True, axis="y", alpha=0.35)
        for b, v in zip(bars, vals):
            ax.text(
                b.get_x() + b.get_width() / 2,
                v + 0.04,
                f"{v:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
        order = sorted(zip(("A", "B", "C"), vals), key=lambda t: -t[1])
        rank = " > ".join(s for s, _ in order)
        ax.text(
            0.5,
            0.95,
            rf"rank: {rank}",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#bbbbbb", alpha=0.92),
        )
    axes[0].set_ylabel(r"Effective efficiency $\eta_{\mathrm{eff}}$")
    fig.suptitle(
        r"E2 open bus at $T_{\mathrm{out}}=36^\circ$C: humidity collapses $\eta_{\mathrm{eff}}$",
        fontsize=12,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(FIG / "e2_B_eta_eff.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # ----- E3: short-circuit loss vs wind (fill under no-leak baseline) -----
    rows = e3_wind_shortcircuit(BUS_STOP_OPEN, GENERIC_SUMMER, BUS_OCC)
    k_show = [0.0, 1.0, 2.0, 3.0]
    colors_k = ["#4c72b0", "#55a868", "#dd8452", "#c44e52"]
    curves = {}
    for k in k_show:
        pts = sorted(
            (r.x1, r.eta_mix)
            for r in rows
            if r.system_id == "B" and abs(r.x2 - k) < 1e-9
        )
        if pts:
            curves[k] = pts
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    base_x, base_y = zip(*curves[0.0])
    ax.plot(base_x, base_y, "-", color=colors_k[0], lw=2.6, label=r"$k_{\mathrm{sc}}=0$ (no short-circuit)")
    for k, col in zip(k_show[1:], colors_k[1:]):
        xs, ys = zip(*curves[k])
        ax.plot(xs, ys, "-o", color=col, lw=2.0, ms=5, label=rf"$k_{{\mathrm{{sc}}}}={k:.0f}$")
        ax.fill_between(xs, ys, 1.0, color=col, alpha=0.18)
    ax.set_xlabel("Wind speed (m/s)")
    ax.set_ylabel(r"Mixing / short-circuit factor $\eta_{\mathrm{mix}}$")
    ax.set_title(r"E3 system B: aiming into wind drains chilled air (shaded = loss vs $\eta_{\mathrm{mix}}=1$)")
    ax.grid(True, alpha=0.35)
    ax.legend(title="Orientation proxy", frameon=True, loc="lower left")
    ax.set_ylim(0, 1.08)
    ax.annotate(
        "stronger aiming into\nopenings → more loss",
        xy=(3.5, 0.22),
        xytext=(2.0, 0.45),
        textcoords="data",
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="#555555"),
        color="#333333",
    )
    fig.tight_layout()
    fig.savefig(FIG / "e3_B_eta_mix.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # ----- keep E5 tornado + E6 2x2 with mathtext -----
    from model.sensitivity import e5_oat, e6_v1_vs_v2
    from model.params import PHOENIX, RAIL_OCC, RAIL_SEMI, SINGAPORE

    oat = e5_oat(BUS_STOP_OPEN, GENERIC_SUMMER, BUS_OCC)
    by_param = {}
    for r in oat:
        if r.system_id != "B" or abs(abs(r.pct_change) - 0.2) > 1e-9:
            continue
        if r.elasticity != r.elasticity:
            continue
        by_param.setdefault(r.param, []).append(r.elasticity)
    label_map = {
        "rh": "Relative humidity",
        "a_open_m2": r"$A_{\mathrm{open}}$",
        "covered_fraction": "Occupancy coverage",
        "k_sc": r"$k_{\mathrm{sc}}$",
        "wind_m_s": "Wind speed",
        "power_kw": "Electrical power",
        "openness": "Openness",
        "height_m": "Shelter height",
        "t_out_c": r"$T_{\mathrm{out}}$",
    }
    items = sorted(
        ((label_map.get(p, p), sum(v) / len(v)) for p, v in by_param.items() if v),
        key=lambda kv: abs(kv[1]),
    )
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    labels = [p for p, _ in items]
    vals = [v for _, v in items]
    colors = ["#c44e52" if v < 0 else "#4c72b0" for v in vals]
    ax.barh(labels, vals, color=colors)
    ax.axvline(0.0, color="k", lw=0.8)
    ax.set_xlabel(r"Elasticity of $\eta_{\mathrm{eff}}$ at $\pm$20% OAT")
    ax.set_title(r"E5 OAT tornado: open bus, evaporative system B")
    fig.tight_layout()
    fig.savefig(FIG / "e5_tornado_bus_B.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    blocks = [
        e6_v1_vs_v2(BUS_STOP_OPEN, GENERIC_SUMMER, BUS_OCC, semi_open=False, case_label="bus"),
        e6_v1_vs_v2(RAIL_SEMI, GENERIC_SUMMER, RAIL_OCC, semi_open=True, case_label="rail"),
        e6_v1_vs_v2(BUS_STOP_OPEN, PHOENIX, BUS_OCC, semi_open=False, case_label="phoenix"),
        e6_v1_vs_v2(RAIL_SEMI, SINGAPORE, RAIL_OCC, semi_open=True, case_label="singapore"),
    ]
    rows = []
    for b in blocks:
        rows.extend(b)
    cases = [
        ("bus", "Open bus (generic)"),
        ("rail", "Semi-open rail"),
        ("phoenix", "Phoenix open bus"),
        ("singapore", "Singapore semi-open"),
    ]
    sids = ["A", "B", "C"]
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 8.0), sharey=True)
    axes_flat = axes.ravel()
    handles = labels = None
    for ax, (case, title) in zip(axes_flat, cases):
        x = np.arange(len(sids))
        w = 0.36
        v1, v2 = [], []
        for sid in sids:
            r1 = next(r for r in rows if r.system_id == sid and r.label == f"{case}:v1")
            r2 = next(r for r in rows if r.system_id == sid and r.label == f"{case}:v2")
            v1.append(r1.eta_eff)
            v2.append(r2.eta_eff)
        ax.bar(x - w / 2, v1, w, label="Baseline algebra (V1)", color="#4c72b0")
        ax.bar(x + w / 2, v2, w, label="Fluids layer (V2)", color="#dd8452")
        ax.set_xticks(x)
        ax.set_xticklabels(sids)
        ax.set_title(title, pad=8)
        ax.grid(True, axis="y", alpha=0.3)
        ax.set_xlabel("System")
        handles, labels = ax.get_legend_handles_labels()
    axes_flat[0].set_ylabel(r"$\eta_{\mathrm{eff}}$")
    axes_flat[2].set_ylabel(r"$\eta_{\mathrm{eff}}$")
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=2,
        frameon=True,
        fontsize=11,
        bbox_to_anchor=(0.5, 0.01),
    )
    fig.suptitle(
        r"E6: $\eta_{\mathrm{eff}}$ across cases — baseline algebra vs fluids layer",
        fontsize=13,
        y=0.995,
    )
    fig.tight_layout(rect=[0, 0.06, 1, 0.97])
    fig.savefig(FIG / "e6_v1_vs_v2_bars.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("Wrote figures to", FIG)


if __name__ == "__main__":
    main()
