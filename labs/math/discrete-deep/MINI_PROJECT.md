# Mini Project: Truth Table Generator

## Goal
Build a tool that takes a logical expression as input and generates its complete truth table, including intermediate sub-expression columns.

## Requirements
1. Parse expressions with variables (P, Q, R, ...), operators (∧, ∨, ¬, →, ↔), and parentheses
2. Generate all 2^n truth assignments for n variables
3. Evaluate the expression for each assignment
4. Display a formatted truth table with intermediate steps
5. Classify the expression: tautology, contradiction, or contingent

## Architecture
```
Input string → Tokenizer → Parser (AST) → Evaluator → Table Formatter → Output
```

## Step 1: Tokenizer
```python
import re

def tokenize(expr):
    pattern = r'[A-Za-z]+|[∧∨¬→↔()]|&&|\|\||!'
    tokens = re.findall(pattern, expr.replace(' ', ''))
    return tokens
```

## Step 2: Parser (Recursive Descent)
Precedence levels:
- Level 1: ↔ (lowest)
- Level 2: →
- Level 3: ∨
- Level 4: ∧
- Level 5: ¬ (unary, highest)

```python
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        return self.parse_biconditional()

    def parse_biconditional(self):
        left = self.parse_implication()
        while self.peek() == '↔':
            self.consume()
            right = self.parse_implication()
            left = ('biconditional', left, right)
        return left
    # ... similar for other levels
```

## Step 3: Evaluator
```python
def evaluate(ast, assignment):
    if ast[0] == 'var':
        return assignment[ast[1]]
    elif ast[0] == 'not':
        return not evaluate(ast[1], assignment)
    elif ast[0] == 'and':
        return evaluate(ast[1], assignment) and evaluate(ast[2], assignment)
    elif ast[0] == 'or':
        return evaluate(ast[1], assignment) or evaluate(ast[2], assignment)
    elif ast[0] == 'implies':
        return (not evaluate(ast[1], assignment)) or evaluate(ast[2], assignment)
    elif ast[0] == 'biconditional':
        return evaluate(ast[1], assignment) == evaluate(ast[2], assignment)
```

## Step 4: Table Generation
```python
from itertools import product

def truth_table(ast, variables):
    headers = variables + ['Result']
    rows = []
    for values in product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        result = evaluate(ast, assignment)
        rows.append(list(values) + [result])
    return headers, rows
```

## Step 5: Classification
- **Tautology:** All results True
- **Contradiction:** All results False
- **Contingent:** Mixed results

## Testing
```python
tests = [
    ("P ∨ ¬P", "tautology"),
    ("P ∧ ¬P", "contradiction"),
    ("P → Q", "contingent"),
    ("(P → Q) ↔ (¬Q → ¬P)", "tautology"),  # Contrapositive
]
```

## Extensions
- Support for ⊕ (XOR) and ↓ (NOR)
- Natural deduction proof checker
- Karnaugh map generator for simplification
- Export to LaTeX or CSV

## Deliverables
- `truth_table.py` — main module
- `test_truth_table.py` — unit tests
- `README.md` — usage examples
