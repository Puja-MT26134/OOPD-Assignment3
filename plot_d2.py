# plot_d2.py -- weak scaling efficiency and Gustafson's law
import csv
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

times = {}
with open("results/d2_raw.csv") as f:
    for row in csv.DictReader(f):
        times.setdefault(int(row["threads"]), []).append(float(row["seconds"]))

threads = sorted(times)
median = {T: statistics.median(times[T]) for T in threads}
base = median[1]

efficiency = {T: base / median[T] for T in threads}
scaled_speedup = {T: T * efficiency[T] for T in threads}

# Gustafson: S(p) = p - f(p-1)  ->  f = (p - S) / (p - 1), taken at p = 4
f_serial = (4 - scaled_speedup[4]) / 3


def gustafson(p):
    return p - f_serial * (p - 1)


print("T   median(s)  efficiency  scaled_speedup")
for T in threads:
    print(f"{T:2d}  {median[T]:9.3f}  {efficiency[T]:10.2f}  {scaled_speedup[T]:14.2f}")
print(f"Serial fraction used for Gustafson (from T=4): {f_serial:.3f}")

plt.figure(figsize=(6, 4.5))
plt.plot(threads, [efficiency[T] for T in threads], marker="o", label="measured")
plt.plot(threads, [gustafson(T) / T for T in threads], ":", label=f"Gustafson, f = {f_serial:.2f}")
plt.axhline(1.0, linestyle="--", color="gray", label="ideal")
plt.axvline(4, color="gray", linewidth=0.8)
plt.xlabel("threads (grid grows with T)")
plt.ylabel("weak-scaling efficiency  T1 / Tp")
plt.title("D2: weak scaling (1000 x 1000 cells per thread)")
plt.legend()
plt.grid(True)
plt.savefig("results/d2_efficiency.png", dpi=150, bbox_inches="tight")

plt.figure(figsize=(6, 4.5))
plt.plot(threads, [scaled_speedup[T] for T in threads], marker="o", label="measured")
plt.plot(threads, threads, "--", label="ideal")
plt.plot(threads, [gustafson(T) for T in threads], ":", label=f"Gustafson, f = {f_serial:.2f}")
plt.xlabel("threads")
plt.ylabel("scaled speedup")
plt.title("D2: scaled speedup")
plt.legend()
plt.grid(True)
plt.savefig("results/d2_speedup.png", dpi=150, bbox_inches="tight")
print("Saved graphs in the results folder")