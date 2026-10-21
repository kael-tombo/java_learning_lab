# Kryo Serialization -- Quiz

## Question 1: Fundamentals
What is the primary purpose of serialization?
A) Object persistence  B) Network communication  C) Both A and B  D) Memory management

## Question 2: Interface
Which interface must a class implement to be eligible for serialization?

## Question 3: Keywords
Which keyword prevents a field from being serialized?

## Question 4: Identifier
What is the purpose of serialVersionUID?

## Question 5: Customization
Which methods can be implemented to customize serialization behavior?

## Question 6: Security
What security risks are associated with deserialization of untrusted data?

## Question 7: Performance
Why is Java serialization generally slower than alternative serialization frameworks?

## Question 8: Inheritance
If a parent class implements Serializable, are its subclasses automatically serializable?

## Question 9: Circular References
How does Java serialization handle circular object references?

## Question 10: Singleton
How can a singleton's invariant be preserved during deserialization?

## Question 11: Externalizable
How does Externalizable differ from Serializable in terms of control?

## Question 12: Proxy Pattern
Explain the Serialization Proxy pattern and its security benefits.

## Question 13: Constructors
Does deserialization call constructors? If not, how are objects created?

## Question 14: Stream Format
What is the magic number and version of the Java serialization stream protocol?

## Question 15: Filters
How can ObjectInputFilter be used to secure deserialization?

## Question 16: Compatibility
What happens if serialVersionUID differs between serialization and deserialization?

## Question 17: Transient
What is the initial value of a transient Object reference after deserialization?

## Question 18: writeReplace
When during the serialization process is writeReplace() invoked?

## Question 19: readResolve
When during deserialization is readResolve() invoked?

## Question 20: Best Practice
What is the recommended access modifier and type for serialVersionUID?

## Answer Key
1-C, 2-Serializable, 3-transient, 4-Version control, 5-writeObject/readObject/readResolve/writeReplace, 6-RCE via gadget chains, 7-Reflection overhead, 8-Yes, 9-Handle table, 10-readResolve, 11-Full control vs automatic, 12-Replace object with proxy, 13-No, uses Unsafe.allocateInstance, 14-0xACED 0x0005, 15-Filter allowed classes, 16-InvalidClassException, 17-null, 18-Before serialization, 19-After deserialization, 20-private static final long
