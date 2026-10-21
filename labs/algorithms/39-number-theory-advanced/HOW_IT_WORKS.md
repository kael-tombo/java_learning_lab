# How It Works
Pollard's Rho: generate pseudorandom sequence x_i = f(x_{i-1}) mod n. Use Floyd's cycle detection comparing x_i and x_2i. Compute gcd(|x_i - x_2i|, n). If > 1 and < n, found factor. Elliptic curve: points satisfy y^2 = x^3 + ax + b (mod p). Addition: draw line through two points, find third intersection, reflect across x-axis.
