# History of String Handling

- **Java 1.0**: String (immutable), StringBuffer (thread-safe mutable)
- **Java 1.4**: java.util.regex (Pattern/Matcher)
- **Java 5**: StringBuilder (non-thread-safe mutable, faster), String.format
- **Java 7**: Strings in switch, named regex groups
- **Java 8**: StringJoiner, Collectors.joining()
- **Java 11**: String.repeat(), isBlank(), lines(), strip(), stripLeading(), stripTrailing()
- **Java 12**: String.indent(), transform()
- **Java 13-14**: Text Blocks (preview)
- **Java 15**: Text Blocks (finalized)
- **Java 21**: String templates (preview)
- **Java 23**: String templates withdrawn — the experts group declined to continue the preview after two rounds (JEP 430/459); no shipping JDK has them, so `String.formatted` and text blocks remain the tools for interpolation

The trend shows continuous improvement in string processing for modern text-heavy workloads.
