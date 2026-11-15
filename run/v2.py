# run E1–E6 sweeps → out/*.csv (+ optional plots)
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.a import H0, H1, L0, L1, L2, O0, O1
from sweep import h as sw

OUT = ROOT / "out"


def has_mpl():
    try:
        import matplotlib  # noqa
        matplotlib.use("Agg")
        return True
    except ImportError:
        return False


def heat(path, xs, ys, z, title, xl, yl, cb):
    import matplotlib.pyplot as plt
    import numpy as np
    fig, ax = plt.subplots(figsize=(5.2, 4.2))
    im = ax.imshow(np.array(z), origin="lower", aspect="auto",
                   extent=[xs[0], xs[-1], ys[0], ys[-1]])
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, label=cb)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def pivot(rows, sid, n1, n2, attr, x3=None):
    xs = sorted({r.x1 for r in rows if r.sid == sid and r.n1 == n1})
    ys = sorted({r.x2 for r in rows if r.sid == sid and r.n2 == n2})
    sub = [r for r in rows if r.sid == sid and (x3 is None or abs(r.x3 - x3) < 1e-9)]
    z = []
    for y in ys:
        row = []
        for x in xs:
            vs = [getattr(r, attr) for r in sub if abs(r.x1 - x) < 1e-9 and abs(r.x2 - y) < 1e-9]
            row.append(sum(vs) / len(vs) if vs else float("nan"))
        z.append(row)
    return xs, ys, z


def tornado(path, rows, sid, title):
    import matplotlib.pyplot as plt
    bag = defaultdict(list)
    for r in rows:
        if r.sid != sid or abs(abs(r.pct) - 0.2) > 1e-9:
            continue
        if r.el == r.el:
            bag[r.p].append(r.el)
    items = sorted(((p, sum(v) / len(v)) for p, v in bag.items() if v), key=lambda kv: abs(kv[1]))
    if not items:
        return
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    labs = [p for p, _ in items]
    vals = [v for _, v in items]
    ax.barh(labs, vals, color=["#c44e52" if v < 0 else "#4c72b0" for v in vals])
    ax.axvline(0, color="k", lw=0.8)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plot = has_mpl()
    print("out=", OUT, "plot=", plot)

    print("E1")
    e1 = sw.e1(L2, H0, O0)
    sw.wcsv(OUT / "e1.csv", e1)
    if plot:
        hs = sorted({r.x3 for r in e1})
        hm = hs[len(hs) // 2]
        for sid, at in (("B", "fu"), ("B", "eta"), ("C", "eta")):
            xs, ys, z = pivot(e1, sid, "openness", "a_open", at, x3=hm)
            if xs and ys:
                heat(OUT / f"e1_{sid}_{at}.png", xs, ys, z, f"E1 {sid} {at}", "o", "A_open", at)

    print("E2")
    e2 = sw.e2(H0, O0)
    sw.wcsv(OUT / "e2.csv", e2)
    if plot:
        for sid in ("A", "B", "C"):
            xs, ys, z = pivot(e2, sid, "t_out", "rh", "eta")
            if xs and ys:
                heat(OUT / f"e2_{sid}.png", xs, ys, z, f"E2 {sid}", "T", "RH", "eta")

    print("E3")
    e3 = sw.e3(H0, L2, O0)
    sw.wcsv(OUT / "e3.csv", e3)
    if plot:
        for sid in ("B", "C"):
            xs, ys, z = pivot(e3, sid, "wind", "k_sc", "m")
            if xs and ys:
                heat(OUT / f"e3_{sid}_m.png", xs, ys, z, f"E3 {sid} mix", "wind", "k_sc", "m")

    print("E4")
    e4 = sw.e4(H0, L2)
    sw.wcsv(OUT / "e4.csv", e4)

    print("E5")
    e5b = sw.e5(H0, L2, O0, so=False)
    e5r = sw.e5(H1, L2, O1, so=True)
    sw.woat(OUT / "e5_bus.csv", e5b)
    sw.woat(OUT / "e5_rail.csv", e5r)
    if plot:
        for sid in ("A", "B", "C"):
            tornado(OUT / f"e5_bus_{sid}.png", e5b, sid, f"E5 bus {sid}")
            tornado(OUT / f"e5_rail_{sid}.png", e5r, sid, f"E5 rail {sid}")

    print("E6")
    e6 = []
    for lab, h, c, o, so in (
        ("bus", H0, L2, O0, False),
        ("rail", H1, L2, O1, True),
        ("phx", H0, L0, O0, False),
        ("sgp", H1, L1, O1, True),
    ):
        e6.extend(sw.e6(h, c, o, so=so, lab=lab))
    sw.wcsv(OUT / "e6.csv", e6)
    for case in ("bus", "rail", "phx", "sgp"):
        for mode in ("v1", "v2"):
            sub = [r for r in e6 if r.lab == f"{case}:{mode}"]
            order = [r.sid for r in sorted(sub, key=lambda x: x.eta, reverse=True)]
            print(case, mode, " > ".join(order))
    print("done")


if __name__ == "__main__":
    main()
