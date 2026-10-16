# Advanced Clustering - Real-World Project: Customer micro-segmentation
## Problem
recency, frequency, monetary features standardized with a noisy outlier tail. Success means a reviewer can rerun the 10-clustering-advanced flow from raw files to final tables without asking for missing steps.
## Architecture (k-means selection, hierarchical dendrogram, DBSCAN tuning, silhouette and stability)
Core chain runs k chosen by elbow plus silhouette plus split-stability, never a single index.
Method set in play: k-means selection, hierarchical dendrogram, DBSCAN tuning, silhouette and stability.
## Build sequence
1. Standardize RFM with median/IQR and clip documented outlier bounds.
2. Sweep k from 2 to 10 recording inertia and silhouette per k.
3. Cut a hierarchical dendrogram with Ward linkage for k-cross-check.
4. Tune DBSCAN eps via k-distance elbow and report noise share.
5. Test split-stability by clustering halves and comparing assignments.
6. Profile final segments with medians, sizes, and plain-language labels.
## Acceptance checks
- k sweep table holds inertia plus silhouette for 2..10 for the 10-clustering-advanced dossier.
- dendrogram cut height stated with linkage named checked against 10-clustering-advanced logs.
- DBSCAN noise share reported with eps value reproduced on rerun of 10-clustering-advanced steps.
- split-stability agreement score shown with method stored with the 10-clustering-advanced artifact set.
- segment profiles include medians and n per segment signed off inside the 10-clustering-advanced review note.
## Limits of Customer micro-segmentation
Textbook methods only; streaming, serving, and cost tuning belong outside this 10-clustering-advanced brief.
## Evidence pack carried with 10-clustering-advanced
- Raw recency, frequency, monetary features standardized with a noisy outlier tail snapshot pointer plus exact row counts.
- Dated run log linking each 10-clustering-advanced build decision to its output table.
- Before/after comparison table kept beside the Customer micro-segmentation tables.
- Rejected-rows file with rule codes for the 10-clustering-advanced audit trail.
- One-page Advanced Clustering glossary defining every column the Customer micro-segmentation emits.
## Reviewer walkthrough for Customer micro-segmentation
- Reviewer opens 10-clustering-advanced inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to recency, frequency, monetary features standardized with a noisy outlier tail.
- Reviewer confirms k sweep table holds inertia plus silhouette for 2..10 without extra explanation.
- Reviewer closes the Advanced Clustering session with two written follow-ups.
