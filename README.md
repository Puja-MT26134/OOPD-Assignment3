# OOPD Assignment 3

## Parallel and Asynchronous Pandemic Simulation

A grid pandemic simulation (S, I, R, V, D) in C++17 with a thread-per-day version,
a thread pool, asynchronous snapshot writing and a parameter sweep.
Python 3 is used only for test, experiment and plotting scripts.
Data files, graphs and the report are not stored in this repository;
they are submitted on Google Classroom.

## Requirements
- g++ with C++17 and POSIX threads (tested with g++ 16.2.0, MinGW-W64, Windows 11)
- Python 3 with matplotlib and numpy (only for the scripts)

## Branches
- main: all parts
- part-b: Parts A and B (sequential version, thread per day, thread pool,
  three ways of dividing the grid, test script run_tests.py)
- part-c: Part C (snapshots, shared header sim_core.h, parameter sweep sweep.cpp)
- part-d: Part D (performance experiment scripts run_d1..run_d5.py, plot_d1..plot_d5.py)
- part-e: Part E (epidemiology scripts run_e.py, plot_e.py, plot_e5.py)

## Build
    g++ -std=c++17 -O2 -pthread sim.cpp -o sim.exe
    g++ -std=c++17 -O2 -pthread sweep.cpp -o sweep.exe

## Run
    sim.exe --N 1000 --days 200 --mode pool --threads 4 --chunks 16 --partition strips --out out.csv
    sim.exe --N 500 --days 100 --snapshot-every 10 --snapshot-mode async --max-pending 4 --io-latency 100
    sweep.exe --N 100 --days 300 --seeds 3 --workers 4 --out sweep_results.csv

The CSV file has one line per day: day,S,I,R,V,D,beta_eff,checksum (days start at 0).

Options of sim.exe:
--N --days --seed --beta --d --mu --I0 --v --mask --lambda --theta-on --theta-off
--lockdown 0/1 --fixed-days 0/1 --mode sequential|thread-per-day|pool --threads --chunks
--partition strips|blocks|interleaved --snapshot-every --snapshot-mode blocking|async
--max-pending --io-latency --snapshot-dir --out

Options of sweep.exe:
--N --days --seeds --workers (runs at once) --threads (threads per run)
--max-runs --time-limit (seconds) --out

## Code overview
sim_core.h (shared by sim.cpp and sweep.cpp)
- Params, parseArgs: all settings from the command line
- State, Cell: one person (state and days infected). The grid is a flat vector,
  cell id = i*N + j
- mix, rand01: every random number is a hash of (seed, day, cell, stream),
  so the results do not depend on the number of threads
- initGrid: vaccination first, then the initial infections
- Chunk, makeChunks: divide the grid into strips, square blocks or interleaved rows
- updateChunk: one day for one chunk. It reads cur, writes only its own cells of next,
  and returns the counts and a checksum
- ThreadPool: workers created once, tasks submitted, results returned through futures
  (a mutex and condition variable are used only inside the task queue)
- simulateDay: runs the chunks one after another, with one thread per chunk, or with the
  pool, then swaps the two grids
- nextBeta: masks and lockdown
- writePPM: image snapshot. With --snapshot-mode async the grid is copied and written
  with std::async, with at most Q writes pending
- runSimulation, Summary: one whole run returning peak, peak day and totals
  (used by sweep.cpp)

sim.cpp: the main loop, snapshots and CSV output.
sweep.cpp: many runs as asynchronous tasks, progress output, results CSV, time limit.

## Scripts (run them from the folder that contains sim.exe and sweep.exe)
- run_tests.py: checks that every parallel run gives the same CSV as the sequential
  run (expected last line: Passed: 63   Failed: 0)
- run_d1.py .. run_d5.py: performance experiments D1 to D5 (the word quick gives a fast
  trial run). They write raw timings to results/ (not committed)
- plot_d1.py .. plot_d5.py: tables and graphs for D1 to D5 (run after the matching run_d script)
- run_e.py (default, beta, vacc, control or all): epidemiology simulations for E1 to E4
- plot_e.py: tables and graphs for E1 to E4; plot_e5.py: SIR equations against the grid (E5)