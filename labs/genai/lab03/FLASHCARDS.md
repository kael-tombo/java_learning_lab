# Lab 03: Prompt Engineering Patterns — Flashcards

| # | Front | Back |
|---|-------|------|
| 1 | Prompt | A program in a probabilistic language: task + constraints + context + stop |
| 2 | Four levers | Role framing, format spec, context injection, decoding controls |
| 3 | Role framing effect | Shifts the conditional toward role-conditioned continuations |
| 4 | Format spec beats adjectives | Schemas reduce variance; "be thorough" does not |
| 5 | Zero-shot | Instruction only, no examples |
| 6 | Few-shot | k demonstrations in-context; no weight updates |
| 7 | Good k | 3-8; past that, diminishing returns and rising cost |
| 8 | Boundary examples | Demos that straddle the decision boundary teach the decision |
| 9 | Position bias | Output changes with example order; randomize + average when evaluating |
| 10 | CoT | State intermediate reasoning before the final answer |
| 11 | Zero-shot CoT trigger | "Let's think step by step" |
| 12 | Self-consistency | Sample k CoT paths, majority vote on the final answer |
| 13 | Self-consistency cost | Multiplies spend by k |
| 14 | Tree-of-thought | Branch, evaluate, backtrack; better on search-like problems |
| 15 | Decomposed prompting | Planner -> independent solvers -> combiner |
| 16 | DecomP stages exchange | Typed records, not free text |
| 17 | Least-to-most | Order subproblems easy-to-hard so each conditions on the last |
| 18 | Chain-of-verification | Separate pass checks each claim against evidence |
| 19 | Structured output | Schema-constrained generation, not a request for JSON |
| 20 | Parser rule | Parse, validate, bound sizes; never eval |
| 21 | Repair loop | Bounded retries with a repair prompt, then deterministic fallback |
| 22 | Fallback extractor | Regex for ids, keyword buckets for intent |
| 23 | Stop sequences | Truncate output at matched text; define them for every call |
| 24 | max_tokens | Decoding control; caps runaway length |
| 25 | APE | Model proposes prompt variants; validation score selects the winner |
| 26 | APE requirement | A held-out validation set and a stopping rule |
| 27 | Prompt as code | Template + registry + version + hash, reviewed like source |
| 28 | Section order | System role, instructions, context, input, output schema |
| 29 | assertNoUnfilled | Catches `{{var}}` leaking to the model as literal text |
| 30 | Injection surface | Every interpolated value is untrusted |
| 31 | Delimiter rule | Mark untrusted blocks and label them data, not orders |
| 32 | Policy placement | Policy in system message; variables in user message |
| 33 | Output validation | Last line of defense after every LLM call |
| 34 | Prefix caching | Engine caches by prefix hash; stable text must come first |
| 35 | Why prefix first | Cached prefix tokens cost far less on repeat calls |
| 36 | Volatile content | Timestamps, user ids, retrieved chunks -> tail |
| 37 | ChatMessage record | `role` + `content` with role validation |
| 38 | PromptBuilder | Fluent section API enforcing order |
| 39 | PromptRegistry | Version -> template, `promote`, `rollback` |
| 40 | Render cache key | sha256(name + version + rendered) |
| 41 | Few-shot cost | Examples are re-billed on every call unless prefix-cached |
| 42 | Temperature 0 | Greedy; deterministic but can loop |
| 43 | Repetition penalty | Discourages verbatim loops in decode |
| 44 | Format failure symptom | Trailing commentary after the JSON block |
| 45 | Robust parse | Extract first balanced brace block, ignore preamble |
| 46 | Ambiguity failure | Two valid JSON objects -> pick first, log a warning |
| 47 | Grounding | Facts in context beat facts in parametric memory |
| 48 | Context vs retrieval | RAG injects facts at inference (Lab 04) |
| 49 | Long-prompt drift | Models weight mid-context weakly; keep decisive text near the ends |
| 50 | Instruction at end | Recency helps the operative instruction land |
| 51 | Example diversity | Cover error classes, not just happy path |
| 52 | Negative examples | "Not this: ..." prevents the most common misreads |
| 53 | Token budgeting | Truncate context before examples; never the schema |
| 54 | Prompt drift metric | Track exact-match rate per version over time |
| 55 | Canary prompts | Known-answer prompts that must never change output |
| 56 | Regression suite | Golden set of prompts + expected schema validity |
| 57 | Eval set hygiene | Held out, versioned, never used for tuning |
| 58 | Confidence proxy | Sampled agreement rate across k attempts |
| 59 | Instruction vs constraint | Constraint at API level beats instruction at text level |
| 60 | Anti-pattern | "Answer in at most 3 sentences" without an output schema |
| 61 | Anti-pattern | Escaping user input by string concatenation into policy |
| 62 | Anti-pattern | Retrying invalid JSON indefinitely |
| 63 | Anti-pattern | Shipping a prompt change with no version bump |
| 64 | Observability | Log rendered prompt hash, model, params, latency, parse outcome |
| 65 | Failure taxonomy | Refusal, truncation, malformed output, wrong-but-valid, injection |
| 66 | Wrong-but-valid | Schema passes but semantics fail — needs semantic eval |
| 67 | Refusal handling | Offer a rephrase path rather than a dead end |
| 68 | Truncation detection | finish_reason = length -> prompt engineering fix |
| 69 | Multimodal prompts | Text + image in one message, tags delimit each part |
| 70 | Latency budget | Extra reasoning passes multiply latency; measure before shipping |

## Self-Check

55+ = strong, 45-54 = redo Exercises 6 and 10, below that reread THEORY 2-10.