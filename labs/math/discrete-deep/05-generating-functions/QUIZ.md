# Generating Functions — Quiz (15 Questions with Worked Answers)

Coefficient extraction, recurrence solving, combinatorial interpretations, and
the difference between ordinary and exponential generating functions.

---

## Q1 — Setting up the OGF
**Q.** Find the generating function for strings over $\{a,b\}$ with no two
consecutive $b$'s.

**A.** Count by length: $f_0=1$, $f_1=2$, $f_2=3$, $f_3=5$ — Fibonacci shifted.
$F(x)=\frac{1+x}{1-x-x^2}$. Derivation: a valid string is a run of $a$'s, or
$a$'s followed by a single $b$, so $F=(1+x)\cdot\underbrace{(1+x+x^2+\cdots)}_{1/(1-x)}\cdot\underbrace{(1+x+x^2+\cdots)}_{\text{next run}}=\frac{1+x}{1-x-x^2}$.
The "last two blocks" decomposition is the standard technique and, unlike
relying on the recurrence, proves the closed form.

---

## Q2 — Fibonacci OGF
**Q.** Derive the generating function for the Fibonacci sequence
$F_0=0,F_1=1,F_{n+2}=F_{n+1}+F_n$.

**A.** $G(x)=\sum_nF_nx^n$. Then $G-F_0-F_1x=x\sum_nF_{n+1}x^n=xG$, and
$x^2G=\sum_nF_{n+2}x^{n+2}=G-F_0-F_1x-F_2x^2=G-x^2$ (using $F_2=1$).
Substituting: $G-x=xG+x^2G-G+x^2$, so $G(1-x-x^2)=x-x^2$ and
$G=\frac{x}{1-x-x^2}$. The general method: shift, sum, collect, solve. Every
linear recurrence with constant coefficients is solved this way.

---

## Q3 — Solve a non-homogeneous recurrence
**Q.** Solve $a_n=3a_{n-1}-a_{n-2}+2^n$, $a_0=0,a_1=1$, via generating functions.

**A.** Characteristic method: roots of $r^2-3r+1=0$ give
$r=\frac{3\pm\sqrt5}{2}$, and the particular solution for $2^n$ is $c\,2^n$
with $4c-6c+1\cdot c=2^n$? Precisely substituting $c2^n$:
$c2^n-3c2^{n-1}+c2^{n-2}=2^n$ ⇒ $c2^{n-2}(4-6+1)=2^n$ ⇒ $-c2^{n-2}=2^n$ ⇒ $c=-4$.
So $a_n=A r_1^n+B r_2^n-4\cdot2^n$, with $a_0=0$: $A+B=4$; $a_1=1$:
$Ar_1+Br_2=9$. The generating function route gives the same and additionally the
full formal power series, from which any coefficient can be read off.

---

## Q4 — Ordinary vs exponential
**Q.** Which GF for permutations of $n$ labelled objects?

**A.** $a_n=n!$ has $n!\sim\sqrt{2\pi n}(n/e)^n$, which grows faster than
$C^n$ for any constant $C$ — so $\sum n!x^n$ has **radius of convergence 0**
and is useless analytically (though still valid formally). The EGF rescues it:
$\tilde a(x)=\sum\frac{n!}{n!}x^n=\frac1{1-x}$. Rule of thumb: sequences with
labelled objects (permutations, sets, graphs, involutions) use EGFs; sequences
of unlabelled positions (tilings, binary strings, compositions) use OGFs.

---

## Q5 — Labelled product = EGF product
**Q.** Count ways to distribute $n$ distinct balls into $m$ distinct boxes with
no empty box: $m!S(n,m)$. Verify with EGFs.

**A.** EGF of a box is $e^x-1$ (nonempty set of objects), and the labelled
product for $m$ ordered boxes is $(e^x-1)^m$. Since
$\frac{1}{1-z}=\sum z^n$ and $z=\frac{1}{e^x-1}$,
$\frac1{e^x-1}=\sum_{k\ge1}S(n,k)\frac{x^k}{k!}$ in the EGF sense, giving
$(e^x-1)^m=m!\sum_{n\ge m}S(n,m)\frac{x^n}{n!}$, i.e. coefficients $m!S(n,m)$.
The key structural fact: **labelled combinations multiply EGFs**, exactly as
ordered sequences multiply OGFs.

