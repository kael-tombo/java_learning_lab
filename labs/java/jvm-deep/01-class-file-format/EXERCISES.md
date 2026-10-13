# Exercises: Class File Format

All tasks need a JDK (not JRE) on PATH for `javac`/`javap`. Use the
exact `--release` flags given; majors depend on them.

## 1. Read the 8-byte header by hand

Compile `public class V{}` with `--release 17`, then print bytes 0–9
as hex (see CODE_DEEP_DIVE snippet 1 for the reader shape).

Expect: `CA FE BA BE 00 00 00 3D` then pool count. `0x3D` is 61.
Repeat with `--release 8` (`0x34` = 52) and `--release 21`
(`0x41` = 65). Record all three before continuing.

## 2. Pin the release→major table

Extend snippet 2 to cover `--release 11` and `--release 23`.
Expect 55 and 67. You now own five measured rows (52/55/61/65/67)
instead of a memorized table.

## 3. Find the pool gap

Compile the PoolGap probe (`Probe2` with a `long`, a `double`, an
`int`, a `String`) with `--release 17`. Run `javap -v -p` and locate
the `Long` and `Double` entries.

Confirm: the index immediately after each is absent from the dump.
Write down both gaps (e.g., `#12 → #14`). Break your own parser on
purpose: parse with stride 1, watch every later entry misresolve.

## 4. Decompose a Code header

Compile the `Probe3.absOrNeg` probe with `--release 17`. Run
`javap -v -c -p` and copy the `stack=/locals=/args_size=` line.

Expect `stack=3, locals=4, args_size=3`. Map each local slot: 0
`this`, 1 `x`, 2 `neg`, 3 `y`. Explain where the value 3 in
`args_size` comes from (receiver + 2 params).

## 5. Correlate StackMapTable with branches

Compile `Probe4` (`straight` + `branchy`) with `--release 17`. Split
`javap -v -p` output per method.

Confirm: `straight` has no `StackMapTable`; `branchy` has one.
Add a second branch (e.g., a loop) to `straight`, recompile, and
confirm the attribute appears. Remove all branches from `branchy`
and confirm it disappears.

## 6. Reproduce the stale constant

Class `Lib { static final int PORT = 8080; }`, client prints
`Lib.PORT`. Compile both with `--release 17`, run (prints 8080).
Change `Lib` to 9090, recompile only `Lib`, rerun the old client.

Confirm it still prints 8080. Run `javap -c` on the client to find
the inlined `sipush 8080`. Recompile the client; confirm 9090.

## 7. Strip debug info and observe

Compile a throwing probe normally and with `-g:none`. Compare
`javap -v` (SourceFile/LineNumberTable present vs absent) and run
both to compare stack traces (`Unknown Source` in the stripped one).
