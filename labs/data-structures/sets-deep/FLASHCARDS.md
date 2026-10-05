# FLASHCARDS — Sets Deep

| # | Front | Back |
|---|---|---|
| 1 | HashSet backed by? | HashMap |
| 2 | HashSet add/get bound? | O(1) avg |
| 3 | TreeSet backed by? | TreeMap |
| 4 | TreeSet add bound? | O(log n) |
| 5 | LinkedHashSet iteration? | insertion order |
| 6 | LinkedHashSet ops? | O(1) avg |
| 7 | BitSet word bits? | 64 |
| 8 | BitSet add(i)? | O(1) |
| 9 | BitSet and/or? | wordwise ops |
| 10 | EnumSet backed by? | bitmask |
| 11 | HashSet iteration? | unspecified |
| 12 | TreeSet null? | generally no |
| 13 | LinkedHashSet null? | one |
| 14 | HashSet null? | one |
| 15 | TreeSet floor/ceiling? | O(log n) |
| 16 | EnumSet.allOf? | all constants |
| 17 | BitSet.set(i)? | set bit |
| 18 | BitSet vs HashSet memory? | BitSet denser for small ints |
| 19 | HashSet DUMMY value? | HashMap dummy |
| 20 | TreeSet custom comparator? | allowed |
| 21 | LinkedHashSet vs HashSet iteration? | insertion vs hash order |
| 22 | BitSet index mapping? | word=i/64 bit=i%64 |
| 23 | TreeSet subSet view? | navigable |
| 24 | HashSet removeIf? | lambda |
| 25 | EnumSet thread-safe? | no |
| 26 | TreeSet descendingSet? | view |
| 27 | HashSet clone? | shallow |
| 28 | LinkedHashSet clone? | shallow |
| 29 | BitSet clone? | copy |
| 30 | TreeSet contains? | O(log n) |
| 31 | HashSet clear? | O(n) |
| 32 | TreeSet clear? | O(n) |
| 33 | LinkedHashSet clear? | O(n) |
| 34 | BitSet cardinality()? | number of set bits |
| 35 | BitSet nextSetBit? | index of next 1 |
| 36 | BitSet previousSetBit? | index of prev 1 |
| 37 | EnumSet.of? | one or more constants |
| 38 | HashSet equals/hashCode contract? | required |
| 39 | TreeSet uses compareTo? | yes (natural order) |
| 40 | HashSet iteration order can change? | yes, on resize |
| 41 | LinkedHashSet order stable? | yes |
| 42 | BitSet max length? | limited by words |
| 43 | TreeSet min/max? | first/last O(log n) |
| 44 | HashSet.retainAll? | intersection |
| 45 | TreeSet headSet? | view up to exclusive |
| 46 | BitSet xor assignment? | xorInPlace |
| 47 | LinkedHashSet iteration cost? | O(n) |
| 48 | HashSet union cost? | O(m) |
| 49 | TreeSet union sorted? | yes |
| 50 | BitSet for sieve? | yes |
| 51 | EnumSet copyOf? | copy |
| 52 | HashSet iterator fail-fast? | yes |
| 53 | TreeSet iterator fail-fast? | yes |
| 54 | LinkedHashSet iterator fail-fast? | yes |
| 55 | BitSet iterator? | none — use nextSetBit |
| 56 | TreeSet comparator equal(0) keys? | treated equal |
| 57 | HashSet backed map type? | HashMap |
| 58 | LinkedHashSet backed? | LinkedHashMap |
| 59 | TreeSet backed? | TreeMap |
| 60 | When BitSet? | dense int domains |
