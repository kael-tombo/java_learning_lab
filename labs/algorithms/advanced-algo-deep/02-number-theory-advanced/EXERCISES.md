# Exercises — Number Theory Advanced

Attempt each before reading the hint.

## Ex 1
Compute gcd(252, 105) by Euclid and show the remainder sequence.

<details><summary>Hint</summary>

252→105→42→21→0, so gcd=21.

</details>

## Ex 2
Extend Euclid to find s,t with 15s + 26t = 1.

<details><summary>Hint</summary>

26=1·15+11, 15=1·11+4, 11=2·4+3, 4=1·3+1 — back-substitute to s=7, t=-4.

</details>

## Ex 3
Compute 3^13 mod 7 by square-and-multiply.

<details><summary>Hint</summary>

3^1=3,3^2=2,3^4=4,3^8=2; 3^13=3^8·3^4·3^1=2·4·3=24≡3.

</details>

## Ex 4
Reduce 7^1000000 mod 11 using Fermat.

<details><summary>Hint</summary>

φ(11)=10; 1000000 mod 10 = 0; 7^10≡1; answer 1.

</details>

## Ex 5
Solve x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7).

<details><summary>Hint</summary>

M=105; x = 2·70·(70⁻¹ mod 3)+3·21·(21⁻¹ mod 5)+2·15·(15⁻¹ mod 7) = 23.

</details>

## Ex 6
How many Miller–Rabin rounds for error ≤ 2⁻⁴⁰?

<details><summary>Hint</summary>

4⁻ᵏ ≤ 2⁻⁴⁰ ⇒ k ≥ 20.

</details>

## Ex 7
Why can you not reduce the exponent of 4^x mod 6 using φ(6)=2?

<details><summary>Hint</summary>

gcd(4,6)=2≠1; Euler does not apply. Directly: 4^1≡4, 4^2≡4 mod 6, so 4^x≡4 for x≥1.

</details>
