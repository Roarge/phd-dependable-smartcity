#!/usr/bin/env python3
"""Does Theory of Mind help collaboration and harm competition?

Generalises the desire model with a shared-anchor weight sigma (the
collaboration<->competition axis). sigma=1 is the published model (shared
common goal at full weight); sigma=0 removes the common goal, leaving only
the two opposing private targets (pure competition). Goal alignment gamma
down-weights the private targets as before.

Three regimes, each with Theory of Mind OFF (alterity 0) and ON (alterity
0.5 symmetric), at goal alignment gamma as noted:

  COMPETITION   sigma=0.0, gamma=0  : only the opposing private goals
  MIXED         sigma=1.0, gamma=0  : shared + opposing private, equal (= A1/A2)
  COLLABORATION sigma=1.0, gamma=1  : only the shared goal (= Model 3/Model 4)

Protocol identical to the main ensemble: per-(condition, seed) reseeding,
one 60-target sweep per seed, 200 epochs, module defaults. Exploratory at
3 seeds. F_Sigma end state = mean of last 10 epochs; measured against the
shared-target generative density in every regime (the collective's expected
state does not move).
"""
import json
import os
import sys
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phas_eai.core.simulation import (
    single_run, MAX_SENSE_PROBABILITY, EPOCHS, ENV_SIZE,
    _system_free_energy_data,
)

SEEDS = [20260702 + k for k in range(3)]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_competition")

CONDITIONS = {
    "COMP_noToM":   dict(shared_weight=0.0, alignment=0.0, alterity=(0, 0)),
    "COMP_ToM":     dict(shared_weight=0.0, alignment=0.0, alterity=(0.5, 0.5)),
    "MIX_noToM":    dict(shared_weight=1.0, alignment=0.0, alterity=(0, 0)),
    "MIX_ToM":      dict(shared_weight=1.0, alignment=0.0, alterity=(0.5, 0.5)),
    "COLLAB_noToM": dict(shared_weight=1.0, alignment=1.0, alterity=(0, 0)),
    "COLLAB_ToM":   dict(shared_weight=1.0, alignment=1.0, alterity=(0.5, 0.5)),
}


def run_sweep(cond, params, seed):
    np.random.seed(seed)
    epochs = EPOCHS
    q_emp = np.zeros([epochs, ENV_SIZE])
    weak_final, shared_hits = [], []
    for shared_target in range(ENV_SIZE):
        t1, c1, b1, psi1, t2, c2, b2, psi2, g1, g2 = single_run(
            shared_target, MAX_SENSE_PROBABILITY,
            params["alterity"], params["alignment"],
            shared_weight=params["shared_weight"], epochs=epochs,
        )
        weak_final.append(float(np.asarray(c2)[-1]))
        shared_hits.append(1.0 if t2 == "shared target" else 0.0)
        for t in range(epochs):
            q_emp[t, psi1[t] - shared_target] += 1
            q_emp[t, psi2[t] - shared_target] += 1
    fe = np.asarray(_system_free_energy_data(q_emp, epochs)["FE"].values, dtype=float)
    return dict(cond=cond, seed=seed, fe_last10=float(fe[-10:].mean()),
                weak_final=float(np.mean(weak_final)),
                shared_share=float(np.mean(shared_hits)))


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = [(c, p, s) for c, p in CONDITIONS.items() for s in SEEDS]
    rows = []
    with ProcessPoolExecutor(max_workers=7) as ex:
        futs = {ex.submit(run_sweep, c, p, s): (c, s) for c, p, s in jobs}
        done = 0
        for f in as_completed(futs):
            r = f.result(); rows.append(r); done += 1
            print(f"[{done}/{len(jobs)}] {r['cond']} seed {r['seed']} "
                  f"F_last10={r['fe_last10']:.2f}", flush=True)
    summ = {}
    for c in CONDITIONS:
        fe = np.array([r["fe_last10"] for r in rows if r["cond"] == c])
        wk = np.array([r["weak_final"] for r in rows if r["cond"] == c])
        sh = np.array([r["shared_share"] for r in rows if r["cond"] == c])
        summ[c] = dict(fe_mean=float(fe.mean()), fe_sd=float(fe.std(ddof=1)),
                       fe_vals=[float(x) for x in fe],
                       weak_mean=float(wk.mean()), shared_share=float(sh.mean()))
    # ToM effect (ToM minus noToM) per regime, paired by seed
    def paired(regime):
        tom = {r["seed"]: r["fe_last10"] for r in rows if r["cond"] == f"{regime}_ToM"}
        non = {r["seed"]: r["fe_last10"] for r in rows if r["cond"] == f"{regime}_noToM"}
        d = np.array([tom[s] - non[s] for s in SEEDS])
        return dict(mean=float(d.mean()), sd=float(d.std(ddof=1)), vals=[float(x) for x in d])
    summ["ToM_effect_on_Fsigma"] = {r: paired(r) for r in ["COMP", "MIX", "COLLAB"]}
    json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=2)
    print("\n=== ToM effect on F_Sigma (positive = detrimental) ===")
    for r in ["COMP", "MIX", "COLLAB"]:
        e = summ["ToM_effect_on_Fsigma"][r]
        print(f"  {r:14s} dF = {e['mean']:+.2f} +- {e['sd']:.2f}   "
              f"(noToM {summ[r+'_noToM']['fe_mean']:.1f} -> ToM {summ[r+'_ToM']['fe_mean']:.1f})")


if __name__ == "__main__":
    main()
