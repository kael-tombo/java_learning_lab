# Lab 03: Prompt Engineering Patterns — Theory

## 1. What a Prompt Actually Is

A prompt is not magic; it is a **program in a probabilistic language**. Tokens are
laid out to (a) specify the task, (b) constrain the output space, (c) supply
retrieval context, (d) define the stop condition. Prompt engineering is the
discipline of arranging those four things so the next-token distribution is
sharply peaked where you want it.

## 2. The Four Levers

1. **Role framing** — "You are a ..." changes the conditional distribution
   because pretraining contains many role-conditioned continuations.
2. **Format specification** — explicit schema (JSON, table, bullet list) reduces
   variance more than adding adjectives.
3. **Context injection** — facts in the prompt are the model's only source of
   truth at inference time (this is the RAG hand-off, Lab 04).
4. **Constraint / decoding controls** — `stop`, `max_tokens`, temperature,
   structured-output / function schemas. These are API-level, not text-level.

## 3. Zero-Shot vs Few-Shot

- **Zero-shot**: instruction only. Works when the task is well represented in
  pretraining.
- **Few-shot (k-shot)**: `k` input/output demonstrations in the context. The
  model pattern-matches the format. Rule of thumb: k = 3-8; diminishing returns
  past that, and each shot costs tokens on every call.
- Choose demonstrations that cover the **decision boundary** of your label space,
  not random examples — boundary examples teach the decision.
- Keep the ordering deterministic; models are sensitive to example order
  (position bias), so randomize and average when evaluating.

## 4. Chain of Thought (CoT)

Stating intermediate reasoning before the answer raises accuracy on arithmetic,
commonsense, and symbolic tasks. Two families:

- **Zero-shot CoT**: append "Let's think step by step." Surprisingly strong
  because such rationales appear abundantly in pretraining.
- **Self-consistency**: sample k CoT paths at T > 0, take the majority final
  answer. Cost multiplies by k; accuracy improves by several points.

Chain-of-verification (Lab 05/09 territory) adds a separate pass that asks the
model to check each claim against the evidence, catching hallucinated steps.

## 5. Tree of Thought and Decomposition

- **Tree-of-Thought**: expand multiple candidate branches, evaluate each with a
  heuristic or a model, backtrack. Handles problems where the first plausible
  step is wrong (Sudoku, planning).
- **Decomposed prompting (DecomP)**: a planner breaks the task into independent
  subtasks, a solver handles each, a combiner merges. Maps naturally to Java
  method composition — see Exercise 6.
- **Least-to-most**: order subproblems by difficulty so the model conditions on
  solved simpler ones.

## 6. Structured Output

Strongest reliability lever: demand a schema and **parse defensively**.

```
Return JSON matching:
{"intent": "<one of: refund|status|other>", "amount_cents": <int|null>, "reason": "<=200 chars"}
```

Engineering rules:
- Prefer provider structured-output / grammar constraints over "please return JSON".
- Validate with a schema; on failure, repair once, then fall back to a rule-based
  extractor (regex for ids, keyword buckets for intent).
- Never `eval()` model output. Parse, whitelist, and bound sizes.
- Set `stop` sequences so the model cannot trail off into commentary.

## 7. Automatic Prompt Engineering (APE)

Instead of hand-tuning: (1) ask the model to propose variations of an initial
prompt, (2) score each by running on a held-out validation set, (3) keep the best.
A practical Java version is a `PromptOptimizer` that mutates templates
(add/remove sections, reorder, change the instruction verb) and hill-climbs on
validation score. Budget: always define a validation set and a stopping rule,
otherwise you will overfit the validator.

## 8. Prompt Templates and Parameterization

Production prompts are code. Model them as:

```
System role | Instructions | Context | Input variables | Output schema
```

with a small Java builder that enforces section order, forbids unfilled
placeholders, and hashes the rendered result for caching. Template versioning is
covered in depth in `ai-engineering/lab05`.

## 9. Injection Surface

Anything you interpolate is an attack surface. Treat retrieved documents, user
text, and tool output as **untrusted data**, delimit them, and never let them
grant instructions. Lab 10 and `ai-engineering/lab09` build the defenses; the
prompt-side rules are:

- Delimit untrusted blocks with explicit markers and tell the model the content
  is data, not orders.
- Put policy in the system message, variables in the user message.
- Do not concatenate "ignore previous instructions" style text into your own
  templates.
- Validate the model output against a schema — the last line of defense.

## 10. Prompt Caching Economics

Providers bill repeated **prefix** tokens at a discount and most engines cache by
prefix hash. Put stable content first (system prompt, few-shot examples), volatile
content last (user query, timestamp). A 4k-token system prompt then costs near zero
on repeat calls. Lab 12 covers the numbers.

## 11. Java Design Patterns for Prompts

- `PromptTemplate` — immutable, `render(Map<String,Object>)`.
- `PromptRegistry` — version -> template, `current()`, `rollback()`.
- `StructuredOutputParser<T>` — schema + `parse(String)` + `repair(String)`.
- `PromptBuilder` — fluent section API with `assertNoUnfilled()`.
- `ChatMessage` record — `role`, `content`, with role validation.

## Key Takeaways

1. Specify output format explicitly; adjectives are not a specification.
2. Few-shot demonstrations should straddle the decision boundary.
3. Put stable prefixes first so prompt caching works.
4. Every interpolated value is untrusted input.
5. Schema-validate and repair; never eval.