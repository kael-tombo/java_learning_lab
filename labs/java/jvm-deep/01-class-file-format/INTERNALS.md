# Internals: Class File Format

## Header field widths (all big-endian)

```text
magic                 u4   bytes 0-3, always 0xCAFEBABE
minor_version         u2   bytes 4-5, 0 from javac
major_version         u2   bytes 6-7, 52/55/61/65/67 measured
constant_pool_count   u2   bytes 8-9, entries + 1
```

Multibyte integers are unsigned and big-endian: major 61 reads as
`00 3D`. The raw-byte probe reconstructs each field with shifts and
masks (`(b[6] & 0xFF) << 8 | (b[7] & 0xFF)`).

## Pool tags met in this lab

```text
1  Utf8               length + modified-UTF-8 bytes
3  Integer            4-byte constant
4  Float              4-byte constant
5  Long               8 bytes, TWO slots
6  Double             8 bytes, TWO slots
7  Class              index -> Utf8 (binary name)
8  String             index -> Utf8 (characters)
9  Fieldref           Class + NameAndType
10 Methodref           Class + NameAndType
11 InterfaceMethodref  Class + NameAndType
12 NameAndType         name Utf8 + descriptor Utf8
15 MethodHandle        kind + reference index
16 MethodType          descriptor Utf8
17 Dynamic             bootstrap + NameAndType
18 InvokeDynamic       bootstrap + NameAndType
19 Module              Utf8
20 Package             Utf8
```

Tags 2, 13, 14 are unassigned. `javap -v` prints each entry with its
index; gaps after tags 5/6 are the double-slot holes.

## access_flags bits (abridged)

`0x0001` PUBLIC, `0x0010` FINAL, `0x0020` SUPER (classes; always set
by modern javac), `0x0200` INTERFACE, `0x0400` ABSTRACT, `0x1000`
SYNTHETIC, `0x4000` ENUM, `0x8000` MODULE. Method flags add `0x0008`
STATIC, `0x0100` NATIVE, `0x0400` ABSTRACT, `0x0800` STRICT.

## Code attribute internals

```text
max_stack   u2   deepest operand stack (probe: 3)
max_locals  u2   local slots incl. receiver+params (probe: 4)
code_length u4   length of code[]
code[]      u1[] instruction stream
exception_table_length u2 + rows {start_pc, end_pc, handler_pc, catch_type}
attributes: LineNumberTable {start_pc -> line}, StackMapTable {frames}
```

`args_size` is a `javap` label, not a stored field: it counts the
receiver plus parameters (probe: this + int + boolean = 3). The extra
local (`y`) explains locals(4) > args_size(3).

## Attribute name table

`ConstantValue` (constant field init), `Code`, `StackMapTable`,
`BootstrapMethods`, `LineNumberTable`, `LocalVariableTable`,
`SourceFile`, `NestHost`/`NestMembers`, `Record`,
`PermittedSubclasses`, `InnerClasses`, `Synthetic`, `Deprecated`.
Every attribute is `{name_index (Utf8), length u4, info[]}` — unknown
attributes can be skipped by length, which is how old JVMs tolerate
selected newer metadata (but never newer majors).
