# plot_d1.py -- speedup, efficiency and Karp-Flatt for D1
import csv
import statistics
import matplotlib
matplotlib.use("Agg")   # draw into files, no window needed
import matplotlib.pyplot as plt

# read the raw timings
times = {}
with open("results/d1_raw.csv") as f:
    for row in csv.DictReader(f):
        T = int(row["threads"])
        times.setdefault(T, []).append(float(row["seconds"]))

threads = sorted(times)
median = {T: statistics.median(times[T]) for T in threads}
base = median[1]   # time with 1 thread

speedup = {}
efficiency = {}
karp = {}
for T in threads:
    speedup[T] = base / median[T]
    efficiency[T] = speedup[T] / T
    if T > 1:
        # Karp-Flatt: e(p) = (1/S - 1/p) / (1 - 1/p)
        karp[T] = (1 / speedup[T] - 1 / T) / (1 - 1 / T)

# serial fraction for Amdahl's law: use the Karp-Flatt value at 4 threads
# (4 = number of physical cores)
f_serial = karp[4] if 4 in karp else karp[min(karp)]

def amdahl(p):
    return 1 / (f_serial + (1 - f_serial) / p)

# print a table and save it
print("T   median(s)  min(s)  max(s)  speedup  efficiency  karp-flatt")
with open("results/d1_table.csv", "w", newline="") as out:
    writer = csv.writer(out)
    writer.writerow(["threads", "median", "min", "max", "speedup", "efficiency", "karp_flatt"])
    for T in threads:
        k = karp.get(T, "")
        writer.writerow([T, median[T], min(times[T]), max(times[T]),
                         speedup[T], efficiency[T], k])
        kk = f"{k:.4f}" if k != "" else "   -"
        print(f"{T:2d}  {median[T]:9.3f} {min(times[T]):7.3f} {max(times[T]):7.3f}  "
              f"{speedup[T]:7.2f}  {efficiency[T]:10.2f}  {kk}")
print(f"Serial fraction used for Amdahl (Karp-Flatt at 4 threads): {f_serial:.4f}")

# graph 1: speedup with min-max spread
lower = [speedup[T] - base / max(times[T]) for T in threads]
upper = [base / min(times[T]) - speedup[T] for T in threads]
plt.figure(figsize=(6, 4.5))
plt.errorbar(threads, [speedup[T] for T in threads], yerr=[lower, upper],
             marker="o", capsize=3, label="measured (median, min-max)")
plt.plot(threads, threads, "--", label="ideal")
plt.plot(threads, [amdahl(T) for T in threads], ":", label=f"Amdahl, f = {f_serial:.3f}")
plt.axvline(4, color="gray", linewidth=0.8)
plt.text(4.1, 0.5, "4 physical cores", fontsize=8)
plt.xlabel("threads")
plt.ylabel("speedup")
plt.title("D1: strong scaling (N = 4000, 200 days)")
plt.legend()
plt.grid(True)
plt.savefig("results/d1_speedup.png", dpi=150, bbox_inches="tight")

# graph 2: efficiency
plt.figure(figsize=(6, 4.5))
plt.plot(threads, [efficiency[T] for T in threads], marker="o")
plt.axhline(1.0, linestyle="--", color="gray")
plt.axvline(4, color="gray", linewidth=0.8)
plt.xlabel("threads")
plt.ylabel("efficiency")
plt.title("D1: efficiency")
plt.grid(True)
plt.savefig("results/d1_efficiency.png", dpi=150, bbox_inches="tight")

# graph 3: Karp-Flatt serial fraction
plt.figure(figsize=(6, 4.5))
ks = sorted(karp)
plt.plot(ks, [karp[T] for T in ks], marker="o")
plt.axvline(4, color="gray", linewidth=0.8)
plt.xlabel("threads")
plt.ylabel("Karp-Flatt serial fraction e(p)")
plt.title("D1: Karp-Flatt")
plt.grid(True)
plt.savefig("results/d1_karpflatt.png", dpi=150, bbox_inches="tight")

print("Saved graphs in the results folder")