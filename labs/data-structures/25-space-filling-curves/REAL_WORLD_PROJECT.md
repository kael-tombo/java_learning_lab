# Tile-Server Index on Z-Order and Hilbert Curves

Map room. A tile server renders map tiles from 2M geo points; range
queries over tiles must hit contiguous key spans so an LSM store scans
sequentially. Z-order (Morton) and Hilbert encodings turn 2-D locality
into 1-D order - the lab measures which curve keeps neighbors together.

Encoding bench. Morton interleave vs Hilbert index for 1M points: build
time, bytes per key, and neighbor-preservation score (fraction of
8-neighbor pairs within a key window of 64). Hilbert should cluster
better; the report shows by how much on uniform vs clustered data.

Tile caller. Bounding-box tile fetch translated to curve-interval scans
with edge refinement (false positives from curve jumps filtered by exact
box test). Recall must equal brute force on 2k tiles; the win metric is
disk seeks avoided, counted from the interval plan.

LSM caller. Geo-key layout benchmark: point inserts in curve order vs
random order into an SSTable-like sorted run; compaction read-amp and
scan speed compared. Curve order should compact and scan friendlier -
measured, with the margin quoted.

Precision file. Bit-depth choice (16 vs 21 vs 31 per axis) with error
bounds stated; points near the antimeridian and poles handled by
documented rule; curve-jump false positives counted per tile query.

Ship. Encoders, tile service, layout bench, preservation scores, edge
rule note. Bar: encoding correctness vs brute force 12, locality scores
with data 10, precision plus jump handling 8.
## Curve scoreboard
- Preservation score per dataset.
- Bit depth 21 default.
- Jump false-positive rate posted.
- Antimeridian rule tested.
- Layout margins updated.
Publish the preservation winner with margins.

