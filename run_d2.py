# run_d2.py -- D2 weak scaling (work per thread stays the same)
# usage:  python run_d2.py          (full experiment)
#         python run_d2.py quick    (tiny test)

import csv
import math
import os
import re
import statistics
import subprocess
import sys

exe = "sim.exe"
cells_per_thread = 1000 * 1000
days = 200
reps = 5

if len(sys.argv) > 1 and sys.argv[1] == "quick":
    cells_per_thread = 300 * 300
    days = 20
    reps = 2

os.makedirs("results", exist_ok=True)
os.makedirs("out", exist_ok=True)

thread_list = [1, 2, 4, 8, 16]


def run_once(T, N):
    command = [exe,
               "--N", str(N),
               "--days", str(days),
               "--fixed-days", "1",
               "--mode", "pool",
               "--threads", str(T),
               "--chunks", str(T),
               "--partition", "strips",
               "--out", "out/d2.csv"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    match = re.search(r"in ([0-9.]+(?:[eE][+-]?[0-9]+)?)", result.stdout)
    return float(match.group(1))


raw_file = "results/d2_raw.csv" if days == 200 else "results/d2_quick.csv"
all_times = {}
with open(raw_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["threads", "N", "rep", "seconds"])
    for T in thread_list:
        N = round(math.sqrt(cells_per_thread * T))
        all_times[T] = []
        for rep in range(1, reps + 1):
            seconds = run_once(T, N)
            all_times[T].append(seconds)
            writer.writerow([T, N, rep, seconds])
            f.flush()
            print(f"T={T:2d} N={N:4d} rep {rep}/{reps}: {seconds:.3f} s")

print()
print("T     N   median      min      max   efficiency")
base = statistics.median(all_times[1])
for T in thread_list:
    N = round(math.sqrt(cells_per_thread * T))
    median = statistics.median(all_times[T])
    print(f"{T:2d} {N:5d} {median:8.3f} {min(all_times[T]):8.3f} {max(all_times[T]):8.3f}   {base / median:5.2f}")