# Advanced NLP - Real-World Project: Support-ticket triage spec
## Brief
help-desk tickets with subject, body, product tag, priority label. Success means a reviewer can rerun the 11-nlp-advanced flow from raw files to final tables without asking for missing steps.
## Components (tokenization/normalization, TF-IDF retrieval, LDA topics, embedding similarity checks)
Core chain runs tokenizer and IDF vocabulary frozen on train; topics labeled by top terms plus exemplars.
Method set in play: tokenization/normalization, TF-IDF retrieval, LDA topics, embedding similarity checks.
## Work plan
1. Normalize text with documented lowercasing, punctuation, stop-word rules.
2. Freeze TF-IDF vocabulary on train and report out-of-vocabulary rate on holdout.
3. Fit LDA across 5, 10, 15 topics comparing coherence scores.
4. Label chosen topics with top terms plus three exemplar tickets each.
5. Score embedding-similarity retrieval with precision at 5 on tagged pairs.
6. Route low-confidence tickets to manual review with threshold rationale.
## Done when
- normalization rules listed verbatim in config for the 11-nlp-advanced dossier.
- OOV rate reported on holdout with counts checked against 11-nlp-advanced logs.
- coherence comparison covers 5/10/15 topics reproduced on rerun of 11-nlp-advanced steps.
- topic labels each cite terms plus exemplars stored with the 11-nlp-advanced artifact set.
- precision-at-5 reported with pair counts signed off inside the 11-nlp-advanced review note.
## Limits of Support-ticket triage spec
Textbook methods only; streaming, serving, and cost tuning belong outside this 11-nlp-advanced brief.
## Evidence pack carried with 11-nlp-advanced
- Raw help-desk tickets with subject, body, product tag, priority label snapshot pointer plus exact row counts.
- Dated run log linking each 11-nlp-advanced build decision to its output table.
- Before/after comparison table kept beside the Support-ticket triage spec tables.
- Rejected-rows file with rule codes for the 11-nlp-advanced audit trail.
- One-page Advanced NLP glossary defining every column the Support-ticket triage spec emits.
## Reviewer walkthrough for Support-ticket triage spec
- Reviewer opens 11-nlp-advanced inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to help-desk tickets with subject, body, product tag, priority label.
- Reviewer confirms normalization rules listed verbatim in config without extra explanation.
- Reviewer closes the Advanced NLP session with two written follow-ups.
