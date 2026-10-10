# Reflection: ConcurrentLinkedQueue

## What surprised you?

Most learners expect pointers to be precise. CLQ's head and tail are
*allowed* to be wrong — and throughput improves because of it. Write down
which correctness facts survive stale pointers, and why that felt
uncomfortable.

## Check your model

1. Two threads offer concurrently at tail P. Narrate both CAS attempts,
   the loser's exact next steps, and the final chain. Where did anyone
   block? (Nowhere — say what replaced blocking.)
2. A walker sees `p == q`. What happened to node P, who did it, and what
   are the walker's next three actions?
3. Why can't `size()` be fixed to be accurate? What would "fixing" it cost
   (think: what synchronization would exact counting need)?

## Connect

- Which queue in your systems needs blocking (`take`) vs never-blocking
  (CLQ)? What breaks if you swap them?
- Where do you branch on `isEmpty()`/`size()` across threads today? What
  is the null-checked-poll rewrite?

## The one-line takeaway

Two CASes define the queue; everything else is tolerated staleness in the
service of never blocking. If your summary names both CASes and the
slack-2 rule, it is complete.
