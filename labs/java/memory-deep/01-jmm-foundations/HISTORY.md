# History: The Java Memory Model

## 1996: the original model ships with Java 1.0

The first JMM tried to define thread semantics alongside the language.
It was widely regarded as broken within a few years: volatile had
implementation-dependent meaning, `final` had no thread-safety story,
double-checked locking (then standard practice) was silently incorrect,
and the spec arguably permitted out-of-thin-air reads. Practitioners
learned to synchronize "to be safe" without a precise rule for what
safety meant.

## 1999-2004: JSR-133 rewrites chapter 17.4

JSR-133 (Manson, Pugh, with Doug Lea's concurrency group; Brian Goetz
documenting and popularizing) rebuilt the model around happens-before.
Shipped with Java 5 (2004) alongside `java.util.concurrent`, it gave:
volatile acquire/release-plus-SC semantics, the monitor chain rule, the
start/join rules, final-field freeze semantics, documented library
edges, and the causality requirements of JLS 17.4.8. The DCL idiom
became correct *with* a volatile field — the canonical before/after
exhibit of the rewrite.

## Why happens-before won

Alternatives (pure sequential consistency everywhere; hardware-specific
rules in the language spec) were either unaffordable (every access
fenced) or unportable (x86 vs ARM rules in user code). Happens-before
splits the difference: programmers declare order where it matters,
implementations fence exactly there, everything else runs free. The
DRF-implies-SC theorem is the sales pitch: order what races, and the
intuitive interleaving model holds.

## 2004-today: stability as a feature

The model has been essentially unchanged for 20+ years — unusual for a
concurrency spec, and the reason the later labs treat it as bedrock.
What changed around it: compilers got more aggressive (C2 hoisting that
makes missing volatiles bite harder), hardware got weaker (ARM servers
where x86-accidental code fails), and the library grew (VarHandle
access modes in Java 9 expose acquire/release/opaque directly). None of
that moved the rules; all of it raised the cost of ignoring them.

## What this lab's demos owe to history

- `StartEdge`/`JoinEdge` exercise the 1996 rules that survived intact:
  thread lifecycle edges, now precisely specified.
- `LockEdge` exercises the monitor rule the original model had but
  under-specified; JSR-133 made the unlock->lock chain exact.
- `LatchEdge` shows the Java 5 payoff: library edges as first-class hb
  sources, so user code rarely hand-rolls flag protocols.
- `CausalityFloor` exhibits the JSR-133 addition with no 1996
  ancestor: values must come from somewhere, even in racy code.

## Dates to keep straight

- 1996: original (flawed) JMM ships.
- 2004: JSR-133 rewrite ships in Java 5 (Manson/Pugh/Goetz era).
- 1967 (Tomasulo) and 2010 (x86-TSO formalization) belong to lab 02's
  story, not this one: CPU reordering history explains the phenomena,
  JSR-133 explains the contract that tames them.
