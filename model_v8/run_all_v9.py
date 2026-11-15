"""Regenerate all v9 numeric artifacts."""

from __future__ import annotations

import numpy as np

from .m3_cei import reproduce_v7_cei


def main() -> None:
    reg = reproduce_v7_cei()
    print("V7 CEI regression", np.round(reg["cei"], 3))
    assert np.allclose(reg["cei"], reg["target"], atol=0.02)

    from . import (
        cei_weight_perturb,
        run_e6_ablation,
        run_flip_ablation,
        run_latent_ablation,
        run_seats,
        run_v8,
    )

    run_flip_ablation.main()
    cei_weight_perturb.main()
    run_seats.main()
    run_latent_ablation.main()
    run_v8.main()
    run_e6_ablation.main()
    print("ALL v9 numeric runs done")


if __name__ == "__main__":
    main()
