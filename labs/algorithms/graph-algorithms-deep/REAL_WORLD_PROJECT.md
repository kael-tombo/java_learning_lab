# REAL_WORLD_PROJECT — Graph Algorithms Deep Track
> Metro-network resilience service: SCC-based dependency map, bridge/critical-segment alerts, LCA-routed hierarchies, and max-flow evacuation capacity.

## System and inputs
- Network snapshot: stations as vertices, links with capacity and travel time; nightly import versioned by snapshot id.
- Dependency edges between signaling subsystems for SCC analysis; hierarchy tree for LCA-routed maintenance dispatch.
- Evacuation queries: (source set, safe set) pairs evaluated for max-flow capacity.

## Design
- SCC pass flags cyclic dependencies between subsystems; each cycle ships with the member list for the review board.
- Bridge/articulation pass marks critical segments; inspection tickets auto-file per critical element per snapshot.
- LCA on the maintenance hierarchy routes each ticket to the nearest responsible crew node.
- Edmonds-Karp (bounded by snapshot size guard; larger snapshots use a documented Dinic upgrade path, labeled) answers evacuation capacity.

## Metrics
- Critical-segment count and inspection-ticket closure rate per snapshot.
- SCC cycle count with review-board disposition (accepted/refactored).
- Evacuation-capacity headroom per queried pair vs required minimum.
- Import-to-dashboard latency with snapshot-version tracking.

## Failure modes
- Snapshot with negative travel times (data error): validation quarantines the snapshot; previous version keeps serving.
- Flow network too large for Edmonds-Karp: size guard diverts to the labeled upgrade path with a logged event.
- Hierarchy change breaking LCA table: versioned hierarchy with rebuild gate; queries carry the hierarchy version.
- Stale critical-segment tickets after topology fix: ticket reconciler closes tickets whose elements left the critical set.

## Rollout
1. Import 30 days of archived snapshots; compare critical segments vs recorded incidents.
2. Advisory mode: tickets filed but non-blocking for one quarter.
3. Blocking mode with the reconciler and versioned snapshots mandatory.

## Acceptance criteria
1. Reference 6-node graph through the service path reproduces hand-verified distances, SCCs, and flow value.
2. Corrupt-snapshot test keeps the previous version serving with an alert.
3. Size-guard test diverts an oversized flow query to the labeled path.
4. Reconciler test closes tickets for fixed topology with audit entries.
5. Rollback restores the previous snapshot and hierarchy versions together.

## Cost and contract notes
- Inspection tickets priced per critical element per snapshot; closure rate reported against crew capacity.
- Evacuation-capacity shortfalls trigger capital-review entries with the required-vs-available numbers attached.
- Snapshot storage (30 days versioned) costed in the platform budget; queries always declare versions.
- Contract: capacity answers embed snapshot id, hierarchy version, and method path (EK vs upgraded).
