# Mini Project: Symbolic Derivative Calculator

## Goal
Build a command-line tool that parses mathematical expressions and computes their derivatives symbolically.

## Requirements
1. Parse expressions like `3*x^2 + sin(x) - 5`
2. Support operators: +, -, *, /, ^
3. Support functions: sin, cos, exp, ln
4. Apply differentiation rules: power, product, quotient, chain
5. Output the simplified derivative expression

## Architecture
```
Input string → Tokenizer → Parser (AST) → Differentiator → Simplifier → Output
```

## Step 1: Tokenizer
Break input into tokens: numbers, variables, operators, functions, parentheses.

```python
import re

def tokenize(expr):
    pattern = r'\d+\.?\d*|[a-zA-Z]+|[+\-*/^()]'
    return re.findall(pattern, expr.replace(' ', ''))
```

## Step 2: Parser (Recursive Descent)
Build an Abstract Syntax Tree (AST) respecting precedence:
- Level 1: +, -
- Level 2: *, /
- Level 3: ^ (right-associative)
- Level 4: unary -, functions, atoms

```python
class Node:
    def __init__(self, type, value=None, children=None):
        self.type = type  # 'num', 'var', 'op', 'func'
        self.value = value
        self.children = children or []
```

## Step 3: Differentiator
Recursively apply rules:
- Constant → 0
- Variable → 1
- Sum → sum of derivatives
- Product → product rule
- Power → power rule (with chain rule for variable exponent)
- sin(u) → cos(u)·u'
- exp(u) → exp(u)·u'
- ln(u) → u'/u

## Step 4: Simplifier
Apply algebraic identities:
- 0 + x → x
- 1 * x → x
- 0 * x → 0
- x^1 → x
- x^0 → 1
- Combine numeric constants

## Step 5: Output
Convert AST back to string with minimal parentheses.

## Testing
```python
tests = [
    ("x^2", "2*x"),
    ("3*x^2 + 2*x + 1", "6*x + 2"),
    ("sin(x)", "cos(x)"),
    ("x*sin(x)", "sin(x) + x*cos(x)"),
    ("exp(2*x)", "2*exp(2*x)"),
]
```

## Extensions
- Partial derivatives for multivariable expressions
- LaTeX output for pretty printing
- Numerical evaluation at a point
- Integration (much harder — Risch algorithm)

## Deliverables
- `differentiator.py` — main module
- `test_differentiator.py` — unit tests
- `README.md` — usage examples
