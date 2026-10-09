# XML Serialization — Mathematical Foundation

## 1. XML Document Structure Mathematics

### Document Size Breakdown
XML document size = Header + RootElement + Σ(ChildElements) + ClosingRoot
- XML declaration: <?xml version=""1.0"" encoding=""UTF-8""?> (~40 bytes)
- Each element: <tagName>content</tagName> (2*tagName + 3 + content bytes)
- Each attribute: attributeName=""value"" (attrName + value + 3 bytes)

### Nested Element Overhead
For an element with N levels of nesting:
- Total tag overhead per leaf: 2 * Σ(tagName_i for i=1 to N) + 3*N
- Example: 3 levels deep with 5-byte tag names = 2*15 + 9 = 39 bytes overhead

## 2. XML Schema Math

### Type Derivation Cost
Complex types with inheritance:
- Base type fields: included in all subtypes
- Extension adds base fields + new fields
- Restriction reduces allowed values but does not affect serialization size

### Namespace Resolution
- xmlns:prefix=""URI"" adds ~20-50 bytes per namespace
- Prefixed elements: prefix:tagName replaces tagName
- Default namespace: xmlns=""URI"" does not add per-element overhead

## 3. JAXB Marshalling Complexity

### Reflection Overhead
JAXB uses reflection to access fields:
- Field lookup: O(1) per field (cached after first access)
- Type conversion: varies by type (string: O(1), date: O(n), custom: depends)
- Annotation processing: O(1) per annotation (cached by JAXBContext)

### Marshal/Unmarshal Time
- Marshalling: O(n) where n is XML output size
- Unmarshalling: O(n) for SAX/StAX parsing
- DOM: O(n) for building and O(n) for traversing (2x memory)

## 4. Namespace Mathematics

### QName Resolution
QName = NamespaceURI + "":" + LocalPart
- Fully qualified name is always unique within a document
- Prefix provides shorthand; actual comparison uses NamespaceURI

### Namespace Context Stack
During serialization, namespace mappings maintain a stack:
- Push on start element with new prefixes
- Pop on end element
- Lookup is O(depth) worst case, optimized with prefix cache

## 5. Encoding Impact

### UTF-8 vs UTF-16
- ASCII characters: UTF-8 (1 byte) vs UTF-16 (2 bytes)
- CJK characters: UTF-8 (3 bytes) vs UTF-16 (2 bytes)
- XML declaration specifies encoding

## Summary
XML serialization mathematics involve document structure overhead, namespace resolution, and encoding considerations that impact both size and processing time.
