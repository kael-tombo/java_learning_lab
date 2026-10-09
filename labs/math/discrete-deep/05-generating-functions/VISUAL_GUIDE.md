# Visual Guide: Generating Functions

## 1. Coefficients as a Sequence With Its Costume

```
sequence:   a₀    a₁    a₂    a₃    a₄     ...
             |     |     |     |      |
series:    a₀ + a₁x + a₂x² + a₃x³ + a₄x⁴ + ...

Fibonacci (a₀=1, a₁=1):  1 + x + 2x² + 3x³ + 5x⁴ + 8x⁵ + ...
G(x) = 1/(1 − x − x²)
```

Reading off coefficients is the only "evaluation" that ever matters; x is a filing label, not a number.

## 2. Why Multiplication Convolution-Adds

```
   1/(1 − x⁵)  =  1 + x⁵ + x¹⁰ + x¹⁵ + x²⁰ + …        (how many 5¢ coins)
   1/(1 − x¹⁰) =  1 + x¹⁰ + x²⁰ + x³⁰ + …              (how many 10¢ coins)

   product term:  x⁵ᵃ · x¹⁰ᵇ = x^{5a + 10b}             (exponents add)
   [x²⁰] = 5 pairs (a,b) ∈ {(4,0),(2,1),(0,2)} + mixed...
```

Each factor is a menu of one coin type; the product enumerates *choices from all menus simultaneously*, and the exponent automatically totals the cents.

## 3. Extraction by Repeated Truncation (the 50¢ Build-Up)

```
after 1¢ :  ways(50) =  1
after 5¢ :  ways(50) = 11      (add every 5th slot)
after 10¢:  ways(50) = 36      (folds pairs again)
after 25¢:  ways(50) = 49
after 50¢:  ways(50) = 50
```

Each coin factor, multiplied in, "folds" the coefficient array with stride c: new f(n) = f(n) + f(n−c) — visually, sliding a copy of the array left by c and adding. Four folds → 50.

## 4. Rational GF ↔ Recurrence (Denominator as Rule)

```
    1                denominator Q = 1 − x − x²
  ─────────   ⇔   aₙ = aₙ₋₁ + aₙ₋₂
 1 − x − x²

    1 + x            numerator P adjusts the seeds
  ─────────   ⇔   same recurrence, a₀ = 1, a₁ = 2  (no-"00" strings)
 1 − x − x²
```

Picture: the denominator stores the *rule*, the numerator stores the *initial conditions*. Partial fractions then pull the rule apart into pure exponentials λᵢⁿ — the visual of "one pole per exponential mode."

## 5. Partial Fractions Decomposition (Fibonacci Example)

```
1/(1 − x − x²) = c/(1 − φx) + d/(1 − ψx),  φ = (1+√5)/2, ψ = (1−√5)/2
        ⇒  Fₙ = (φⁿ − ψⁿ)/√5
```

Two poles → two geometric series → subtraction of two exponentials. The irrational φ and ψ cancel out of the final integer — the reason Binet's formula, though real-valued, always lands on a whole number.

## 6. Lattice Path Counting via the GF of Steps

```
steps: right R ↦ x,  up U ↦ y        path ↦ monomial x^{#R} y^{#U}
all paths to (m,n):  [x^m y^n]  1/(1 − (x + y))      (any sequence of steps)

restricted (never above diagonal):  Catalan GF  C(x) = (1 − √(1 − 4x))/(2x)
                                    C(x) = 1 + x·C(x)²   (first return split)
```

The quadratic functional equation drawn as a tree (root → left subtree × right subtree) is the same shape as the recurrence Cₙ = ΣCᵢCₙ₋₁₋ᵢ — the picture and the equation are one object.