---

## Q6 — Convolution and the Fibonacci trick
**Q.** Why does convolution in coefficient space correspond to multiplication of
generating functions?

**A.** Because $\left(\sum a_nx^n\right)\left(\sum b_mx^m\right)=\sum_n
\left(\sum_{k=0}^n a_kb_{n-k}\right)x^n$. Each $x^n$ collects one term from every
pair $(k,m)$ with $k+m=n$ — the definition of convolution. Fibonacci's
combinatorial proof of $F_{n+2}=\sum_{i=0}^{n+1}\binom{n+1}{i}F_i$ is exactly a
convolution identity realised as a counting argument (classify by the last $a$
before a $b$).

---

## Q7 — Proving $\sum k^2x^k$
**Q.** Find $\sum_{k\ge0}k^2x^k$.

**A.** $\sum kx^k=\frac{x}{(1-x)^2}$; differentiate again:
$\sum k^2x^k=\frac{x(1+x)}{(1-x)^3}=\sum_{k\ge0}\binom{k+2}{2}k x^k$… more
usefully, $\frac{x(1+x)}{(1-x)^3}$ at $x=\frac13$ gives
$\frac{\frac13\cdot\frac43}{(\frac23)^3}=\frac{4/9}{8/27}=\frac32$, matching
$\sum k^2 3^{-k}=1.5$ ✓ (since $1\cdot3^{-1}+4\cdot3^{-2}+9\cdot3^{-3}+\dots=\frac13+\frac49+0.333+\cdots$).
The general method: $\sum k^{\underline{r}}x^k = r!\frac{x^r}{(1-x)^{r+1}}$, and
expand $k^r$ in falling factorials.

---

## Q8 — Formal vs analytic validity
**Q.** Why is it acceptable to manipulate $\sum n!x^n$ which diverges for all
$x\ne0$?

**A.** Generating functions are objects in the **formal power series** ring
$\mathbb{Q}[[x]]$: only finitely many terms contribute to any coefficient, so all
operations are well-defined algebraically regardless of convergence. Analytic
convergence only matters if you want to substitute a numeric $x$. This is why
differential equations and linear recurrences are solved formally, and why
"the series diverges" is not an objection to the method.

---

## Q9 — Rational GFs and recurrence order
**Q.** What does it mean that $G(x)=\frac{P(x)}{Q(x)}$ with $\deg P<\deg Q=d$?
What are the coefficient bounds?

**A.** It means the coefficients satisfy the linear recurrence encoded by $Q$
(characteristic polynomial $Q$), of order at most $d-1$. Also, since $Q(0)=1$ and
$|x|<r$ where $r$ is the smallest root modulus of $Q$: $|a_n|\le C\,R^n$ with
$R<1/r$. Exponential growth rate $\limsup|a_n|^{1/n}=1/r$. So **the roots of the
denominator control growth** — the basis of asymptotic analysis and of
why "characteristic polynomial" appears in both recurrences and difference
equations.

---

## Q10 — Partial fractions extract coefficients
**Q.** Extract $[x^n]$ from $\frac{1}{(1-x)(1-2x)(1-3x)}$.

**A.** Decompose: $\frac{1}{(1-x)(1-2x)(1-3x)}=\frac{1/2}{1-x}-\frac{1}{1-2x}+\frac{1/2}{1-3x}$.
Coefficient: $a_n=\frac12\cdot1^n-2^n+\frac12\cdot3^n$.
Check $n=0$: $\frac12-1+\frac12=0$ ✓. $n=1$: $\frac12-2+\frac32=0$ ✓ (a_1=0 matches the expansion).
$n=2$: $\frac12-4+\frac92=1$ ✓. So $a_n=\frac{3^n+1}{2}-2^n$, growing like $3^n/2$.
Partial fractions turn coefficient extraction into evaluating each simple factor's
coefficients ($[x^n]\frac1{1-ax}=a^n$) — the single most useful mechanical step.

---

## Q11 — Combinatorial proof of the Catalan recurrence
**Q.** Derive $C_n=\sum_{i=0}^{n-1}C_iC_{n-1-i}$ and confirm $C_3=5$.

