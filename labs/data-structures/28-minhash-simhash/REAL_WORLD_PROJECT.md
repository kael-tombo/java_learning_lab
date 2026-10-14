# Near-Duplicate Suppression on MinHash and SimHash

Intake problem. A crawl pipe ingests 1M pages where 8 percent are
near-duplicates, and support tickets repeat with paraphrase. MinHash
estimates Jaccard similarity for candidate generation; SimHash flags
near-dupes by small Hamming distance. Kept topics: both callers, with
candidate-pair generation for the recommender as the second stage.

MinHash lane. 128 permutations over shingle sets (5-grams); signature
similarity must track exact Jaccard within tolerance on 2k labeled
pairs. LSH banding (b bands, r rows) turns signatures into candidate
pairs; recall vs exact pairs quoted at two threshold settings.

SimHash lane. 64-bit token-weighted fingerprints; Hamming distance <= 3
means duplicate. Precision/recall on 5k labeled ticket pairs with the
threshold justified by the curve, not by default.

Recommender caller. Candidate pairs feed a similarity shortlist; the
metric is pairs reduction (comparisons avoided vs all-pairs) at held
recall above 95 percent on the labeled set.

Threshold study. Similarity thresholds 0.5/0.7/0.9 each with measured
precision, recall, and candidate counts - the report names the operating
point per caller and the cost of moving it.

Drift cases. Empty documents, single-shingle pages, language-mixed
tickets (shingling policy stated), fingerprint bit-flip robustness
(1-bit change keeps distance small, verified).

Deliver. Both lanes, LSH index, threshold study, reduction numbers,
drift log. Marks: estimate agreement 12, operating-point evidence 10,
candidate math plus drift 8.
## Operating points
- Crawl threshold 0.7 default.
- Tickets distance 3 default.
- Recall floor 95 percent.
- Threshold study rerun quarterly.
- Drift cases in CI.
