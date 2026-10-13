# Visual Guide: Class File Format

## Byte map (offsets, probe values for --release 17)

```text
offset  0  1  2  3  4  5  6  7  8  9  10 ...
bytes  CA FE BA BE 00 00 00 3D .. .. | pool entries ...
       |<-- magic -->|<-minor->|<-major->|<-count->|
       always CAFEBABE  0         61=17    N+1
```

## Pool with a wide-entry hole

```text
 #11 = Utf8            "BIG"
 #12 = Long            0x1122334455667788
 #13 = (dead slot — second half of Long, never printed)
 #14 = Utf8            "SMALL"
 #15 = Integer         42
 #16 = Double          3.14159...
 #17 = (dead slot)
 #18 = String -> #19   (characters live in Utf8 #19)
```

Rule: after tag 5/6, the counter jumps 2, not 1.

## Methodref resolution (3 hops)

```text
#31 = Methodref
       |---> #20 = Class  ---> #21 = Utf8 "java/lang/Object"
       |---> #30 = NameAndType
                    |---> #22 = Utf8 "<init>"
                    +---> #23 = Utf8 "()V"
```

## Code header vs locals (probe absOrNeg (IZ)I)

```text
stack=3, locals=4, args_size=3
locals: [0:this][1:x:int][2:neg:boolean][3:y:int]
              |<--- args_size=3 --->|
                                     |<- method local
stack depth over time: 0 -> 1 -> 2 -> 1 -> ... (max 3)
```

## StackMapTable placement

```text
straight:  iload_1; iconst_2; imul; iconst_1; iadd; ireturn
           (no jumps)  -->  NO StackMapTable

branchy:   iload_1; ifge L1; iload_1; ineg; goto L2
           L1: iload_1
           L2: ireturn     [* frame at L1, frame at L2 *]
```

## Attribute tree

```text
ClassFile
 +-- SourceFile, BootstrapMethods, NestHost, Record, ...
 +-- fields[]  (+ ConstantValue on static finals)
 +-- methods[]
       +-- Code
            +-- code[] (instructions)
            +-- exception_table[] (ranges, not opcodes)
            +-- LineNumberTable (pc -> line)
            +-- StackMapTable (frames at merges only)
```
