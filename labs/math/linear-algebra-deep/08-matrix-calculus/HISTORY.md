# History: Matrix Calculus

## Statistics first (1940s)
Systematic formulas for differentiating with respect to vectors and
matrices appeared in the statistics literature of the 1940s, notably
Dwyer and MacPhail's 1948 paper on symbolic matrix derivatives,
driven by likelihood estimation. The trace identities and the rule
d(Ax)/dx = A in this lab come straight from that line.

## Control and econometrics (1960s-1970s)
Optimal control and simultaneous-equation models needed gradients of
quadratic forms and traces routinely. Textbooks of estimation theory
in the 1960s and 1970s standardized results like the derivative of
x^T A x and the cyclic property of the trace under differentiation.

## Automatic differentiation (1970-1974)
Seppo Linnainmaa introduced the reverse mode of automatic
differentiation in his 1970 master's thesis; Paul Werbos described its
use for neural networks in his 1974 dissertation. The field then slept
until hardware caught up.

## Textbook consolidation (1980s)
Jan Magnus and Heinz Neudecker's Matrix Differential Calculus,
published in the 1980s, gave the subject its reference text: differentials
first, identifications second, layout conventions stated explicitly.
The numerator-versus-denominator layout split this lab warns about
dates from this textbook era.

## Backpropagation (1986)
Rumelhart, Hinton, and Williams' 1986 Nature papers made one matrix
calculus computation, the gradient of a layered composition, the most
evaluated derivative in history. Every deep-learning framework since
is a matrix-calculus engine with an optimizer attached.

## What this lab inherits
The numeric instance f = 27 with gradient (12, 21) at (1, 2) and the
trace check 21 = 21 rehearse the 1948 formulas inside the 1980s
notation, the combination every practitioner actually uses.
