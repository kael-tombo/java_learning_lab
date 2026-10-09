# History: Combinatorics

## Counting Before the Name Existed

**Zhu Shijie (朱世杰, c. 1261–1303)** illustrated the binomial coefficients in the *Jade Mirror of the Four Unknowns* (1303), where the triangle of additive coefficients appears as a table of "powers' coefficients." Persian mathematician **al-Karaji (c. 953–1029)** and **al-Samawal (c. 1130–1180)** used the same triangle to expand powers and stated the additive rule for its entries — six centuries before Pascal.

**Blaise Pascal (1623–1662)** wrote *Traité du triangle arithmétique* (1654, published 1665), systematizing the triangle's identities: row n sums to 2ⁿ, alternating rows sum to 0, and the hockey-stick sums — the treatise that made the Chinese/Persian triangle a named, citable object of study in Europe. In the same year he exchanged letters with **Pierre de Fermat (1601–1665)** about division of stakes in an unfinished game — the *problem of points* — which founded the combinatorial treatment of probability: count the equally likely futures, divide by the total.

**Jacob Bernoulli (1654–1705)** extended counting to powers in *Ars Conjectandi* (1713, posthumous), where the law of large numbers first appears alongside what we now call Bernoulli trials and the multiplication principle stated explicitly.

## The Binomial Theorem Generalizes

**Isaac Newton (1642–1727)**, in a 1665 letter to Henry Oldenburg, generalized the binomial expansion from integer exponents to fractional ones — (1+x)^(1/2) = 1 + x/2 − x²/8 + … — creating infinite series for real exponents. **Leonhard Euler (1707–1783)** used binomial coefficients in his work on partitions and later in combinatorial identities for sequences.

## Sieves and Inclusion–Exclusion

Counting "objects with at least one property" long predates the name: Eratosthenes' sieve (c. 250 BC) removes multiples. The general alternating formula — add single properties, subtract pairwise, add triple — appears in the 18th-century literature (it underlies the classical solutions of the birthday problem, discussed by **Abraham de Moivre (1667–1754)** in *The Doctrine of Chances*, 1730s/1738), and the coefficients are packaged in **August Ferdinand Möbius (1809–1868)**'s function μ (1832), where μ(n) is exactly the sieve sign attached to the divisors of n.

## Catalan Numbers: Euler to Catalan

**Leonhard Euler**, in a 1751 letter to **Christian Goldbach**, counted the ways to triangulate a convex polygon: an (n+2)-gon splits into n−1 triangles in Cₙ ways, giving 1, 1, 2, 5, 14, 42… He proved the recurrence Cₙ = Σ CᵢCₙ₋₁₋ᵢ. **Eugène Charles Catalan (1814–1894)** returned to the sequence in 1838 (counting ways to parenthesize n+1 factors), and the modern name "Catalan numbers" was popularized later in the 20th century; the sequence turns out to enumerate Dyck paths, binary trees, and non-crossing partitions alike.

## Stirling, Derangements, and Asymptotics

**James Stirling (1692–1770)**, in *Methodus Differentialis* (1730), introduced the numbers now bearing his name (arrangements by cycle type) and the approximation n! ≈ √(2πn)(n/e)ⁿ later refined by **Abraham de Moivre** and **Pierre-Simon Laplace**. **Pierre Rémond de Montmort (1678–1719)** posed the derangement problem (*Problème des ménages*-adjacent, 1708–1713) — the number of permutations with no fixed point, !n, converging to 1/e.

**Laplace's** *Théorie analytique des probabilités* (1812) made systematic counting of arrangements a technical discipline.

## Modern Combinatorics

**Frank Ramsey (1903–1930)** proved in 1930 that in any coloring of the edges of a large enough complete graph, a monochromatic complete subgraph must appear — "every graph contains order" — founding Ramsey theory. **George Pólya (1887–1985)** published his enumeration theorem (1937) for counting configurations up to symmetry. **Paul Erdős (1913–1996)** pioneered the *probabilistic method* (1947 onward): exhibit a combinatorial object by showing the number of bad objects is fewer than the total. **Richard Stanley**'s *Enumerative Combinatorics* (1986, 2nd ed. 2011) codified the modern field, with the **Stanley–Wilf conjecture** (proved 2004 by Marcus and Tardos) a landmark on permutation patterns.
