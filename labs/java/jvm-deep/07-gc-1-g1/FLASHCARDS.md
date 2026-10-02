# FLASHCARDS — G1 GC

| # | Front | Back |
|---|-------|------|
| 1 | G1 primary goal? | Low, predictable pauses for large heaps; regional collection. |
| 2 | Heap division? | Equal regions (1-32MB); young/old distributed. |
| 3 | Region states? | Free, Humongous, Eden, Survivor, Old. |
| 4 | Humongous object? | >50% region size; contiguous regions; never in young gen. |
| 5 | Predictable pauses? | Mixed GC (subset of regions); pause target (default 200ms). |
| 6 | Mixed GC? | Young + selected old regions; incremental old gen reclamation. |
| 6 | RSet (Remembered Set)? | Per-region incoming refs index; enables young GC without full scan. |
| 7 | Humongous object? | >50% region size; contiguous regions; never in young gen. |
| 7 | Mixed GC trigger? | Old gen > InitiatingHeapOccupancyPercent (default 45%). |
| 7 | SATB? | Snapshot-At-The-Beginning write barrier; preserves liveness snapshot. |
| 7 | Mixed GC trigger? | Old gen > InitiatingHeapOccupancyPercent (default 45%). |
| 7 | SATB? | Snapshot-At-The-Beginning write barrier; preserves liveness snapshot. |
| 7 | Young GC trigger? | Eden full; young regions selected. |
| 7 | Young GC trigger? | Eden full; young regions selected. |
| 6 | Default pause target? | 200ms (-XX:MaxGCPauseMillis). |
| 6 | Default pause target? | 200ms (-XX:MaxGCPauseMillis). |
| 7 | RSet? | Per-region incoming refs index; avoids full heap scan on young GC. |
| 7 | RSet (Remembered Set)? | Per-region incoming refs index; enables young GC without full scan. |
| 7 | Humongous object? | >50% region size; contiguous regions; never in young gen. |
| 7 | Mixed GC trigger? | Old gen > InitiatingHeapOccupancyPercent (default 45%). |
| 7 | SATB? | Snapshot-At-The-Beginning write barrier; preserves liveness snapshot. |
| 7 | Mixed GC trigger? | Old gen > InitiatingHeapOccupancyPercent (default 45%). |
| 7 | SATB? | Snapshot-At-The-Beginning write barrier; preserves liveness snapshot. |
| 7 | Young GC trigger? | Eden full; young regions selected. |
| 7 | Young GC trigger? | Eden full; young regions selected. |
| 6 | Default pause target? | 200ms (-XX:MaxGCPauseMillis). |
| 6 | Default pause target? | 200ms (-XX:MaxGCPauseMillis). |