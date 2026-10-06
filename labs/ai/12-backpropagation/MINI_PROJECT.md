# Backpropagation - MINI PROJECT

## Project: Automatic Differentiation Engine

Build an automatic differentiation engine for computing gradients.

### Implementation

```java
public class Value {
    public double data;
    public double grad;
    public List<Value> children;
    public String op;
    
    public Value(double data) {
        this.data = data;
        this.grad = 0;
        this.children = new ArrayList<>();
    }
    
    public Value add(Value other) {
        Value out = new Value(this.data + other.data);
        out.children = List.of(this, other);
        out.op = "+";
        return out;
    }
    
    public Value multiply(Value other) {
        Value out = new Value(this.data * other.data);
        out.children = List.of(this, other);
        out.op = "*";
        return out;
    }
    
    public void backward() {
        // Topological sort
        List<Value> topo = new ArrayList<>();
        Set<Value> visited = new HashSet<>();
        buildTopo(this, visited, topo);
        
        // Reverse topological order
        this.grad = 1.0;
        Collections.reverse(topo);
        for (Value v : topo) {
            if (v.op.equals("+")) {
                v.children.get(0).grad += v.grad;
                v.children.get(1).grad += v.grad;
            } else if (v.op.equals("*")) {
                v.children.get(0).grad += v.children.get(1).data * v.grad;
                v.children.get(1).grad += v.children.get(0).data * v.grad;
            }
        }
    }
}
```

### Test It

```java
@Test
public void testAutograd() {
    Value a = new Value(2.0);
    Value b = new Value(3.0);
    Value c = a.multiply(b);
    c.backward();
    assertEquals(3.0, a.grad, 0.001);
    assertEquals(2.0, b.grad, 0.001);
}
```

## Deliverables

- [ ] Computational graph construction
- [ ] Forward pass evaluation
- [ ] Backward pass gradient computation
- [ ] Support for add, multiply, tanh, relu, exp
- [ ] Gradient checking utility
