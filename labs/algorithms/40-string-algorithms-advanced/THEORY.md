# Theory
Suffix Automaton: minimal DFA accepting all suffixes. Built incrementally O(n). Each state has length (longest string) and link (suffix link). Manacher: finds longest palindrome in O(n) using symmetry to avoid redundant comparisons. BWT: sorts all rotations, takes last column; invertible via LF mapping.
