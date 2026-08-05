"""
Multi-Seed Ensemble Comparison
==============================

Runs every compared condition in ONE script under per-(condition, seed)
reseeding, so that endpoint statistics carry dispersion and any claim that
names Kaufmann's published Model 4 binds to the published parameterisation.

Conditions:
  - The paper's own factorial A1 to A6 (symmetric alterity 0.5, alignment
    0.5) plus A7, the scaffold-with-alignment-without-ToM cell.
  - Kaufmann's published parameterisations (Kaufmann et al. 2021, Table 2):
    M2pub (weak-only ToM), M3pub (alignment 1), and M4pub in both alterity
    variants (0.2 published primary, 0.5 published footnote). The published
    Model 1 parameterisation equals A1, so it needs no separate condition.
  - The combined-model conditions S_DYN (scaffold + dynamic gamma) and
    F_FULL (the full PHAS-EAI model).

Protocol per (condition, seed): np.random.seed(seed); no_of_cycles full
sweeps of the shared target across all 60 cells, 200 epochs each (module
defaults for gradient steps and learning rate).

Outputs (results/ensemble/): one .npz per (condition, seed) with the system
free-energy trajectory, mean convergence trajectories, per-run final
distances, target-pursuit shares, and mean gamma traces, plus summary.json
with across-seed statistics.

Usage:
    python -m phas_eai.experiments.run_ensemble [--seeds 5] [--base-seed 20260702]
                                                [--cycles 1] [--workers 7] [--quick]
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from phas_eai.core.simulation import (  # noqa: E402
    single_run, MAX_SENSE_PROBABILITY, EPOCHS, ENV_SIZE,
    _system_free_energy_data,
)

SCAFFOLD = dict(h=(0.0, 0.3), niche_construction=True, niche_boost=0.25,
                niche_radius=3, practice_interval=20, practice_fidelity=0.5)

# Labelling rule: Kaufmann's published Model labels are reserved for
# conditions matching Kaufmann et al. (2021) Table 2 (the recreated published
# parameterisations live in simulation/kaufmann/). A-prefixed conditions are
# this project's own factorial levels (symmetric alterity 0.5, goal alignment
# 0.5), which differ from the published Model 2 to 4 parameterisations.
CONDITIONS = {
    "A1":        dict(alterity=(0, 0),     alignment=0),
    "A2":        dict(alterity=(0.5, 0.5), alignment=0),
    "A3":        dict(alterity=(0, 0),     alignment=0.5),
    "A4":        dict(alterity=(0.5, 0.5), alignment=0.5),
    "A5":        dict(alterity=(0, 0),     alignment=0,   **SCAFFOLD),
    "A6":        dict(alterity=(0.5, 0.5), alignment=0.5, **SCAFFOLD),
    "A7":        dict(alterity=(0, 0),     alignment=0.5, **SCAFFOLD),
    "M2pub":     dict(alterity=(0, 0.5),   alignment=0),
    "M3pub":     dict(alterity=(0, 0),     alignment=1),
    "M4pub_a02": dict(alterity=(0, 0.2),   alignment=1),
    "M4pub_a05": dict(alterity=(0, 0.5),   alignment=1),
    "S_DYN":     dict(alterity=(0, 0),     alignment=0.0,
                      dynamic_gamma=True, gamma_lr=0.01, **SCAFFOLD),
    "F_FULL":    dict(alterity=(0.5, 0.5), alignment=0.5,
                      dynamic_gamma=True, gamma_lr=0.01, **SCAFFOLD),
}


def run_sweep(cond_key, params, seed, no_of_cycles=1, epochs=EPOCHS):
    """Run no_of_cycles 60-target sweeps under one seed for one condition."""
    np.random.seed(seed)
    ep1 = epochs + 1
    n_runs = no_of_cycles * ENV_SIZE
    q_empirical = np.zeros([epochs, ENV_SIZE])
    conv_strong = np.zeros([n_runs, ep1])
    conv_weak = np.zeros([n_runs, ep1])
    labels_strong, labels_weak = [], []
    gamma_strong = np.zeros([n_runs, ep1])
    gamma_weak = np.zeros([n_runs, ep1])
    for cycle in range(no_of_cycles):
        for shared_target in range(ENV_SIZE):
            i = cycle * ENV_SIZE + shared_target
            t1, c1, b1, psi1, t2, c2, b2, psi2, g1, g2 = single_run(
                shared_target, MAX_SENSE_PROBABILITY,
                params["alterity"], params["alignment"],
                h=params.get("h", (0.0, 0.0)),
                niche_construction=params.get("niche_construction", False),
                niche_boost=params.get("niche_boost", 0.15),
                niche_radius=params.get("niche_radius", 3),
                dynamic_gamma=params.get("dynamic_gamma", False),
                gamma_lr=params.get("gamma_lr", 0.01),
                practice_interval=params.get("practice_interval", 0),
                practice_fidelity=params.get("practice_fidelity", 0.5),
                epochs=epochs,
            )
            labels_strong.append(t1)
            labels_weak.append(t2)
            conv_strong[i] = np.asarray(c1)[:ep1]
            conv_weak[i] = np.asarray(c2)[:ep1]
            g1a = np.asarray(g1, dtype=float)
            g2a = np.asarray(g2, dtype=float)
            if g1a.size >= ep1:
                gamma_strong[i] = g1a[:ep1]
                gamma_weak[i] = g2a[:ep1]
            for t in range(epochs):
                q_empirical[t, psi1[t] - shared_target] += 1
                q_empirical[t, psi2[t] - shared_target] += 1
    fe = np.asarray(_system_free_energy_data(q_empirical, epochs)["FE"].values,
                    dtype=float)
    return dict(
        cond=cond_key, seed=seed, fe=fe,
        conv_strong_mean=conv_strong.mean(axis=0),
        conv_weak_mean=conv_weak.mean(axis=0),
        final_strong=conv_strong[:, -1],
        final_weak=conv_weak[:, -1],
        shared_share_strong=float(np.mean([l == "shared target" for l in labels_strong])),
        shared_share_weak=float(np.mean([l == "shared target" for l in labels_weak])),
        gamma_strong_mean=gamma_strong.mean(axis=0),
        gamma_weak_mean=gamma_weak.mean(axis=0),
    )


def summarise(out_dir, seeds):
    summary = {}
    for c in CONDITIONS:
        ep, l10, wk, st, sh_w, sh_s = [], [], [], [], [], []
        for s in seeds:
            path = os.path.join(out_dir, f"{c}_seed{s}.npz")
            if not os.path.exists(path):
                continue
            d = np.load(path)
            ep.append(float(d["fe"][-1]))
            l10.append(float(d["fe"][-10:].mean()))
            wk.append(float(d["final_weak"].mean()))
            st.append(float(d["final_strong"].mean()))
            sh_w.append(float(d["shared_share_weak"]))
            sh_s.append(float(d["shared_share_strong"]))
        if not ep:
            continue
        ep, l10, wk, st = map(np.asarray, (ep, l10, wk, st))
        summary[c] = dict(
            fe_endpoint_mean=float(ep.mean()),
            fe_endpoint_sd=float(ep.std(ddof=1)) if len(ep) > 1 else None,
            fe_last10_mean=float(l10.mean()),
            fe_last10_sd=float(l10.std(ddof=1)) if len(l10) > 1 else None,
            fe_endpoints=[float(x) for x in ep],
            weak_final_mean=float(wk.mean()),
            weak_final_sd=float(wk.std(ddof=1)) if len(wk) > 1 else None,
            strong_final_mean=float(st.mean()),
            strong_final_sd=float(st.std(ddof=1)) if len(st) > 1 else None,
            shared_share_weak_mean=float(np.mean(sh_w)),
            shared_share_strong_mean=float(np.mean(sh_s)),
            n_seeds=len(ep),
        )
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Multi-seed ensemble comparison")
    parser.add_argument("--seeds", type=int, default=5,
                        help="number of seeds per condition (default 5)")
    parser.add_argument("--base-seed", type=int, default=20260702,
                        help="first seed; seed k is base+k (default 20260702)")
    parser.add_argument("--cycles", type=int, default=1,
                        help="60-target sweeps per (condition, seed) (default 1)")
    parser.add_argument("--workers", type=int, default=7,
                        help="parallel worker processes (default 7)")
    parser.add_argument("--quick", action="store_true",
                        help="2 seeds, A1/A2/M4pub_a05 only (smoke test)")
    args = parser.parse_args()

    os.environ["PYTHONHASHSEED"] = "0"
    seeds = [args.base_seed + k for k in range(2 if args.quick else args.seeds)]
    conds = ({k: CONDITIONS[k] for k in ("A1", "A2", "M4pub_a05")}
             if args.quick else CONDITIONS)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "results", "ensemble")
    os.makedirs(out_dir, exist_ok=True)

    jobs = [(c, p, s) for c, p in conds.items() for s in seeds]
    t0 = time.time()
    done = 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {
            ex.submit(run_sweep, c, p, s, args.cycles): (c, s)
            for c, p, s in jobs
        }
        for fut in as_completed(futures):
            c, s = futures[fut]
            r = fut.result()
            np.savez(os.path.join(out_dir, f"{c}_seed{s}.npz"),
                     **{k: v for k, v in r.items() if k not in ("cond", "seed")})
            done += 1
            print(f"[{done}/{len(jobs)}] {c} seed {s} done "
                  f"({time.time() - t0:.0f}s elapsed)", flush=True)

    summary = summarise(out_dir, seeds)
    print(f"Wrote {out_dir}/summary.json ({len(summary)} conditions)")


if __name__ == "__main__":
    main()
