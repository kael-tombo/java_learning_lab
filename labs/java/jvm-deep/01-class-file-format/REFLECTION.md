# Reflection: Class File Format

## Recalling the probes

- Without looking: write the 8-byte header layout (field names,
  widths, probe values for `--release 17`). Which two bytes did the
  release flag actually change?
- Sketch the pool index line for a class holding one `long`, one
  `double`, one `String`: where do the gaps fall, and which indices
  are dead?
- Reproduce `stack=3, locals=4, args_size=3` from the probe source
  alone: which source element owns each local slot?

## Checking your model

- If someone shows you `javap -v` output with `#12 = Long` then
  `#13 = ...`, what do you conclude — corrupt file, old `javap`,
  or hand-edited dump? What single question settles it?
- A method has 5 `ifeq` branches but no `StackMapTable`. List the
  two possible explanations (class-file version vs toolchain), and
  the command that distinguishes them.
- Your service prints a stale config value after a library-only
  redeploy. Which `javap` invocation proves `ConstantValue` inlining
  is the cause, and what rebuild fixes it?

## Connecting forward

- Class loading (lab 02) links these bytes: which three header/pool
  facts does the verifier need before it can check `max_stack`?
- Bytecode reading (lab 03) interprets the `code[]` bytes these
  headers describe: how does knowing `locals=4` change how you read
  `iload_3` vs `iload_0`?
- Generation (lab 04) must emit every field you read here: which
  two header values would you refuse to hand-compute, and why does
  the builder API derive them instead?

## What would you teach

- Explain the phantom index 0 to a colleague in two sentences using
  the `super_class == 0` case. Then explain the double-slot rule
  using `#12 → #14`. Which explanation needed a diagram, and why?
- State the stale-constant rule as a deploy checklist item (one
  line) that a build engineer could enforce without knowing JVMS §4.
