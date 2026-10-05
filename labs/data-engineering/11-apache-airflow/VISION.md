# VISION — Apache Airflow: Authoring DAGs That Survive Real Data
> Where this lab takes you: from "my DAG works on my machine" to operators,
  deferrable sensors, dynamic task mapping, and DAGs that are safe to retry.

## The Arc
1. **Authoring** — DAG structure, operators, templating, variables.
2. **Data** — XCom limits, object storage for large payloads, task SDK.
3. **Patterns** — dynamic task mapping, task groups, datasets, triggers.
4. **Reliability** — deferrable sensors, retries, pools, SLA misses.
5. **Operate** — scheduler lag, DAG processing, testing, CI for DAGs.

## Milestones (checkable)
- [ ] M1: write a DAG with 8 tasks, correct dependencies, and a bounded retry policy.
- [ ] M2: pass a large intermediate value between tasks without XCom size limits.
- [ ] M3: use dynamic task mapping to fan out over a runtime-discovered list.
- [ ] M4: convert a blocking sensor to a deferrable one and measure scheduler impact.
- [ ] M5: write a DAG unit test that fails on a bad dependency, not just on a bug.

## Anti-Goals
- Logic inside `bash_command` that should be a PythonOperator.
- Passing 200MB through XCom.
- Sensors without timeouts that pin scheduler slots.

## Interview Lens
- "Your DAG has 60 tasks. Why is scheduling delayed by 4 minutes?"
- "How do you pass a list discovered at runtime to parallel tasks?"
- "Explain deferrable sensors and when they are worth it."

## 30-Day Plan
- Wk1 THEORY + EXERCISES L1-L7. Wk2 MINI_PROJECT DAG.
- Wk3 add deferrable sensors + dynamic mapping. Wk4 REAL_WORLD_PROJECT.

## Done = You Can
- Author, test, and operate production DAGs without surprising your platform team.
