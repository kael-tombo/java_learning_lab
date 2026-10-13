# Reflection: Bytecode Introduction

## Recalling the probes

- Write the six-opcode `add3` sequence from memory, with stack depth
  after each instruction. Where does left-associativity show?
- List which probe method produced each of the five invokes, and the
  callee kind that selected it (static/private/virtual/interface/lambda).
- State the four descriptors from `javap -s` without looking, then
  mark where erasure removed information.

## Checking your model

- A dump shows `invokevirtual` where you expected `invokeinterface`.
  What does that tell you about the receiver's declared type? What
  one-word source change flips the instruction?
- `mh.invokeExact("not-a-double")` on a `(double)double` handle:
  which exception, thrown when (link vs run), and what two fixes
  exist? Which fix belongs in a hot loop?
- Two lambdas produce how many `invokedynamic` sites, how many
  `lambda$` methods, and how many runtime class definitions on a
  cold start? Which of those three numbers grows per loop iteration
  for a capturing lambda?

## Connecting forward

- Lab 01's pool-gap rule reappears here as tag table errata: why do
  wide entries and the tag-11 correction both punish hand parsers,
  and what single habit (check against JVMS §4.4) prevents both?
- Lab 04 generates the instructions you read here: which builder
  calls emit the `add3` sequence, and what does the builder derive
  that `javap` merely reports (`max_stack`, frames)?
- Lab 05 composes the handles introduced here: how does
  `guardWithTest`'s full-arg-list rule mirror `invokedynamic`'s
  full type descriptor at the call site?

## What would you teach

- Explain the five invokes to a colleague using five one-line code
  examples, each naming its dispatch mechanism. Which two are most
  often confused, and what sentence separates them?
- State the verification story (four passes, frames at merges) as a
  three-sentence operational rule for anyone hand-editing bytecode.
