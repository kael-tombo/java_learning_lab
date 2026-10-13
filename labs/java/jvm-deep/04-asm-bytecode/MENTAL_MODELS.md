# Mental Models: Bytecode Generation

## 1. Parse as reading through glass

`ClassModel` is a museum case over the original bytes: you see every
exhibit (methods, flags, versions) without touching anything. The
glass is the point — inspection cannot smudge the artifact, and ten
readers share one case cheaply. `build` is the gift-shop copy, cast
fresh from your selections.

## 2. Builders as dictation, not bricklaying

You dictate instructions (`iload, iadd, ireturn`) to a clerk who
measures, frames, and files as you speak: stack depths tallied,
merge frames drafted, pool entries numbered. ASM's `COMPUTE_FRAMES`
was hiring a surveyor after construction; the classfile builder is a
clerk who surveys while you talk. You never touch a tape measure
(`max_stack`) or a zoning form (`StackMapTable`).

## 3. Labels as named trail junctions

Raw bytecode jumps by numbered paces ("skip ahead 7 bytes") —
renumber every insertion by hand. Labels name the junction ("the
overlook") and let the builder repave distances after all edits.
`labelBinding` plants the sign; `if_icmpge` follows it wherever it
moves. Control flow becomes geography instead of arithmetic.

## 4. Transform as a bouncer's list

Every element queues past the lambda; `builder.with(e)` waves it
through, returning silently turns it away. Dropping `main` is not
deletion — it is non-admission to the new club. Order preserved,
no gaps to sweep: the absentees simply never re-materialize.

## 5. ASM↔classfile as saxophone↔piano

Same score (parse→transform→emit), different instruments: ASM plays
events in time (SAX callbacks you catch as they fly), the classfile
API lays out keys you press deliberately (views and builders).
Musicians switch instruments keeping the music; engineers switch
APIs keeping the operation graph.

## 6. defineClass as the building inspector

However clever the construction, the inspector (`defineClass`
verification) walks the finished building with lab 01/03's checklist:
headers consistent, frames at merges, pool indices in range. Bribes
rejected — failure is `VerifyError` posted on the door, never a
quiet occupancy.
