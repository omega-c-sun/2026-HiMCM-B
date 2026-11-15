# print baseline case tables (bus/rail/phx/sgp)
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from case import g


def fmt(rows):
    hs = ["sid", "eta", "qe", "fu", "cv", "safe", "lcc", "bud", "ok", "cps", "co2"]
    lines = ["  ".join(f"{x:>8}" for x in hs)]
    for r in rows:
        cps = f"{r.cps:8.2f}" if r.cps < 1e12 else f"{'inf':>8}"
        lines.append("  ".join([
            f"{r.sid:>8}", f"{r.eta:8.3f}", f"{r.qe:8.1f}", f"{r.fu:8.3f}",
            f"{r.cv:8.3f}", f"{'Y' if r.safe else 'N':>8}", f"{r.lcc:8.0f}",
            f"{r.bud:8.0f}", f"{'Y' if r.ok else 'N':>8}", cps, f"{r.co2:8.0f}",
        ]))
    return "\n".join(lines)


def main():
    d = g.all()
    for k, t in [
        ("bus", "open bus"),
        ("rail", "semi-open rail"),
        ("phx", "Phoenix bus"),
        ("sgp", "Singapore rail"),
    ]:
        rows = d[k]
        print("-" * 60)
        print(t)
        print(fmt(rows))
        print("eta:", " > ".join(g.rank_eta(rows)))
        print("ok cps:", " > ".join(g.rank_ok(rows)) or "(none)")
    print("phx", " > ".join(g.rank_eta(d["phx"])))
    print("sgp", " > ".join(g.rank_eta(d["sgp"])))


if __name__ == "__main__":
    main()
