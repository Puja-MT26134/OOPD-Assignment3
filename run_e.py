# run_e.py -- Part E: epidemiology experiments
# usage:  python run_e.py default | beta | vacc | control | all

import csv
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

exe = "sim.exe"
N = 500
seeds = list(range(1, 11))     # 10 seeds
max_days = 20000                # safety limit; runs stop earlier when nobody is infected
workers = 4                    # simulations running at the same time

os.makedirs("results", exist_ok=True)
os.makedirs("out/e", exist_ok=True)

# each setting: (name, extra command line flags)
experiments = {
    "default": [("default", [])],
    "beta": [(f"beta{b}", ["--beta", str(b)])
             for b in [0.01, 0.02, 0.03, 0.035, 0.04, 0.045, 0.05, 0.06, 0.08, 0.10, 0.12, 0.16]],
    "vacc": [(f"v{v}", ["--v", str(v)])
             for v in [0, 0.1, 0.2, 0.3, 0.32, 0.34, 0.36, 0.38, 0.4, 0.42, 0.45, 0.5, 0.6, 0.8]],
    "control": [("baseline", []),
                ("mask0.7", ["--mask", "0.7"]),
                ("mask0.5", ["--mask", "0.5"]),
                                ("lockdown-default", ["--lockdown", "1"]),
                ("lockdown-low", ["--lockdown", "1", "--theta-on", "0.005", "--theta-off", "0.001"]),
                ("mask0.7+lockdown-default", ["--mask", "0.7", "--lockdown", "1"]),
                ("mask0.7+lockdown-low", ["--mask", "0.7", "--lockdown", "1", "--theta-on", "0.005", "--theta-off", "0.001"])],
}


def summarise(path):
    """Read one run's CSV and return its summary numbers."""
    with open(path) as f:
        rows = list(csv.DictReader(f))
    total = N * N
    peak = 0.0
    peak_day = 0
    for r in rows:
        fraction = int(r["I"]) / total
        if fraction > peak:
            peak = fraction
            peak_day = int(r["day"])
    last = rows[-1]
    ever_infected = int(last["I"]) + int(last["R"]) + int(last["D"])
    return peak, peak_day, ever_infected / total, int(last["D"]) / total, len(rows)


def work(job):
    name, extra, seed = job
    path = f"out/e/{name}_s{seed}.csv"
    command = [exe, "--N", str(N), "--days", str(max_days),
               "--seed", str(seed), "--out", path] + extra
    subprocess.run(command, capture_output=True, check=True)
    peak, peak_day, attack, deaths, days = summarise(path)
    return [name, seed, peak, peak_day, attack, deaths, days]


which = sys.argv[1] if len(sys.argv) > 1 else "all"
chosen = list(experiments) if which == "all" else [which]

for exp in chosen:
    jobs = [(name, extra, seed) for (name, extra) in experiments[exp] for seed in seeds]
    print(f"{exp}: running {len(jobs)} simulations ...")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(work, jobs))
    with open(f"results/e_{exp}.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["setting", "seed", "peak_fraction", "peak_day",
                         "attack_fraction", "death_fraction", "days"])
        writer.writerows(results)
    print(f"{exp}: done")