# MINI_PROJECT — Online Algorithms
> Build a paging + rent-or-buy simulator that reports faults and competitive ratios on fixed traces.

## Inputs
- Request trace file: one integer page id per line, e.g. `0 1 2 3 0 1 4 0 1 2 3 4` (12 requests).
- Cache capacity `k` (default 3) and ski-rental pair (buy price, rent rate).

## Build steps
1. Implement LRU with an access-order map, FIFO with a queue, and offline OPT by Belady MIN (evict the page used farthest in the future).
2. On the 12-request reference trace with k=3, print per-algorithm fault counts and the ratio faults(LRU)/faults(OPT).
3. Implement the ski-rental rule: rent until cumulative rent reaches the buy price, then buy; print strategy cost vs OPT for trip lengths 4 and 14 at buy=100, rent=10.
4. Add a `--trace` flag reading arbitrary traces and a `--k` flag; emit one CSV row per run: `algo,k,faults,ratio`.
5. Write a short note explaining why no online paging algorithm beats k-competitiveness in general.

## Acceptance criteria
1. Reference trace reproduces faults(LRU)=10 and faults(OPT)=7 with k=3.
2. Ski-rental output shows strategy=200 vs OPT=100 (ratio 2.0) for the 14-day trip and 40 vs 40 for the 4-day trip.
3. FIFO, LRU, OPT all run from the same trace parser with no duplicated eviction logic per algorithm file.
4. CSV output has exactly the header `algo,k,faults,ratio` and one row per algorithm.
5. The note states the k lower bound for deterministic paging in one paragraph without hand-waving.
6. `java` run completes on a 100k-request generated trace within the machine's memory (streaming read, no full-trace buffering beyond OPT's needs).

## Analysis prompts
1. Which request pattern maximizes the LRU/OPT gap on your tests, and why?
2. At what trip length does rent-then-buy switch from renting to buying, as a formula of buy/rent?
3. What breaks in OPT when the full trace is not known ahead (streaming setting)?

## Non-goals
- Randomized paging (marking) and the k-server problem; adversarial-trace generation beyond one example.

## Worked reference (verified outputs)
- Ski-rental at buy=100, rent=10: 14-day trip prints strategy=200 opt=100 ratio=2.0; 4-day trip prints cost=40.
- LRU capacity 2 on put(1),put(2),get(1),put(3): prints get1=10 get2=-1 get3=30 with keys=[1, 3].

## Stretch
- Add the marking algorithm and compare its faults against LRU on the same traces.
- Generate one adversarial trace per algorithm that attains at least 80 percent of the k bound.
