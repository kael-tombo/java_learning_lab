# RFC: ArrayStack Service for Undo, Evaluation, and DFS

Status: proposed. Scope: one module, no frameworks, CLI plus optional
loopback HTTP. This note specifies behavior precisely enough that two
implementations could interoperate on the snapshot format.

Background. The lab needs a LIFO core shared by three callers: an editor
undo stack, a bracket/expression evaluator, and an explicit DFS frontier
for graph search. One ArrayStack backs all three behind a narrow push /
peek / pop / depth interface with a fixed ceiling.

Requests and replies. The CLI accepts push, pop, peek, depth, clear, and
save/load verbs; the evaluator accepts a single expression string and
returns either a value or the position of the first mismatch. DFS accepts
an adjacency file plus a start node and streams visit order to stdout.

Capacity policy. The stack is bounded (default 64k frames). Push past the
ceiling rejects with a diagnostic naming the caller and current depth;
the evaluator maps that to a depth-exceeded error at the offending token.

Correctness contract. Pop on empty, peek on empty, and unbalanced input
are specified errors with stable messages. Evaluator results must match
a recursive reference on 5k generated expressions. DFS preorder must
match the recursive oracle on 200 generated graphs.

Durability. Save writes depth plus frames oldest-first as CSV; load
rejects truncated files and restores exact depth. Undo history persists
only when the caller opts in, so crash recovery never resurrects stale
edits by surprise.

Observability. Each run appends op, depth-after, and nanos to a local
CSV. The report quotes push/pop cost, max depth seen, evaluator mismatch
rate (target zero), and DFS divergence count (target zero).

Rejected alternatives. Unbounded growth was rejected because undo memory
then tracks session length. Linked nodes were rejected for the evaluator
hot loop after measuring pointer-chase cost against the array version.

Acceptance. Cold-start demo runs undo, one evaluation, and one DFS from
flags alone. Oracle logs attached. Chaos script covers empty pop, full
push, truncated snapshot, and adversarial nesting (10k deep brackets).

Judgment. Contract coverage across the three callers: 12. Oracle parity
plus snapshot round-trip: 10. Depth policy and chaos behavior: 8.
