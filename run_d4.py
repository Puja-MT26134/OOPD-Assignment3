# run_d4.py -- D4: R runs at once, each with T threads
# usage:  python run_d4.py          (full experiment)
#         python run_d4.py quick    (tiny test)

import csv
import os
import re
import subprocess
import sys

exe = "sweep.exe"
N = 500
days = 300
seeds = 2
total_runs = 32
reps = 5

# (R, T): R runs at once, each with T threads
combos = [(1, 4), (2, 2), (4, 1),      # 4 physical cores
          (1, 8), (2, 4), (4, 2), (8, 1)]   # 8 logical cores

if len(sys.argv) > 1 and sys.argv[1] == "quick":
    N = 200
    reps = 2

os.makedirs("results", exist_ok=True)
os.makedirs("out", exist_ok=True)
result_file = "out/d4_sweep.csv"


def run_sweep(R, T):
    """Run the 32-run sweep once and return the total time in seconds."""
    command = [exe,
               "--N", str(N),
               "--days", str(days),
               "--seeds", str(seeds),
               "--max-runs", str(total_runs),
               "--workers", str(R),
               "--threads", str(T),
               "--out", result_file]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    match = re.search(r"Finished (\d+) of (\d+) runs in ([0-9.]+)", result.stdout)
    if match is None or match.group(1) != str(total_runs):
        raise RuntimeError(f"sweep did not finish all runs for R={R}, T={T}")
    return float(match.group(3))


def read_sorted():
    with open(result_file) as f:
        return sorted(f.read().splitlines()[1:])


raw_file = "results/d4_raw.csv" if N == 500 else "results/d4_quick.csv"

# warm-up
print("Warming up...")
for k in range(2):
    run_sweep(4, 1)

reference = None
with open(raw_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["R", "T", "rep", "seconds"])
    for rep in range(1, reps + 1):
        for (R, T) in combos:
            seconds = run_sweep(R, T)
            # every combination must give exactly the same results
            rows = read_sorted()
            if reference is None:
                reference = rows
            elif rows != reference:
                print(f"WARNING: results differ for R={R}, T={T}")
            writer.writerow([R, T, rep, seconds])
            f.flush()
        print(f"repetition {rep}/{reps} done")

print("Finished. Raw results in", raw_file)