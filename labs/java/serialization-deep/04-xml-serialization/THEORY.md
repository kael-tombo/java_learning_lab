# XML Serialization — Theoretical Foundation

## Core Concepts

### 1. Fundamental Principle
XML serialization in Java converts objects to and from XML documents. JAXB (Java Architecture for XML Binding) is the standard API that maps XML schemas to Java objects using annotations.

### 2. Theoretical Foundation
XML serialization is based on the concept of data binding — mapping XML elements and attributes to Java classes and fields. The binding is defined through annotations, XML schema, or both.

#### Key Theoretical Properties
- **Schema-Driven**: XML Schema (XSD) defines the structure, types, and constraints
- **Namespace Support**: XML namespaces prevent element name collisions
- **Validation**: XML can be validated against schemas during parsing
- **Extensibility**: XML supports mixed content, attributes, and processing instructions

### 3. Algorithmic Details

#### JAXB Marshalling (Object -> XML)
1. JAXBContext is created from annotated classes or package names
2. Marshaller is created from JAXBContext
3. Object is traversed via reflection, using @XmlRootElement, @XmlElement, @XmlAttribute
4. Java-to-XSD type mapping converts Java types to XML representations
5. Output is written to the specified destination (Stream, Writer, ContentHandler)

#### JAXB Unmarshalling (XML -> Object)
1. Unmarshaller is created from JAXBContext
2. XML input is parsed (SAX, StAX, or DOM)
3. XML elements are mapped to Java fields via annotations
4. XSD type-to-Java conversion converts text content to Java types
5. Object graph is reconstructed and returned

### 4. Trade-offs

#### JAXB vs XStream vs Jackson XML
- **JAXB**: Standard Java API, tightly coupled to XML Schema, annotation-heavy
- **XStream**: Simpler API, no schema required, supports arbitrary object graphs
- **Jackson XML**: Familiar Jackson API for XML, good performance, less mature

### 5. Mathematical Basis

#### XML Parsing Complexity
- DOM parsing: O(n) memory, O(n) time for entire document
- SAX parsing: O(1) memory, O(n) time, event-driven
- StAX parsing: O(1) memory, O(n) time, pull-based

#### XML Size Overhead
XML typically adds 200-400% overhead compared to binary formats due to:
- Opening and closing tags
- Namespace declarations
- Attribute quotes
- Indentation/whitespace

## Summary
XML serialization remains important in enterprise Java, particularly for configuration, legacy system integration, and standards-compliant data exchange.

## Key Theorems

### Theorem 1: Schema Binding
Every JAXB-annotated class corresponds to a schema type. The mapping must be consistent between the schema and annotations.

### Theorem 2: Round-Trip Fidelity
JAXB marshalling followed by unmarshalling should produce an equivalent object graph, provided the schema supports the full data representation.

### Theorem 3: Namespace Resolution
XML namespace prefixes are local to a document. JAXB uses @XmlSchema to define namespace-qualified element names.

## Key Insights

### Insight 1: JAXB Requires No-Arg Constructor
JAXB creates instances via the no-arg constructor and populates fields through setters or direct field access.

### Insight 2: XmlJavaTypeAdapter for Custom Types
Custom adapters allow mapping non-trivial types (like Date, BigDecimal) to XML string representations.

### Insight 3: Schema Generation
JAXB can generate XML Schema from annotated classes using schemagen, enabling contract-first or code-first approaches.
