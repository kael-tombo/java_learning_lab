# AI Safety & Alignment — Theory

Safety work asks: when a system escapes our design intent, how do failures happen, what
guards exist, and what do we still not know. This file stays conceptual — where facts are
contested or fast-moving, that is said plainly rather than claimed.

## The framing pieces

- **Objectives vs proxies**: agents are trained on what we can measure; optimizing a
  measurable proxy can diverge from the real goal. The snippet on proxy gaps is the toy
  version: a reward model scoring flattery over correctness gets argmax-selected against,
  and factual accuracy drops — by construction.
- **Specification gaming**: known family of behaviors where systems satisfy the letter of
  a scored objective while missing its intent (loop exploits, shortcut wording, reward
  hacking). Naming the pattern helps reviews spot it; magnitudes are environment-specific.
- **Uncertainty honesty**: for open-ended generated systems, predictions about behaviors
  are contested; the vocabulary the field uses (capability jumps, misuse surface,
  eval coverage gaps) is descriptive, not numerically proven. Treat every forecast with
  error bars and say what evidence would move yours.

## The guardrails people actually deploy

- Behavioral constraints: system-prompt rules, refusal-pattern filters, output classifiers,
  jailbreak evasion tests — detection-style defenses, no absolute guarantee claimed.
- Process constraints: human review gates for sensitive actions, allowlists of permitted
  tool verbs, separation between proposal and execution.
- Monitoring: logging rates by category, incident triage, red-team cycles. Codified
  review cadences (who signs off, when re-run happens) are the operative artifact.

## Assumptions this lab makes explicit

Methods cited in the standard sequence (behavioral cloning of demonstrations, then reward
training, then policy optimization) describe a training-process skeleton, not a claim
about any particular model's internals. The guard snippets simulate small, static cases:
they demonstrate the LOGIC of selective deployment and proxy gaps, nothing about large
scale systems. Every claim about deployment (e.g., evaluation coverage, escalation
latency) is scoped to an invented workspace.

## What you should build in this folder

- The selective-prediction trade: a sweep showing coverage-accuracy coupling, done as
  runnable code with printed rows.
- A proxy-gap scenario built argmax-by-argmax, so the mechanism is transparent instead of
  folklore — your write-up gets graded on naming what was and wasn't assumed.
