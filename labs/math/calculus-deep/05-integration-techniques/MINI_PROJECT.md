# MINI_PROJECT — Integration Techniques: Technique Picker
> Implement + pick + integrate. ~2 hours.

## Goal
Build a CLI that classifies an integral by pattern (parts, trig sub, partial fractions,
u-sub, numeric-only) and computes it symbolically where elementary, otherwise numerically.

## Build Steps
1. `Pattern.java`: regex/AST match of a small set of forms.
2. `Parts.java`, `TrigSub.java`, `PartialFractions.java` solvers for textbook forms.
3. `Numeric.java`: Simpson fallback with error table.
4. Driver: 10 integrals; print chosen technique + result.

## Acceptance
- [ ] Each technique exercised ≥2 times.
- [ ] Non-elementary integrals fall back to numeric with a note.

## Extensions
- Definite vs indefinite distinction in output.
