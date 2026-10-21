# How It Works
SAM: extend character by character. Each new character may clone a state. Contains: walk transitions, if path exists then substring present. Manacher: maintain center and rightmost palindrome. Use symmetry p[i] = min(right-i, p[2*center-i]) then expand.
