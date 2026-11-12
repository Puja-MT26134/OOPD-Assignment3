# plot_d5.py -- tables and graphs for D5
import csv
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 1000   # must match run_d5.py

with open("results/d5_raw.csv") as f:
    rows = list(csv.DictReader(f))


def select(experiment, mode, latency, K, Q):
    return [r for r in rows
            if r["experiment"] == experiment and r["mode"] == mode
            and int(r["latency"]) == latency and int(r["K"]) == K and int(r["Q"]) == Q]


def median_time(experiment, mode, latency, K, Q):
    return statistics.median([float(r["seconds"]) for r in select(experiment, mode, latency, K, Q)])


base = median_time("main", "none", 0, 0, 0)
main_rows = [r for r in rows if r["experiment"] == "main" and r["mode"] != "none"]
latencies = sorted({int(r["latency"]) for r in main_rows})
ks = sorted({int(r["K"]) for r in main_rows}, reverse=True)
q_main = max(int(r["Q"]) for r in main_rows)

print(f"No snapshots: {base:.3f} s")
print()
print("latency   K   blocking   async(Q=%d)   write time hidden" % q_main)
fig, axes = plt.subplots(1, len(latencies), figsize=(5 * len(latencies), 4), sharey=True)
for ax, L in zip(axes, latencies):
    blocking, asyn = [], []
    for K in ks:
        b = median_time("main", "blocking", L, K, 0)
        a = median_time("main", "async", L, K, q_main)
        blocking.append(b)
        asyn.append(a)
        extra = b - base
        if extra > 0.05:
            hidden = f"{100 * (b - a) / extra:6.0f} %"
        else:
            hidden = "   (writing cost too small)"
        print(f"{L:5d} ms {K:3d}   {b:8.3f}   {a:9.3f}      {hidden}")
    ax.plot(ks, blocking, marker="o", label="blocking")
    ax.plot(ks, asyn, marker="s", label=f"async (Q={q_main})")
    ax.axhline(base, linestyle="--", color="gray", label="no snapshots")
    ax.set_xscale("log")
    ax.invert_xaxis()     # more frequent snapshots to the right
    ax.set_xlabel("K (snapshot every K days)")
    ax.set_title(f"io-latency = {L} ms")
    ax.grid(True)
axes[0].set_ylabel("total time (s)")
axes[0].legend()
plt.savefig("results/d5_main.png", dpi=150, bbox_inches="tight")

# ---- effect of Q ----
q_rows = [r for r in rows if r["experiment"] == "q"]
qL = int(q_rows[0]["latency"])
qK = int(q_rows[0]["K"])
q_values = sorted({int(r["Q"]) for r in q_rows})
blocking_ref = median_time("main", "blocking", qL, qK, 0)

print()
print(f"Effect of Q (io-latency {qL} ms, K = {qK}); blocking = {blocking_ref:.3f} s, none = {base:.3f} s")
print("  Q   median(s)   max pending   extra memory (MB)")
times = []
for Q in q_values:
    sel = select("q", "async", qL, qK, Q)
    t = statistics.median([float(r["seconds"]) for r in sel])
    mp = max(int(r["maxpending"]) for r in sel)
    times.append(t)
    print(f"{Q:3d}   {t:8.3f}   {mp:10d}   {mp * N * N * 8 / 1e6:12.0f}")

plt.figure(figsize=(6, 4.5))
plt.plot(q_values, times, marker="o", label="async")
plt.axhline(blocking_ref, linestyle=":", color="red", label="blocking")
plt.axhline(base, linestyle="--", color="gray", label="no snapshots")
plt.xscale("log", base=2)
plt.xlabel("Q (most writes pending)")
plt.ylabel("total time (s)")
plt.title(f"D5: effect of Q (latency {qL} ms, K = {qK})")
plt.legend()
plt.grid(True)
plt.savefig("results/d5_q.png", dpi=150, bbox_inches="tight")
print("Saved graphs in the results folder")