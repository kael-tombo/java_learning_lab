# Architecture: Class File Layout

The class file is a flat big-endian struct. Every tool in this lab
(`javap -v`, the raw-byte probe, the pool-gap probe) reads the same
sequence of tables in the same order.

## Top-level order (JVMS §4.1)

```text
u4  magic                  0xCAFEBABE
u2  minor_version          0 (javac output)
u2  major_version          52/55/61/65/67 for 8/11/17/21/23
u2  constant_pool_count    entries + 1 (index 0 phantom)
cp  constant_pool[]        tags 1,3–12,15–20 (see INTERNALS.md)
u2  access_flags           ACC_PUBLIC/SUPER/FINAL/...
u2  this_class             pool index -> Class -> Utf8
u2  super_class            pool index; 0 means java.lang.Object itself
u2  interfaces_count + []  pool indices
u2  fields_count + []      field_info entries
u2  methods_count + []     method_info entries
u2  attributes_count + []  SourceFile, BootstrapMethods, NestHost, ...
```

## Method table shape

```text
method_info {
  u2 access_flags, name_index, descriptor_index;
  u2 attributes_count; attribute_info attributes[];  // Code lives here
}
Code {
  u2 max_stack, max_locals;     // probe: stack=3, locals=4
  u2 args_size (javap label);   // probe: 3 = this + 2 params
  u1 code[];                    // instruction stream
  exception_table[];            // try/catch metadata, not instructions
  LineNumberTable;              // pc -> source line
  StackMapTable;                // only if branches exist
}
```

## Pool indirection

A `Methodref` resolves in three hops: `Methodref → Class/NameAndType
→ Utf8`. A `String` entry holds no characters; it points at a `Utf8`.
Deduplication falls out of this: one name/descriptor triple stored
once, referenced from every call site.

## Attribute placement

- Per-class: `SourceFile`, `BootstrapMethods`, `NestHost`/`NestMembers`,
  `Record`, `PermittedSubclasses`, `InnerClasses`.
- Per-method: `Code` (which nests `LineNumberTable`, `StackMapTable`,
  `LocalVariableTable`).
- Per-field: `ConstantValue` (only compile-time-constant static finals),
  `Synthetic`, `Deprecated`.

## Design consequences

Fixed header first means a reader rejects garbage in 8 bytes: wrong
magic is `ClassFormatError` before any table is touched. Pool-before-
use means every later index is bounds-checkable against
`constant_pool_count`. Attributes-last means new JDK releases add
metadata (`Record` in 16, `PermittedSubclasses` in 17) without moving
any existing field.
