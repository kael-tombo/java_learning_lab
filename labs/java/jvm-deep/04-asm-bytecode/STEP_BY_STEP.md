# Step by Step: Bytecode Generation

Requires JDK 23. Every command carries the preview rig.

## Step 1 — Parse your own class

```bash
mkdir -p /tmp/asm && cd /tmp/asm
cat > ParseOwn.java <<'EOF'
import java.lang.classfile.ClassFile;
import java.lang.classfile.ClassModel;
public class ParseOwn {
    public static void main(String[] args) throws Exception {
        byte[] bytes;
        try (var in = ParseOwn.class.getResourceAsStream("/ParseOwn.class")) {
            bytes = in.readAllBytes();
        }
        ClassModel model = ClassFile.of().parse(bytes);
        System.out.println("this class = " + model.thisClass().asInternalName());
        System.out.println("major version = " + model.majorVersion());
        for (var m : model.methods()) System.out.println("method: " + m.methodName().stringValue());
    }
}
EOF
javac --release 23 --enable-preview ParseOwn.java
java --enable-preview ParseOwn
```

Expect `ParseOwn`, a major ≥ 65, methods `[<init>, main]`.

## Step 2 — Generate add and run it

Write `GenerateAdd` (CODE_DEEP_DIVE snippet 2): `build` with
`withMethod("add", MethodTypeDesc.of(CD_int, CD_int, CD_int),
ACC_PUBLIC | ACC_STATIC, iload/iload/iadd/ireturn)`, check magic,
`defineClass`, `findStatic`, `invokeExact(40, 2)`.

Expect `Gen.add(40, 2) = 42`, `generated code runs: true`.

## Step 3 — Drop a method by withholding

Write `DropMethod` (snippet 3) against its own bytes. List methods
before and after; confirm `main` gone, `<init>` kept, output smaller.
Note the `lambda$` filter — your transform lambda left a synthetic
footprint in the class under inspection.

## Step 4 — Branch with labels

Write `GenerateMax` (snippet 4): `newLabel`, `if_icmpge`,
`labelBinding`, two `ireturn`s. `invokeExact(3, 7)` → 7,
`invokeExact(9, 2)` → 9. No `max_stack` math, no frame code — state
which lines the builder derived them from.

## Step 5 — Close the triangle with raw bytes

Write `VersionRoundTrip` (snippet 5): compile `V17` with
`--release 17`, parse, compare `model.majorVersion()` against bytes
6–7. Expect 61 both ways. You now trust parse, build, and raw reads
against each other — the full lab in one agreement.