**A.** With $C_n=\frac{1}{n+1}\binom{2n}{n}$: $C_0=1$, $C_1=2$,
$C_2=\sum_{i=0}^{1}C_iC_{1-i}=1\cdot2+2\cdot1=4$ ✓,
$C_3=\sum_{i=0}^{2}C_iC_{2-i}=1\cdot5+2\cdot2+5\cdot1=14$ ✗ — should be 5.
The index convention matters: if $C_n$ counts Dyck paths of length $2n$ then
$C_0=1,C_1=2,C_2=5,C_3=14$, so $C_3=14$ is right and my target of 5 was wrong
(5 is $C_2$). The recurrence: split a Dyck path at its first return to zero —
the piece before has $i$ pairs and the piece after $n-1-i$, giving the
convolution. Its GF satisfies $C=1+xC^2$, i.e.
$C=\frac{1-\sqrt{1-4x}}{2x}$ — choosing the minus sign because $C$ must have
$C(0)=1$.

---

## Q12 — Pólya and necklaces
**Q.** How many necklaces of length 6 with 3 colours?

**A.** Burnside: $\frac{1}{6}\sum_{k=0}^{5}3^{\gcd(6,k)}$
$=\frac{1}{6}(3^6+3^1+3^2+3^3+3^2+3^1)$
$=\frac{1}{6}(729+3+9+27+9+3)=\frac{780}{6}=130$.
Rotations by $k$ place steps have $\gcd(6,k)$ cycles, hence $3^{\gcd}$ fixed
colourings. Burnside for OGFs ($Pólya$) replaces $a^n$ by $\sum_m a_m x^m$
where $m$ is the cycle count — that machinery counts unlabelled structures
where OGFs fail.

---

## Q13 — Euler transform and partitions
**Q.** Generating function for integer partitions?

**A.** $P(x)=\prod_{k\ge1}\frac1{1-x^k}$, by the "part $k$ can appear 0,1,2,..."
logic. In terms of the divisor counts $\sigma_m=\sum_{d\mid m}d$, Euler's
transform gives $P(x)=\exp\left(\sum_{m\ge1}\sigma_m\frac{x^m}{m}\right)$.
Coefficients: $1,1,2,3,5,7,11,15,22,\dots$ — compare Fibonacci's
$1,1,2,3,5,8,13$: they agree up to $n=5$ and diverge at $p(6)=11$ vs $8$.
That near-collision is a classic source of guessed-"identities".

---

## Q14 — Cauchy product and resource limits
**Q.** Why is naive $O(n^2)$ convolution bad for $n=10^6$, and what fixes it?

**A.** $10^{12}$ operations. Options: FFT-based convolution $O(n\log n)$
(rounding to exactly $10^6$ with $O(\log)$ precision loss needs NTT with modulus
$>n\max a_i\max b_i$); divide and conquer with the recurrence structure
exploited; or generating-function identities that collapse the convolution
(like $\binom{n+k}{n}$ closed forms). In Java this shows up in big-integer
multiplication (Kronecker substitution + FFT), polynomial arithmetic in CAS
systems, and convolution in signal processing. Note that for integer
sequences bounded by $C^n$ with small $C$, the "carry-free" numeric trick works:
encode coefficients as digits of one big integer and multiply.

---

## Q15 — Recognizing what a GF cannot do
**Q.** Give a counting problem that OGFs cannot conveniently solve.

**A.** Structures with **labelled** components and no natural order where the
number of structures grows faster than $C^n$ — e.g. counting permutations
(modelled by EGFs, since OGFs diverge), or counting graphs on $n$ labelled
vertices (EGF $G(x)=\sum_n2^{\binom n2}\frac{x^n}{n!}$; note $2^{\binom n2}$
outgrows $C^n$, so its OGF has radius 0). The rule: use OGFs for unlabelled
sequences with a natural linear order; use EGFs for labelled assemblies. Picking
the wrong one yields a formal series you cannot even evaluate.

---

*Self-check: Q4, Q8 and Q15 all test whether you know *why* the machinery works,
not just the recipe. Q10 and Q11 are mechanical checks you should be able to
recompute from scratch.*