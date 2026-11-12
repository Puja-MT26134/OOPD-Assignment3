# plot_d3.py -- graphs and tables for D3
import csv
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rows = []
with open("results/d3_raw.csv") as f:
    for r in csv.DictReader(f):
        rows.append(r)


def times_for(**kw):
    values = []
    for r in rows:
        if all(r[k] == str(v) for k, v in kw.items()):
            values.append(float(r["seconds"]))
    return values


# ---- D3a: number of chunks ----
chunk_list = sorted({int(r["chunks"]) for r in rows if r["experiment"] == "chunks"})
med, lo, hi = [], [], []
for C in chunk_list:
    t = times_for(experiment="chunks", chunks=C)
    med.append(statistics.median(t))
    lo.append(med[-1] - min(t))
    hi.append(max(t) - med[-1])
best = chunk_list[med.index(min(med))]
print("D3a  chunks   median(s)")
for C, m in zip(chunk_list, med):
    print(f"     {C:5d}   {m:8.3f}")
print("Best number of chunks:", best)

plt.figure(figsize=(6, 4.5))
plt.errorbar(chunk_list, med, yerr=[lo, hi], marker="o", capsize=3)
plt.xscale("log", base=2)
plt.xlabel("number of chunks C (T = 4 threads)")
plt.ylabel("time (s)")
plt.title("D3a: effect of the number of chunks")
plt.grid(True)
plt.savefig("results/d3a_chunks.png", dpi=150, bbox_inches="tight")

# ---- D3b: ways of dividing the grid ----
schemes = ["strips", "blocks", "interleaved"]
cs = [4, 16, 64]
print()
print("D3b  scheme        " + "  ".join(f"C={C:<3d}" for C in cs))
plt.figure(figsize=(6, 4.5))
width = 0.25
for i, scheme in enumerate(schemes):
    values = [statistics.median(times_for(experiment="schemes", partition=scheme, chunks=C)) for C in cs]
    print(f"     {scheme:12s}  " + "  ".join(f"{v:6.3f}" for v in values))
    positions = [k + i * width for k in range(len(cs))]
    plt.bar(positions, values, width, label=scheme)
plt.xticks([k + width for k in range(len(cs))], [f"C={C}" for C in cs])
plt.ylabel("time (s)")
plt.title("D3b: ways of dividing the grid (T = 4)")
plt.legend()
plt.grid(True, axis="y")
plt.savefig("results/d3b_schemes.png", dpi=150, bbox_inches="tight")

# ---- D3c: small grids ----
sizes = sorted({int(r["N"]) for r in rows if r["experiment"] == "small"})
modes = ["sequential", "thread-per-day", "pool"]
small = {}
for mode in modes:
    small[mode] = {N: statistics.median(times_for(experiment="small", mode=mode, N=N)) for N in sizes}

print()
print("D3c      N   sequential   thread-per-day   pool")
for N in sizes:
    print(f"     {N:5d}   {small['sequential'][N]:9.4f}   {small['thread-per-day'][N]:13.4f}   {small['pool'][N]:8.4f}")
for mode in ["thread-per-day", "pool"]:
    better = [N for N in sizes if small[mode][N] < small["sequential"][N]]
    print(mode, "is first faster than sequential at N =", min(better) if better else "never")

plt.figure(figsize=(6, 4.5))
for mode in modes:
    plt.plot(sizes, [small[mode][N] for N in sizes], marker="o", label=mode)
plt.xscale("log")
plt.yscale("log")
plt.xlabel("grid size N")
plt.ylabel("time for 200 days (s)")
plt.title("D3c: small grids")
plt.legend()
plt.grid(True, which="both")
plt.savefig("results/d3c_small.png", dpi=150, bbox_inches="tight")
print("Saved graphs in the results folder")