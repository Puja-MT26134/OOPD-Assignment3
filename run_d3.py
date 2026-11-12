# run_d3.py -- D3: size of work units (interleaved version)
# Every repetition runs ALL configurations once, so that slow or fast
# periods of the machine affect every configuration equally.
# usage:  python run_d3.py          (full experiment)
#         python run_d3.py quick    (tiny test)

import csv
import os
import re
import subprocess
import sys

exe = "sim.exe"
physical = 4          # physical cores of this laptop
reps = 5
N_big = 2000
days_big = 100
days_small = 200
sizes = [50, 100, 150, 200, 300, 400, 500, 750, 1000]

if len(sys.argv) > 1 and sys.argv[1] == "quick":
    reps = 2
    N_big = 500
    days_big = 20
    days_small = 20
    sizes = [50, 100, 200]

os.makedirs("results", exist_ok=True)
os.makedirs("out", exist_ok=True)


def run_once(N, days, mode, threads, chunks, partition):
    command = [exe,
               "--N", str(N),
               "--days", str(days),
               "--fixed-days", "1",
               "--mode", mode,
               "--threads", str(threads),
               "--chunks", str(chunks),
               "--partition", partition,
               "--out", "out/d3.csv"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    match = re.search(r"in ([0-9.]+(?:[eE][+-]?[0-9]+)?)", result.stdout)
    return float(match.group(1))


# the list of all configurations: (experiment, N, days, mode, threads, chunks, partition)
jobs = []

# D3a: number of chunks, from T to 64T
for k in [1, 2, 4, 8, 16, 32, 64]:
    jobs.append(("chunks", N_big, days_big, "pool", physical, physical * k, "strips"))

# D3b: the three ways of dividing the grid
for partition in ["strips", "blocks", "interleaved"]:
    for C in [4, 16, 64]:
        jobs.append(("schemes", N_big, days_big, "pool", physical, C, partition))

# D3c: small grids
for N in sizes:
    jobs.append(("small", N, days_small, "sequential", 1, 1, "strips"))
    jobs.append(("small", N, days_small, "thread-per-day", physical, physical, "strips"))
    jobs.append(("small", N, days_small, "pool", physical, physical, "strips"))

raw_file = "results/d3_raw.csv" if N_big == 2000 else "results/d3_quick.csv"

# warm-up: untimed runs so the machine settles before measuring
print("Warming up...")
for k in range(8):
    run_once(1000, 100, "pool", physical, physical, "strips")

with open(raw_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["experiment", "mode", "partition", "threads", "chunks", "N", "rep", "seconds"])

    for rep in range(1, reps + 1):
        for (experiment, N, days, mode, threads, chunks, partition) in jobs:
            seconds = run_once(N, days, mode, threads, chunks, partition)
            writer.writerow([experiment, mode, partition, threads, chunks, N, rep, seconds])
            f.flush()
        print(f"repetition {rep}/{reps} done")

print("Finished. Raw results in", raw_file)