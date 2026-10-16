# Vector Calculus -- Math Foundation

All values computed in Python; observed outputs pasted.

## 1. Divergence and Curl, Evaluated at Points

F(x,y,z) = (x^2, y^2, z^2): div F = 2x + 2y + 2z; at (1,2,3):
2 + 4 + 6 = 12 (observed). curl F: Ry - Qz = 0 - 0 = 0 and likewise
for all three components, so curl F = (0,0,0) everywhere -- symmetric
pure-stretch fields do not rotate. G(x,y,z) = (-y, x, 0): div G =
0 + 0 + 0 = 0; curl G = (0 - 0, 0 - 0, 1 + 1) = (0, 0, 2) (observed):
pure rotation with uniform vorticity 2 and no net outflow.

## 2. Line Integral Along r(t) = (t, t^2)

F(x,y) = (y, x), 0 <= t <= 1: F(r(t)) = (t^2, t), r'(t) = (1, 2t),
dot product t^2 + 2t^2 = 3t^2. int_0^1 3t^2 dt = 1 exactly. Midpoint
Riemann sum with n = 100000 gives 0.9999999999750026 (observed).
Straight-line path from (0,0) to (1,1) instead: r(t) = (t, t),
F . r' = t + t = 2t, integral 1 as well -- same value, hinting the
field structure; note F = grad(xy), so path-independence is exact.

## 3. Conservative Field, Two Paths

F(x,y) = (2x, 2y) = grad(x^2 + y^2), potential phi = x^2 + y^2.
Path A (axes): (0,0) -> (1,0) -> (1,1): int = int_0^1 2x dx + int_0^1
2y dy = 1 + 1 = 2. Path B (diagonal): r(t) = (t,t): F . r' = 4t,
int_0^1 4t dt = 2. Both give 2 = phi(1,1) - phi(0,0) (observed).
curl check: Qx - Py = 0 - 0 = 0, consistent with conservativeness.

## 4. Green's Theorem on the Unit Disk

Circulation of F = (-y, x) around the unit circle r(t) = (cos t,
sin t): F(r) . r' = (-sin t)(-sin t) + (cos t)(cos t) = 1, so int_0^{2pi}
1 dt = 2 pi = 6.283185307179586 (observed). Green side: Qx - Py =
1 - (-1) = 2 over the disk of area pi: 2 pi (observed product).
Boundary and interior computations agree.

## 5. Flux via Divergence Theorem (Sphere Check)

F(x,y,z) = (x, y, z), div F = 3. Over the unit ball (volume 4 pi/3 =
4.1887902047863905, observed): flux = 3 * 4 pi/3 = 4 pi =
12.566370614359172 (observed). Direct surface check: on |r| = 1,
F . n = 1, times area 4 pi gives 4 pi. Interior and surface agree.
