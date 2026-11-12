# plot_d4.py -- table and graph for D4
import csv
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

total_runs = 32
times = {}
with open("results/d4_raw.csv") as f:
    for row in csv.DictReader(f):
        key = (int(row["R"]), int(row["T"]))
        times.setdefault(key, []).append(float(row["seconds"]))

combos = list(times)
print("R x T   threads   median(s)   min    max    runs/second")
labels, rates, lows, highs = [], [], [], []
for (R, T) in combos:
    t = times[(R, T)]
    med = statistics.median(t)
    rate = total_runs / med
    print(f"{R} x {T}      {R * T:2d}      {med:8.3f}  {min(t):6.3f} {max(t):6.3f}   {rate:6.2f}")
    labels.append(f"{R}x{T}")
    rates.append(rate)
    lows.append(rate - total_runs / max(t))
    highs.append(total_runs / min(t) - rate)

plt.figure(figsize=(7, 4.5))
plt.bar(labels, rates, yerr=[lows, highs], capsize=3)
plt.xlabel("R runs at once x T threads per run")
plt.ylabel("runs completed per second")
plt.title("D4: parallelism within a run vs across runs (32 runs)")
plt.grid(True, axis="y")
plt.savefig("results/d4_runs_per_second.png", dpi=150, bbox_inches="tight")
print("Saved graph in the results folder")