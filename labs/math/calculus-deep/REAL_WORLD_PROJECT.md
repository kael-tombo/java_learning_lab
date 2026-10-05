# Real-World Project: Physics Simulation Engine

## Overview
Build a 2D physics engine that simulates projectile motion, orbital mechanics, and spring systems using numerical calculus. This mirrors what game engines and scientific simulators do.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- NASA Orbital Mechanics: https://www.grc.nasa.gov/www/k-12/rocket/shortr.html
- Open Source Physics (OSP) Project: https://www.compadre.org/osp/

## Project Goals
1. Simulate projectile motion with air resistance
2. Model orbital mechanics (two-body problem)
3. Implement spring-mass-damper systems
4. Visualize trajectories in real-time

## Physics Background

### Projectile Motion with Drag
Without air resistance: x(t) = v₀cos(θ)·t, y(t) = v₀sin(θ)·t - ½gt²

With quadratic drag: F_d = -½ρC_dA|v|v, requiring numerical integration:
- dv_x/dt = -(k/m)·v·v_x
- dv_y/dt = -g - (k/m)·v·v_y

### Orbital Mechanics
Newton's law of gravitation: F = GMm/r²
Equations of motion:
- d²x/dt² = -GMx/r³
- d²y/dt² = -GMy/r³

### Spring-Mass-Damper
m·d²x/dt² + c·dx/dt + k·x = F(t)
State-space form: dx/dt = v, dv/dt = (F - cv - kx)/m

## Implementation Plan

### Phase 1: Core Integrator
Implement Runge-Kutta 4th order (RK4) for accuracy:
```python
def rk4(f, y0, t_span, dt):
    """Solve dy/dt = f(t, y) with RK4."""
    t, y = t_span[0], y0
    trajectory = [(t, y.copy())]
    while t < t_span[1]:
        k1 = f(t, y)
        k2 = f(t + dt/2, y + dt*k1/2)
        k3 = f(t + dt/2, y + dt*k2/2)
        k4 = f(t + dt, y + dt*k3)
        y = y + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)
        t += dt
        trajectory.append((t, y.copy()))
    return trajectory
```

### Phase 2: Projectile Simulator
- Input: initial velocity, angle, drag coefficient
- Output: trajectory, max height, range, flight time
- Compare with analytical (no-drag) solution

### Phase 3: Orbital Simulator
- Input: initial position, velocity, central mass
- Output: orbit trajectory, period, apogee/perigee
- Verify conservation of energy and angular momentum

### Phase 4: Spring System
- Input: mass, spring constant, damping, initial displacement
- Output: displacement over time, natural frequency, damping ratio
- Classify: underdamped, critically damped, overdamped

### Phase 5: Visualization
Use matplotlib to animate trajectories in real-time.

## Validation
- Projectile: range without drag matches v₀²sin(2θ)/g
- Orbit: circular orbit has constant speed; elliptical orbits conserve energy
- Spring: undamped system conserves total energy

## Extensions
- N-body gravitational simulation
- Collision detection and response
- Wind effects on projectiles
- Variable gravity with altitude

## Deliverables
- `physics_engine.py` — core simulation library
- `projectile.py` — projectile motion demo
- `orbital.py` — orbital mechanics demo
- `spring.py` — spring system demo
- `visualization.py` — animated plots
- `README.md` — theory, usage, and results
