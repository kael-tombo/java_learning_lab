# Mini Project - Gradebook CLI (fundamentals)

Build in 2-4h: a CLI gradebook exercising types, control flow, OOP, exceptions, generics.
## Goal
A `Gradebook` CLI reads `name,score` lines, assigns letter grades, prints a summary and exits nonzero on bad input.
## Requirements
- [ ] Parse args: `java -cp out Gradebook <file>`; missing file prints usage to stderr, exit code 2.
- [ ] Grade with a switch expression: 90+ A, 80+ B, 70+ C, else F.
- [ ] Model Student as a record and Roster as a generic `Box<T>`-style holder with add/get.
- [ ] Catch NumberFormatException per line: report `bad=<line>` and continue, exit code 1 if any line failed.
- [ ] Reject scores outside 0-100 with IllegalArgumentException and a clear message.
- [ ] 3+ tests: grade boundaries (89/90), bad-line handling, empty-file summary.
## Steps
1. Scaffold `Gradebook.java`, `Student.java`, `Roster.java`; compile with `javac --release 21 -encoding UTF-8`.
2. Implement parse -> grade -> summarize loop; print `name=grade` per student plus class average.
3. Add a Main-style self-check (assert-like prints) covering the 3 test cases above.
4. Record one metric: wall-time via System.nanoTime for a 10k-line file.
## Starter sketch
```java
public class MiniApp {
  public static void main(String[] a) { System.out.println("mini running"); }
}
```
Observed: mini running. Grow this into Gradebook: replace the println with arg parsing first.
## Sample run
Input file: `ada,95` / `bob,x9` / `cy,72`. Expected stdout: `ada=A`, `bad=x9`, `cy=C`, `avg=83.5`.
Exit code 1 (one bad line), stderr empty except usage errors.
## Rubric (10)
- Functionality 4 (parses, grades, exit codes correct), edge cases 2, clarity 2, metric 2.
- Stretch: `--sort name` flag printing roster alphabetically via a lambda Comparator.
- Stretch: histogram of A/B/C/F counts printed after the average.
- Stretch: `--strict` flag aborting on the first bad line instead of continuing.
