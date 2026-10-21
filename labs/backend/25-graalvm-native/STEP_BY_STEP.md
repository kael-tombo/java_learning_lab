# Step by Step: GraalVM Native

## Step 1: Add Plugin
`xml
<plugin>
    <groupId>org.graalvm.buildtools</groupId>
    <artifactId>native-maven-plugin</artifactId>
</plugin>
`

## Step 2: Build Native Image
`ash
mvn -Pnative native:compile
`

## Step 3: Run Native Image
`ash
./target/backend25-application
`

## Step 4: Reflection Config
`json
{
    "name": "com.learning.backend25.model.MyClass",
    "methods": [
        {"name": "getValue", "parameterTypes": []},
        {"name": "setValue", "parameterTypes": ["java.lang.String"]}
    ]
}
`

## Step 5: Resource Config
`json
{
    "resources": {
        "includes": [
            {"pattern": "\\Qmessages.properties\\E"},
            {"pattern": "messages_.*\\.properties"}
        ]
    }
}
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\25-graalvm-native "CODE_DEEP_DIVE.md") @"
# Code Deep Dive: GraalVM Native

## Spring Boot AOT Engine

The AOT engine runs at build time:
1. Analyzes @SpringBootApplication configuration
2. Resolves all bean definitions
3. Evaluates @Conditional annotations
4. Generates runtime initialization code
5. Creates native-image.properties and reflection config

## Native Image Building Process

1. Points-to analysis (static analysis of reachable code)
2. Heap snapshotting (pre-initialize constant objects)
3. AOT compilation (compile to machine code)
4. Image writing (create standalone executable)

## Reflection Registration

Spring AOT generates reflection config for:
- All beans and configuration classes
- @Autowired constructors/fields/methods
- @Value annotation processing
- Jackson serialization types
- Hibernate entity classes
- AOP proxied classes
