# Mental Models: Class File Format

## 1. The shipping manifest

Think of the class file as a freight manifest taped to a crate. The
first 8 bytes are the routing label (magic = "this is freight",
major = "which dock can unload it"). Everything after is an itemized
contents list. Like a manifest, it is read before anything is moved:
wrong label, and the crate is refused unopened (`ClassFormatError`,
`UnsupportedClassVersionError`).

## 2. The pool as a footnote system

Academic papers number each distinct citation once and reference it by
number. The constant pool works identically: each distinct string,
name, type, or method triple gets one numbered entry; bytecode cites
numbers. `String → Utf8` is a footnote pointing at an endnote that
holds the actual text. Deduplication is not an optimization pass — it
is the addressing scheme.

## 3. The missing hotel room

`Long`/`Double` entries are guests who booked two adjoining rooms and
occupy both. Room 13 stays empty because guest 12 took 12 and 13.
`javap` lists occupants, not rooms, so the directory jumps `#12 →
#14`. Index 0 is the lobby: numbered, but nobody sleeps there.

## 4. max_stack as the high-water mark

Picture a sink with the drain open: pushes run the tap, pops drain
it. `max_stack` is the high-water stain `javac` measured; the
verifier replays every path checking the water never exceeds the
stain. `locals=4` is the dish rack with fixed slots: this, x, neg in
the first three, y in the fourth. `args_size=3` is how many dishes
arrived with the order versus one washed on site.

## 5. StackMapTable as trail checkpoints

Pre-JSR-202 verification bushwhacked the whole trail to infer the
terrain. Now `javac` plants signed checkpoints (frames) at every
trail junction, and the verifier just checks the signs match the map.
A straight trail needs no signs — that is why linear methods carry no
`StackMapTable`.

## 6. ConstantValue as advance photocopies

A `static final` constant is photocopied into every client's notes at
lecture time (client compilation). Changing the professor's slide
later does not update anyone's photocopy. Recompiling the client is
fetching a fresh copy — the only fix for stale constants.
