# Common Mistakes: Class File Format

## 1. Stepping the pool index by 1 past Long/Double

`Long=5` and `Double=6` consume two slots. After `#12 = Long`, index
13 is dead and the next entry is `#14`. A hand parser doing `i++`
misaligns every later entry and reports garbage tags.

Fix: when the tag is 5 or 6, advance the slot counter by 2. The
lab's PoolGap probe asserts the gap by parsing `javap -v` output.

## 2. Treating javap numbering as dense

Same cause, different symptom: searching for `#13` after a `Long` at
`#12` and concluding the dump is corrupt. It is not — JVMS §4.4.5
mandates the hole. Expect gaps; assert structure, not indices.

## 3. Reading index 0 as the first entry

Index 0 is reserved. `constant_pool_count` is entries + 1, so real
entries are count − 1. A zero `super_class` is legal and means the
class is `java.lang.Object`; a zero attribute index never occurs.

## 4. Memorizing major versions instead of measuring

The table (45=1.1 … 52=8, 55=11, 61=17, 65=21, 67=23) is long enough
to misremember. Compile with `--release N` and read bytes 6–7. The
lab's ReleaseToMajor probe pins 8→52, 17→61, 21→65 empirically.

## 5. Assuming StackMapTable is always present

Straight-line methods have no merge points, so `javac` emits no
frames. The StackMaps probe shows `straight` without the attribute
and `branchy` with it. Absence in linear code is correct, not a bug.

## 6. Hand-editing max_stack / max_locals

They look like tuning knobs; they are checked claims. `stack=3,
locals=4` in the probe decomposes exactly (this + x + neg + y). A
class claiming `stack=1` while pushing 2 fails verification with
`VerifyError` at link time.

## 7. Expecting minor_version to matter

`javac` emits minor 0. Branching on it (e.g., rejecting nonzero
minors) breaks exotic but legal producers. Gate on major only.

## 8. Recompiling only the constants class

`static final int PORT = 8080` carries a `ConstantValue` attribute and
inlines into every client at client-compile time. Changing the library
without recompiling clients leaves the old value baked in. This is
the stale-constant bug, not a class-loading bug.

## 9. Confusing BootstrapMethods with bytecode

`BootstrapMethods` is an attribute naming linkage methods; the pool's
`InvokeDynamic=18`/`Dynamic=17` entries point at it. The attribute
does not execute — it is consulted once per dynamic site at first run.
