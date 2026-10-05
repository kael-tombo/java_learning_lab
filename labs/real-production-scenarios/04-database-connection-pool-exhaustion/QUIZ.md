# QUIZ — Connection Pool Exhaustion (15Q)

1. Pool exhaustion latency signature? A) p99→timeout value cliff B) linear rise C) bimodal D) no change → **A**
2. `active≈max` + pending>0 means? A) DB down B) pool saturated C) network cut D) GC pause → **B**
3. Best leak finder? A) bigger pool B) `leakDetectionThreshold` stacks C) restart D) more replicas → **B**
4. `idle in transaction` in pg_stat_activity suggests? A) fast query B) conn held open, not working C) vacuum D) checkpoint → **B**
5. Fix for unclosed branch? A) finally/try-with-resources B) larger timeout C) more pods D) retry → **A**
6. 10 pods × 20 pool vs DB max 100 → ? A) fine B) 2× oversubscribed C) DB faster D) irrelevant → **B**
7. Safe per-pod max with 20% headroom? A) 20 B) 8 C) 50 D) 100 → **B**
8. Slow query pins pool — first fix? A) raise pool B) fix query/index C) restart DB D) disable metrics → **B**
9. Raising `connectionTimeout` alone does? A) adds capacity B) lengthens tail, hides problem C) fixes leak D) frees slots → **B**
10. Hikari `connectionTimeout` is? A) query limit B) max wait for pool slot C) socket timeout D) idle eviction → **B**
11. `maxLifetime` prevents? A) leaks B) stale/firewall-killed conns C) slow queries D) deadlocks → **B**
12. PgBouncer transaction mode helps when? A) many idle app conns B) single conn C) no DB D) CPU hog → **A**
13. Threads waiting for conn hold? A) nothing B) Tomcat worker threads C) disk D) GPU → **B**
14. First mitigation? A) schema change B) restart/drain + kill blocker C) rewrite app D) add index in prod blindly → **B**
15. Proof leak vs under-size? A) guess B) leak stacks + active growth on flat traffic C) CPU graph D) deploy color → **B**

Score: 13–15 expert, 10–12 ready, <10 redo THEORY + EXERCISES.
