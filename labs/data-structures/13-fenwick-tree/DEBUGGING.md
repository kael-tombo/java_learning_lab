# Debugging Fenwick Tree

## Verification Strategy

### Brute Force Validation
`java
public boolean validate(int[] arr) {
    FenwickTree ft = FenwickTree.fromArray(arr);
    int[] prefix = new int[arr.length];
    for (int i = 0; i < arr.length; i++) {
        prefix[i] = (i > 0 ? prefix[i-1] : 0) + arr[i];
        if (ft.sum(i) != prefix[i]) return false;
    }
    return true;
}
`

## Common Bug Symptoms

| Symptom | Likely Cause |
|---------|-------------|
| Wrong prefix sum | 0-indexed/1-indexed conversion error |
| Infinite loop | Wrong loop condition in add/sum |
| ArrayIndexOutOfBounds | BIT array too small |
| Negative sum values | Integer overflow or incorrect range update |
| Random wrong values | Not updating all relevant indices |
| Off-by-one in range queries | l-1 not used in rangeSum |

## Print State
`java
public void printState() {
    System.out.println("BIT: " + Arrays.toString(bit));
    System.out.print("Prefix sums: ");
    for (int i = 0; i < n; i++) {
        System.out.print(sum(i) + " ");
    }
    System.out.println();
}
`

## Unit Testing Tips

1. Test with n = 1, 2, 3 (small exhaustive)
2. Test with arrays of size power of 2
3. Test with arrays of size power of 2 - 1
4. Test with random operations, verify against brute force
5. Test range update + range query with two BITs
