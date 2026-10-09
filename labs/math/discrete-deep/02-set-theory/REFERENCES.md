# References: Set Theory

## Primary Sources

- **Georg Cantor, "Über eine Eigenschaft des Inbegriffs aller reellen algebraischen Zahlen" (1874)**, *Journal für die reine und angewandte Mathematik*, 77:258–262. The first uncountability proof; short and still readable.
- **Georg Cantor, "Beiträge zur Begründung der transfiniten Mengenlehre" (1895, 1897)**, *Mathematische Annalen* 46, 48. The two-part founding paper of ordinal and cardinal arithmetic.
- **Ernst Zermelo, "Untersuchungen über die Grundlagen der Mengenlehre I" (1908)**, *Mathematische Annalen* 65:261–281. The original axiomatization (English translation in Jean van Heijenoort, *From Frege to Gödel*, 1967).
- **Bertrand Russell, letter to Gottlob Frege, 16 June 1901**, reprinted in van Heijenoort's anthology alongside Frege's reply. The paradox that ended naive comprehension.

## Textbooks

- **Paul Halmos, *Naive Set Theory* (Van Nostrand, 1960; Dover reprint)**. The standard first book: 12 short chapters covering ∪, ∩, products, relations, functions, cardinals, and the axiom of choice with no formalism overhead. Ideal companion to this lab.
- **Herbert Enderton, *Elements of Set Theory* (Academic Press, 1977)**. Gentler than Halmos; builds the natural numbers from scratch using ordered pairs.
- **Thomas Jech, *Set Theory* (Springer, 3rd ed. 2003)**. The graduate standard: forcing, independence, and large cardinals in one volume.
- **Kenneth Kunen, *Set Theory* (Elsevier, 2011)**. Covers ZFC, consistency proofs, and forcing with a model-theoretic flavor.
- **Abraham Fraenkel, Yoav Bar-Hillel, Azriel Levy, *Foundations of Set Theory* (North-Holland, 1973)**. The history and the independence results in context.

## On the Paradoxes and the Crisis

- **José Ferreirós, *Labyrinth of Thought* (Birkhäuser, 1999)**. Standard history of how Cantor and Dedekind arrived at set-theoretic thinking.
- **Stewart Shapiro, *Foundations without Foundationalism* (Oxford, 1991)**. Second-order logic and the ZFC axioms as a framework choice.

## For the Programming Angle

- **Joshua Bloch, *Effective Java*, 3rd ed. (Addison-Wesley, 2018), Item 10–17**. The canonical treatment of `equals`/`hashCode` contracts that make `HashSet` behave like a mathematical set.
- **Joshua Bloch, *Effective Java*, Item 58** ("prefer streams to recursion") and the collection guidance on choosing `Set` implementations.
- **Alfred Aho, Jeffrey Ullman, Ravi Sethi, *Compilers: Principles, Techniques, and Tools*, 2nd ed. (Pearson, 2006)**. Symbol-table construction and bit-set dataflow analysis — sets in real compiler machinery.
- **Donald Knuth, *The Art of Computer Programming*, Vol. 1, 3rd ed. (Addison-Wesley, 1997), §1.1** — set algorithms as subroutines of basic programming.

## Formal Systems

- **ZFC axiom list**: extensionality, empty set, pairing, union, power set, separation, replacement, infinity, foundation, choice (in ZF+Choice). See Kunen, Chapter I, for each axiom's motivation.
- **Kurt Gödel, *The Consistency of the Axiom of Choice and of the Generalized Continuum-Hypothesis with the Axioms of Set Theory* (Princeton, 1940)** and **Paul Cohen, "The independence of the continuum hypothesis" (PNAS 50, 1963; 51, 1964)** — the two halves of the independence theorem.
