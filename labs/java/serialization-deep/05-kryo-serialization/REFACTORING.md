# Kryo Serialization -- Refactoring

## Refactoring Strategies

### 1. Replace Default Serialization with Custom Serialization
Default serialization uses reflection and writes all fields. Replace with custom writeObject/readObject for better performance and control.

**Before:**
`java
public class User implements Serializable {
    private String name;
    private String password; // sensitive!
}
`

**After:**
`java
public class User implements Serializable {
    private String name;
    private transient String password;
    
    private void writeObject(ObjectOutputStream oos) throws IOException {
        oos.defaultWriteObject();
        oos.writeObject(encrypt(password));
    }
    private void readObject(ObjectInputStream ois) throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
        this.password = decrypt((String) ois.readObject());
    }
}
`

### 2. Replace Serializable with Externalizable
For full control over serialization format, replace Serializable with Externalizable.

### 3. Introduce Serialization Proxy
Replace direct serialization with the Proxy pattern for better security and decoupling.

### 4. Extract Serialization Logic
Move serialization code from domain objects to separate Serializer classes.

### 5. Add Validation
Add input validation to readObject to ensure deserialized objects are valid.

### Refactoring Patterns

#### Pattern 1: Encapsulate serialVersionUID
Move serialVersionUID to a constant and use it consistently.

#### Pattern 2: Replace Magic Numbers
Replace hardcoded serialization constants with named constants.

#### Pattern 3: Introduce Builder
Replace telescoping constructors with Builder pattern for message construction.

#### Pattern 4: Extract Adapter
Extract type conversion logic into XmlAdapter or JsonSerializer implementations.

### Testing During Refactoring
- Before refactoring: write tests that serialize/deserialize and verify
- During refactoring: run tests incrementally
- After refactoring: verify backward compatibility with old serialized data
- Performance regression: benchmark before and after
