# Mock Interview: Classical Simulation of Quantum Circuits
> Three questions on what a classical simulator actually stores. This lab is about simulation cost on ordinary hardware, not quantum devices.
## Q1: single-qubit Hadamard
Problem: apply H to |0> in a 2-amplitude state vector and report amplitudes and probabilities.
Key insight: the simulator stores all 2 amplitudes explicitly and multiplies by the 2x2 unitary; norm preservation (unitarity) is checkable as p0 + p1 = 1.
Complexity: O(2^n) memory in general, O(1) at n = 1.
```java
public class L35Q1 {
    public static void main(String[] a){
        double h = 1.0 / Math.sqrt(2.0);
        double[] o = {h, h}; // H|0>
        System.out.println("amp0=" + String.format("%.4f", o[0]) + " amp1=" + String.format("%.4f", o[1]));
        System.out.println("p0=" + String.format("%.4f", o[0]*o[0]) + " p1=" + String.format("%.4f", o[1]*o[1]));
    }
}
```
Observed output:
```
amp0=0.7071 amp1=0.7071
p0=0.5000 p1=0.5000
```
Follow-up: which single-qubit gates only permute or flip signs of amplitudes?
## Q2: Bell pair via H + CNOT
Problem: build (|00> + |11>)/sqrt(2) from |00> with H on qubit 0 then CNOT.
Key insight: the result cannot be factored into two single-qubit states, yet the 4-amplitude vector still represents it exactly; measurement gives 00 or 11 with probability 1/2 each.
Complexity: O(4) memory at n = 2, doubling per qubit.
```java
public class L35Q2 {
    public static void main(String[] a){
        double h = 1.0 / Math.sqrt(2.0);
        double[] o = {h, 0, 0, h}; // (H x I)|00> then CNOT
        System.out.println("probs=" + String.format("%.4f", o[0]*o[0]) + "," + String.format("%.4f", o[1]*o[1]) + "," + String.format("%.4f", o[2]*o[2]) + "," + String.format("%.4f", o[3]*o[3]));
    }
}
```
Observed output:
```
probs=0.5000,0.0000,0.0000,0.5000
```
Follow-up: why does an entangled state still fit the same state-vector scheme?
## Q3: the 2^n memory wall
Problem: tabulate amplitudes and bytes (16 bytes per complex double) for n = 10, 20, 30, 40.
Key insight: each added qubit doubles memory, so n = 40 needs about 16 TiB; this doubling is why simulators top out near a few dozen qubits regardless of gate cleverness.
Complexity: O(2^n) memory per state vector.
```java
public class L35Q3 {
    public static void main(String[] a){
        for (int n : new int[]{10, 20, 30, 40}) System.out.println("n=" + n + " amplitudes=" + (1L<<n) + " bytes=" + ((1L<<n)*16L));
    }
}
```
Observed output:
```
n=10 amplitudes=1024 bytes=16384
n=20 amplitudes=1048576 bytes=16777216
n=30 amplitudes=1073741824 bytes=17179869184
n=40 amplitudes=1099511627776 bytes=17592186044416
```
Follow-up: which circuit families dodge the wall (Clifford/stabilizer simulation, tensor networks)?
## Pass checklist
- [ ] Recompute the byte column as 2^n x 16 by hand for one row.
- [ ] Confirm probabilities sum to 1 in Q1 and Q2 outputs.
- [ ] Describe the wall as classical memory cost, never as device performance.
