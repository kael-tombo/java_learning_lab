# Reflection: Bytecode Generation

## Recalling the probes

- State the exact `withMethod` argument list for `Gen.add` (name,
  type expression with `CD_int`, flags) and the four builder calls
  in its body. Which values does the builder derive that you never
  pass?
- Reproduce the `DropMethod` transform lambda from memory. What does
  returning without `builder.with` do, and what does the output
  listing show (`[<init>]`, smaller bytes)?
- Write the five-line `GenerateMax` branch shape (`newLabel`,
  loads, `if_icmpge`, returns, binding). Where does the merge frame
  come from?

## Checking your model

- `parse` then `majorVersion()` disagrees with `xxd` bytes 6–7.
  Which is wrong — the model, the dump, or your fixture handling?
  What single-process check (snippet 5) settles it?
- A transform drops `main` by name and accidentally removes an
  overload you wanted. What second predicate (lab 03's linkage
  identity) makes the drop surgical?
- Generated `GenMax` throws `VerifyError` at `defineClass`. Is the
  bug in the magic, the version, or the branch graph — and which
  probe line distinguishes version failures from verify failures?

## Connecting forward

- Lab 01's struct is this lab's material: which three `Code`
  sub-fields do you now derive instead of read, and which pool rule
  (wide entries) still applies to builder-allocated pools?
- Lab 03's five invokes are generatable: which builder calls would
  emit an `invokestatic` site, and what pool entries would the
  builder allocate for it?
- Lab 05 loads generated code through `defineClass` + `findStatic`:
  why is the lookup's `MethodType` the same string family as the
  builder's `MethodTypeDesc`?

## What would you teach

- Explain withhold-to-delete to a colleague using the ASM
  `visitMethod`-returns-null parallel in two sentences. When is
  transform the wrong tool (new classes) and what replaces it?
- State the preview-rig rule (`--release 23 --enable-preview` both
  halves) as a one-line CI check a build engineer could enforce.
