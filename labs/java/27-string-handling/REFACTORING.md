# Refactoring: String Handling

## Pattern 1: StringBuilder Pre-sizing

### Before
```java
StringBuilder sb = new StringBuilder();
for (String s : list) {
    sb.append(s).append(",");
}
```

### After
```java
int estimated = list.size() * 10;  // Average string length
StringBuilder sb = new StringBuilder(estimated);
for (String s : list) {
    sb.append(s).append(",");
}
```

## Pattern 2: Replace String.format() with StringBuilder

### Before
```java
String result = String.format("User: %s, Age: %d, Email: %s", name, age, email);
```

### After
```java
String result = new StringBuilder()
    .append("User: ").append(name)
    .append(", Age: ").append(age)
    .append(", Email: ").append(email)
    .toString();
```

## Pattern 3: Reuse StringBuilder

### Before
```java
public String process(List<String> items) {
    String result = "";
    for (String item : items) {
        result += item.toUpperCase() + "-";
    }
    return result;
}
```

### After
```java
public String process(List<String> items) {
    StringBuilder sb = new StringBuilder(items.size() * 16);
    for (String item : items) {
        sb.append(item.toUpperCase()).append('-');
    }
    return sb.toString();
}
```

## Pattern 4: Use String.join()

### Before
```java
StringBuilder sb = new StringBuilder();
for (int i = 0; i < items.size(); i++) {
    if (i > 0) sb.append(", ");
    sb.append(items.get(i));
}
```

### After
```java
String result = String.join(", ", items);
```

## Pattern 5: Avoid toString() Chaining

### Before
```java
return "Value: " + obj.toString() + " (" + obj.hashCode() + ")";
```
### After (Java 15+)
```java
// "Value: %s (%d)".formatted(obj, obj.hashCode()) — the withdrawn JDK 21/22
// string-templates preview would have spelled this STR."Value: \{obj} (\{obj.hashCode()})"
return "Value: %s (%d)".formatted(obj, obj.hashCode());
```
Or use StringBuilder for older versions.
