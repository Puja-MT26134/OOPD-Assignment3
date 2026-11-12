# run_d5.py -- D5: hiding I/O time
# usage:  python run_d5.py          (full experiment)
#         python run_d5.py quick    (tiny test)

import csv
import os
import re
import shutil
import subprocess
import sys

exe = "sim.exe"
N = 1000
days = 100
reps = 5
threads = 4
chunks = 16
latencies = [0, 20, 100]          # ms
ks = [20, 10, 5, 2]               # snapshot every K days
q_default = 4
q_values = [1, 2, 4, 8, 16]
q_latency = 100
q_k = 2

if len(sys.argv) > 1 and sys.argv[1] == "quick":
    N = 300
    days = 30
    reps = 2
    latencies = [0, 20]
    ks = [10, 5]
    q_values = [1, 4]
    q_latency = 20
    q_k = 5

snap_dir = "out/snaps_d5"
os.makedirs("results", exist_ok=True)
os.makedirs("out", exist_ok=True)


def run_once(mode, latency, K, Q):
    """Run one simulation; return (seconds, max pending writes)."""
    command = [exe,
               "--N", str(N),
               "--days", str(days),
               "--fixed-days", "1",
               "--mode", "pool",
               "--threads", str(threads),
               "--chunks", str(chunks),
               "--partition", "strips",
               "--out", "out/d5.csv"]
    if mode != "none":
        command += ["--snapshot-every", str(K),
                    "--snapshot-mode", mode,
                    "--max-pending", str(Q),
                    "--io-latency", str(latency),
                    "--snapshot-dir", snap_dir]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    out = result.stdout
    seconds = float(re.search(r"in ([0-9.]+(?:[eE][+-]?[0-9]+)?)", out).group(1))
    m = re.search(r"max pending: (\d+)", out)
    max_pending = int(m.group(1)) if m else 0
    f = re.search(r"failed writes: (\d+)", out)
    if f and f.group(1) != "0":
        print("WARNING: failed writes:", f.group(1))
    return seconds, max_pending


# all configurations: (experiment, mode, latency, K, Q)
jobs = [("main", "none", 0, 0, 0)]
for L in latencies:
    for K in ks:
        jobs.append(("main", "blocking", L, K, 0))
        jobs.append(("main", "async", L, K, q_default))
for Q in q_values:
    jobs.append(("q", "async", q_latency, q_k, Q))

raw_file = "results/d5_raw.csv" if N == 1000 else "results/d5_quick.csv"

print("Warming up...")
for k in range(5):
    run_once("none", 0, 0, 0)

with open(raw_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["experiment", "mode", "latency", "K", "Q", "rep", "seconds", "maxpending"])
    for rep in range(1, reps + 1):
        for (experiment, mode, L, K, Q) in jobs:
            seconds, max_pending = run_once(mode, L, K, Q)
            writer.writerow([experiment, mode, L, K, Q, rep, seconds, max_pending])
            f.flush()
        print(f"repetition {rep}/{reps} done")

shutil.rmtree(snap_dir, ignore_errors=True)   # remove the snapshot images
print("Finished. Raw results in", raw_file)