# Interview Questions: XML Serialization

## Company-Specific Focus

### Google
- JAXB (Java Architecture for XML Binding): standard API for XML serialization
- @XmlRootElement, @XmlElement, @XmlAttribute: mapping annotations
- Marshalling: Java -> XML, Unmarshalling: XML -> Java

### Microsoft
- JAXB vs .NET XmlSerializer
- SAX vs DOM vs StAX: different XML parsing approaches

### Amazon
- XML configuration: legacy systems use XML for configuration
- XML in SOAP services: still used in enterprise integration
- StAX: streaming XML parsing (cursor-based and event-based)

### Meta
- JAXB limitations: no support for immutable objects
- XML vulnerabilities: XXE (XML External Entity) attacks
- Security: disable DTD processing to prevent XXE

### Apple
- SAX: event-driven, forward-only XML parsing
- DOM: builds an in-memory tree, higher memory usage
- StAX: pull-based streaming parsing

### Oracle
- JAXB: standard for XML binding in Java EE
- javax.xml.bind: package containing JAXB API
- XML Schemas: generating Java classes from XSD
- JAXB vs DOM/SAX/StAX: different abstraction levels

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — XML serialization is enterprise-focused) |

## Real Production Scenarios
- **LinkedIn**: XXE vulnerability in XML parsing of partner feeds — disabled DTD processing
- **Uber**: JAXB for XML configuration files — migrated to JSON/YAML for simpler processing

## Interview Patterns & Tips
- **Marshalling**: Java object to XML
- **Unmarshalling**: XML to Java object
- **XXE attack**: always disable DTD processing
- **DOM vs SAX**: DOM for small documents, SAX for large documents

## Deep Dive Questions
- **JAXB annotations**: What are the key annotations for XML mapping?
- **Marshalling**: How does JAXB marshal a Java object to XML?
- **SAX vs DOM vs StAX**: What are the differences?
- **XML Schema**: How are Java classes generated from XSD?
- **XXE prevention**: How to protect against XML External Entity attacks?