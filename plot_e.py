# plot_e.py -- tables and graphs for Part E (only for the experiments that were run)
import csv
import os
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 500
seeds = range(1, 11)


def load_summary(exp):
    with open(f"results/e_{exp}.csv") as f:
        return list(csv.DictReader(f))


def by_setting(rows):
    groups = {}
    for r in rows:
        groups.setdefault(r["setting"], []).append(r)
    return groups


def column(rows, name):
    return [float(r[name]) for r in rows]


def mean_sd(values):
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    return statistics.mean(values), sd


def load_series(name):
    """All runs of one setting as fractions per day, padded to the same length."""
    runs = []
    for seed in seeds:
        with open(f"out/e/{name}_s{seed}.csv") as f:
            runs.append(list(csv.DictReader(f)))
    longest = max(len(r) for r in runs)
    data = {c: [] for c in "SIRD"}
    for r in runs:
        for c in "SIRD":
            values = [int(row[c]) / (N * N) for row in r]
            values += [values[-1]] * (longest - len(values))   # state stays constant after the end
            data[c].append(values)
    return data


# ---------------- E1: default parameters ----------------
if os.path.exists("results/e_default.csv"):
    data = load_series("default")
    days = range(len(data["S"][0]))
    plt.figure(figsize=(7, 4.5))
    for c, label in [("S", "susceptible"), ("I", "infected"), ("R", "recovered"), ("D", "dead")]:
        mean = [statistics.mean(col) for col in zip(*data[c])]
        low = [min(col) for col in zip(*data[c])]
        high = [max(col) for col in zip(*data[c])]
        plt.plot(days, mean, label=label)
        plt.fill_between(days, low, high, alpha=0.25)
    plt.xlabel("day")
    plt.ylabel("fraction of population")
    plt.title("E1: default parameters (mean and min-max of 10 seeds, N = 500)")
    plt.legend()
    plt.grid(True)
    plt.savefig("results/e1_default.png", dpi=150, bbox_inches="tight")

    rows = load_summary("default")
    print("E1 default parameters (mean +- sd over 10 seeds)")
    for field, label in [("peak_fraction", "peak infected fraction"), ("peak_day", "day of peak"),
                         ("attack_fraction", "total ever infected"), ("death_fraction", "deaths"),
                         ("days", "epidemic length (days)")]:
        m, s = mean_sd(column(rows, field))
        print(f"  {label:24s} {m:9.4f} +- {s:.4f}")
    print()

# ---------------- E2: vary beta ----------------
if os.path.exists("results/e_beta.csv"):
    groups = by_setting(load_summary("beta"))
    betas, attack_m, attack_s, major = [], [], [], []
    print("E2 vary beta     beta   attack fraction (mean +- sd)   runs with a large outbreak   mean length")
    for name, rows in groups.items():
        b = float(name[4:])
        attack = column(rows, "attack_fraction")
        m, s = mean_sd(attack)
        large = sum(1 for a in attack if a > 0.01) / len(attack)   # more than 1% of the population infected
        length = statistics.mean(column(rows, "days"))
        print(f"            {b:7.3f}   {m:8.4f} +- {s:.4f}              {100 * large:5.0f} %                  {length:7.0f}")
        betas.append(b)
        attack_m.append(m)
        attack_s.append(s)
        major.append(large)
    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.errorbar(betas, attack_m, yerr=attack_s, marker="o", capsize=3, label="total ever infected")
    ax1.set_xlabel("transmission probability beta")
    ax1.set_ylabel("fraction ever infected")
    ax1.grid(True)
    ax2 = ax1.twinx()
    ax2.plot(betas, major, "r--s", label="runs with a large outbreak")
    ax2.set_ylabel("fraction of runs with a large outbreak")
    ax1.set_title("E2: outbreak size against beta (10 seeds)")
    fig.legend(loc="center right", bbox_to_anchor=(0.88, 0.5))
    plt.savefig("results/e2_beta.png", dpi=150, bbox_inches="tight")
    print()

# ---------------- E3: vary vaccination ----------------
if os.path.exists("results/e_vacc.csv"):
    groups = by_setting(load_summary("vacc"))
    vs, attack_m, attack_s, major = [], [], [], []
    print("E3 vary v        v     attack fraction (mean +- sd)   runs with a large outbreak")
    for name, rows in groups.items():
        v = float(name[1:])
        attack = column(rows, "attack_fraction")
        m, s = mean_sd(attack)
        large = sum(1 for a in attack if a > 0.01) / len(attack)
        print(f"            {v:7.2f}   {m:8.4f} +- {s:.4f}              {100 * large:5.0f} %")
        vs.append(v)
        attack_m.append(m)
        attack_s.append(s)
        major.append(large)
    fig, ax1 = plt.subplots(figsize=(7, 4.5))
    ax1.errorbar(vs, attack_m, yerr=attack_s, marker="o", capsize=3)
    ax1.set_xlabel("vaccinated fraction v")
    ax1.set_ylabel("fraction ever infected")
    ax1.grid(True)
    ax2 = ax1.twinx()
    ax2.plot(vs, major, "r--s")
    ax2.set_ylabel("fraction of runs with a large outbreak", color="r")
    ax1.set_title("E3: outbreak size against vaccination (10 seeds)")
    plt.savefig("results/e3_vaccination.png", dpi=150, bbox_inches="tight")
    print()

# ---------------- E4: masks and lockdown ----------------
if os.path.exists("results/e_control.csv"):
    groups = by_setting(load_summary("control"))
    print("E4 masks and lockdown")
    print("  setting             peak fraction        day of peak        total infected")
    plt.figure(figsize=(7, 4.5))
    for name, rows in groups.items():
        pm, ps = mean_sd(column(rows, "peak_fraction"))
        dm, ds = mean_sd(column(rows, "peak_day"))
        am, a_s = mean_sd(column(rows, "attack_fraction"))
        print(f"  {name:18s}  {pm:6.3f} +- {ps:.3f}    {dm:7.1f} +- {ds:5.1f}    {am:6.3f} +- {a_s:.3f}")
        data = load_series(name)
        mean_i = [statistics.mean(col) for col in zip(*data["I"])]
        plt.plot(range(len(mean_i)), mean_i, label=name)
    plt.xlabel("day")
    plt.ylabel("infected fraction (mean of 10 seeds)")
    plt.title("E4: effect of masks and lockdown")
    plt.legend()
    plt.grid(True)
    plt.savefig("results/e4_control.png", dpi=150, bbox_inches="tight")
    print()

print("Saved graphs in the results folder")