# Calculus Flashcards

## Limits
| Front | Back |
|-------|------|
| lim(x→a) f(x) = L means | f(x) gets arbitrarily close to L as x approaches a |
| lim(x→0) sin(x)/x | 1 |
| lim(x→∞) (1+1/x)^x | e |
| L'Hôpital's Rule | lim f/g = lim f'/g' for 0/0 or ∞/∞ |
| Indeterminate form 0/0 | Apply L'Hôpital or algebraic manipulation |
| One-sided limit | Limit approaching from left or right only |
| Continuity at a point | lim(x→a) f(x) = f(a) |
| Squeeze theorem | If g ≤ f ≤ h and g,h → L, then f → L |

## Derivatives
| Front | Back |
|-------|------|
| f'(x) definition | lim(h→0) [f(x+h)-f(x)]/h |
| Power rule | d/dx[x^n] = n·x^(n-1) |
| Product rule | (fg)' = f'g + fg' |
| Quotient rule | (f/g)' = (f'g - fg')/g² |
| Chain rule | d/dx[f(g(x))] = f'(g(x))·g'(x) |
| d/dx[sin x] | cos x |
| d/dx[cos x] | -sin x |
| d/dx[e^x] | e^x |
| d/dx[ln x] | 1/x |
| Critical point | Where f'(x) = 0 or f'(x) undefined |
| Local maximum | f' changes from + to - |
| Inflection point | Where concavity changes |

## Integrals
| Front | Back |
|-------|------|
| ∫f(x)dx | Antiderivative F(x) + C |
| Fundamental Theorem | ∫[a,b] f(x)dx = F(b) - F(a) |
| ∫x^n dx | x^(n+1)/(n+1) + C (n ≠ -1) |
| ∫(1/x)dx | ln|x| + C |
| ∫e^x dx | e^x + C |
| ∫sin(x)dx | -cos(x) + C |
| ∫cos(x)dx | sin(x) + C |
| Substitution method | ∫f(g(x))g'(x)dx = ∫f(u)du |
| Integration by parts | ∫u dv = uv - ∫v du |
| Definite integral | Net signed area under curve |

## Series
| Front | Back |
|-------|------|
| Geometric series sum | a/(1-r) when |r| < 1 |
| p-series Σ1/n^p | Converges iff p > 1 |
| Ratio test | lim|a_(n+1)/a_n| < 1 → converges |
| Alternating series test | Decreasing terms → 0 implies convergence |
| Taylor series | f(x) = Σ f^(n)(a)/n! ·(x-a)^n |
| Maclaurin series | Taylor series centered at a = 0 |
| e^x series | Σ x^n/n! for all x |
| sin x series | Σ (-1)^n x^(2n+1)/(2n+1)! |
| Radius of convergence | Distance from center where series converges |

## Applications
| Front | Back |
|-------|------|
| Velocity | Derivative of position: v = ds/dt |
| Acceleration | Derivative of velocity: a = dv/dt |
| Optimization | Find critical points, test endpoints |
| Related rates | Differentiate both sides w.r.t. time |
| Disk method volume | V = π∫[f(x)]²dx |
| Arc length | ∫√(1 + [f'(x)]²)dx |
| Work (variable force) | W = ∫F(x)dx |
| Average value of f | (1/(b-a))∫[a,b] f(x)dx |
