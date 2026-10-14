# Memo: Tree Traversals Powering an Org-Chart API

To: lab reviewers. From: trees group. Subject: shipping a traversal
service that doubles as the structural foundation for later index labs.

What we ship. An org-chart API over a general tree (n-ary, parent
pointers): headcount rollups, chain-of-command paths, level listings,
and lowest-common-manager queries. A binary-tree module rides along for
expression trees and traversal drills.

Traversal inventory. Preorder for reporting lines, postorder for rollup
aggregation, level-order for org rendering, inorder reserved for the
binary side. Every traversal ships iterative and recursive forms with an
agreement test between them on 500 generated trees.

Depth policy. Iterative forms are the production path; recursion is the
oracle. A 100k-deep chain fixture proves the iterative walker survives
where call stacks give up, and the memo records the measured depth at
which the recursive form fails on the lab JVM.

Query semantics. Subtree size in O(subtree) via postorder memoization,
manager path in O(depth) via parent links, LCA via ancestor marking.
All three cross-checked against brute force on small orgs.

Change handling. Reorg operations (reparent subtree, insert report,
remove leaf) maintain parent/child counts; a structural audit walks the
tree verifying every child's parent pointer and every size field.

Second caller. Expression-tree evaluator over the binary module with
inorder/preorder/postorder print forms; evaluation must match direct
computation on 2k random expressions.

Evidence pack. Traversal agreement log, depth-survival note, audit
output on a 50k-node org, evaluator parity log. Weighting: traversal
correctness 12, reorg audit strength 10, depth and evaluator proof 8.
## Review prompts
- Walk one reparent by hand.
- Quote the chain depth survived.
- Name the recursion limit found.
