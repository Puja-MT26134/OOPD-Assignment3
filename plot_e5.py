# plot_e5.py -- E5: standard SIR equations compared with the grid simulation
import csv
import statistics
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 500
seeds = range(1, 11)

# parameters of the default run
beta = 0.08
neighbours = 8
d = 7
mu = 0.01
I0 = 10
v = 0.0

contact = neighbours * beta     # new infections per infected person per day (everybody can meet everybody)
gamma = 1.0 / d                 # recovery rate
R0 = contact / gamma


def derivatives(state):
    S, I, R, D = state
    new_infections = contact * S * I
    leaving = gamma * I
    return [-new_infections,
            new_infections - leaving,
            (1 - mu) * leaving,
            mu * leaving]


def rk4_step(state, h):
    k1 = derivatives(state)
    k2 = derivatives([s + h / 2 * k for s, k in zip(state, k1)])
    k3 = derivatives([s + h / 2 * k for s, k in zip(state, k2)])
    k4 = derivatives([s + h * k for s, k in zip(state, k3)])
    return [s + h / 6 * (a + 2 * b + 2 * c + e)
            for s, a, b, c, e in zip(state, k1, k2, k3, k4)]


def solve_sir(days):
    state = [1 - v - I0 / (N * N), I0 / (N * N), 0.0, 0.0]
    series = [state]
    for day in range(days):
        for k in range(20):                 # 20 small steps of 0.05 day
            state = rk4_step(state, 0.05)
        series.append(state)
    return series


# ---- grid results: mean of 10 seeds ----
runs = []
for seed in seeds:
    with open(f"out/e/default_s{seed}.csv") as f:
        runs.append(list(csv.DictReader(f)))
length = max(len(r) for r in runs)
grid = {c: [] for c in "SIRD"}
for c in "SIRD":
    for day in range(length):
        values = []
        for r in runs:
            row = r[min(day, len(r) - 1)]       # after the end the state stays constant
            values.append(int(row[c]) / (N * N))
        grid[c].append(statistics.mean(values))

sir = solve_sir(length - 1)
sir_series = {c: [s[i] for s in sir] for i, c in enumerate("SIRD")}

# ---- graphs ----
colors = {"S": "tab:green", "I": "tab:red", "R": "tab:blue", "D": "black"}
names = {"S": "susceptible", "I": "infected", "R": "recovered", "D": "dead"}

plt.figure(figsize=(8, 4.5))
plt.plot(grid["I"], color="tab:red", label="grid (mean of 10 seeds)")
plt.plot(sir_series["I"], "--", color="tab:red", label="SIR equations")
plt.xlabel("day")
plt.ylabel("infected fraction")
plt.title("E5: infected people over time, grid vs SIR")
plt.legend()
plt.grid(True)
plt.savefig("results/e5_infected.png", dpi=150, bbox_inches="tight")

plt.figure(figsize=(8, 4.5))
for c in "SRD":
    plt.plot(grid[c], color=colors[c], label=f"{names[c]} (grid)")
    plt.plot(sir_series[c], "--", color=colors[c], label=f"{names[c]} (SIR)")
plt.xlabel("day")
plt.ylabel("fraction of population")
plt.title("E5: S, R and D over time, grid vs SIR")
plt.legend(ncol=2, fontsize=8)
plt.grid(True)
plt.savefig("results/e5_compartments.png", dpi=150, bbox_inches="tight")

# ---- comparison table ----
with open("results/e_default.csv") as f:
    summary = list(csv.DictReader(f))


def mean_of(name):
    return statistics.mean(float(r[name]) for r in summary)


sir_peak = max(sir_series["I"])
sir_peak_day = sir_series["I"].index(sir_peak)
sir_ever = sir_series["I"][-1] + sir_series["R"][-1] + sir_series["D"][-1]

print(f"R0 = 8 * beta / gamma = {R0:.2f}")
print()
print("                          SIR equations     grid (mean of 10 seeds)")
print(f"peak infected fraction     {sir_peak:10.3f}        {mean_of('peak_fraction'):10.3f}")
print(f"day of the peak            {sir_peak_day:10d}        {mean_of('peak_day'):10.0f}")
print(f"ever infected              {sir_ever:10.3f}        {mean_of('attack_fraction'):10.3f}")
print(f"deaths                     {sir_series['D'][-1]:10.3f}        {mean_of('death_fraction'):10.3f}")
print()
print(f"threshold beta for an outbreak:   SIR {gamma / neighbours:.3f}   grid about 0.035 to 0.04 (from E2)")
print(f"vaccination for herd immunity:    SIR {1 - 1 / R0:.2f}    grid about 0.40 (from E3)")
print("Saved graphs in the results folder")