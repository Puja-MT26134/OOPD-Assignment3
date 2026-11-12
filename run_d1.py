# run_d1.py  -- D1 strong scaling
# usage:  python run_d1.py          (full experiment)
#         python run_d1.py quick    (tiny test to check the script works)

import csv
import os
import re
import statistics
import subprocess
import sys

exe = "sim.exe"
N = 4000
days = 200
reps = 5

if len(sys.argv) > 1 and sys.argv[1] == "quick":
    N = 500
    days = 20
    reps = 2

os.makedirs("results", exist_ok=True)
os.makedirs("out", exist_ok=True)

# thread counts: 1, 2, 4, ... up to twice the number of logical cores
logical = os.cpu_count()
thread_list = []
t = 1
while t <= 2 * logical:
    thread_list.append(t)
    t = t * 2


def run_once(T):
    """Run the simulation once and return the time it measured."""
    command = [exe,
               "--N", str(N),
               "--days", str(days),
               "--fixed-days", "1",
               "--mode", "pool",
               "--threads", str(T),
               "--chunks", str(T),
               "--partition", "strips",
               "--out", "out/d1.csv"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    match = re.search(r"in ([0-9.]+(?:[eE][+-]?[0-9]+)?)", result.stdout)
    return float(match.group(1))


raw_file = "results/d1_raw.csv" if N == 4000 else "results/d1_quick.csv"
print("Logical cores:", logical, "  Thread counts:", thread_list)

all_times = {}
with open(raw_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["threads", "rep", "seconds"])
    for T in thread_list:
        all_times[T] = []
        for rep in range(1, reps + 1):
            seconds = run_once(T)
            all_times[T].append(seconds)
            writer.writerow([T, rep, seconds])
            f.flush()   # save every result straight away
            print(f"T={T:2d} rep {rep}/{reps}: {seconds:.3f} s")

print()
print("T    median      min      max   speedup")
base = statistics.median(all_times[1])
for T in thread_list:
    median = statistics.median(all_times[T])
    print(f"{T:2d}  {median:8.3f} {min(all_times[T]):8.3f} {max(all_times[T]):8.3f}   {base / median:5.2f}")