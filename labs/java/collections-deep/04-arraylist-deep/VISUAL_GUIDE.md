# Visual Guide: ArrayList

## Store layout
```
elementData (Object[], contiguous)     size = 4
+---+---+---+---+---+---+---+---+
| a | b | c | d |null|...       |   [0..size) live, [size..len) null
+---+---+---+---+---+---+---+---+
get(2): one indexed load -> c      set(2,z): one store, NO modCount++
```

## Growth 1.5x (10 -> 15 -> 22)
```
[10 full] --add--> grow: newLength(10, 1, 10>>1=5) = 15, copyOf moves 10
[15: 11 live, 4 slack] --fill+add--> newLength(15, 1, 7) = 22, moves 15
total for n appends ~= 3n moves; presized = n moves
```

## remove(0): shift + null
```
before: [a][b][c][d] size=4
shift:  [b][c][d][d] (arraycopy 3 words left)
clear:  [b][c][d][null] size=3   <- fastRemove nulls the slot (no leak)
```

## Lazy sentinels
```
new ArrayList<>()  -> DEFAULTCAPACITY_EMPTY_ELEMENTDATA -> first add: 10
new ArrayList<>(0) -> EMPTY_ELEMENTDATA                 -> grows exact-fit
```

## SubList view
```
subList(1,3) ---- window on the SAME array (live, fail-fast, CME on drift)
mutate via view -> writes backing array; structural parent change -> CME
```
