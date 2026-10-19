# Code Deep Dive: 02-matrices-operations
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Mt02A - matmul, transpose, trace
A=[[1,2],[3,4]], B=[[2,0],[1,2]]: product and trace 12.
```java
public class Mt02A {
    public static void main(String[] args) {
        double[][] A={{1,2},{3,4}}, B={{2,0},{1,2}};
        double[][] C=new double[2][2];
        for(int i=0;i<2;i++)for(int j=0;j<2;j++)for(int k=0;k<2;k++)C[i][j]+=A[i][k]*B[k][j];
        System.out.printf("AB=[[%.0f,%.0f],[%.0f,%.0f]] trace=%.0f%n", C[0][0],C[0][1],C[1][0],C[1][1],C[0][0]+C[1][1]);
        System.out.printf("AT=[[%.0f,%.0f],[%.0f,%.0f]]%n", A[0][0],A[1][0],A[0][1],A[1][1]);
    }
}
```
Observed output:
```
AB=[[4,4],[10,8]] trace=12
AT=[[1,3],[2,4]]
```
## Snippet 2: Mt02B - 2x2 inverse verified
det=10; inv via adjugate; A*inv printed as identity.
```java
public class Mt02B {
    public static void main(String[] args) {
        double[][] A={{4,7},{2,6}};
        double det=A[0][0]*A[1][1]-A[0][1]*A[1][0];
        double[][] I={{A[1][1]/det,-A[0][1]/det},{-A[1][0]/det,A[0][0]/det}};
        System.out.printf("det=%.0f inv=[[%.4f,%.4f],[%.4f,%.4f]]%n", det, I[0][0],I[0][1],I[1][0],I[1][1]);
        System.out.printf("A*inv=[[%.1f,%.1f],[%.1f,%.1f]]%n",
            A[0][0]*I[0][0]+A[0][1]*I[1][0], A[0][0]*I[0][1]+A[0][1]*I[1][1],
            A[1][0]*I[0][0]+A[1][1]*I[1][0], A[1][0]*I[0][1]+A[1][1]*I[1][1]);
    }
}
```
Observed output:
```
det=10 inv=[[0.6000,-0.7000],[-0.2000,0.4000]]
A*inv=[[1.0,0.0],[-0.0,1.0]]
```
## Checks
- AB=[[4,4],[10,8]]: hand-check row 2 = 3*2+4*1=10, 3*0+4*2=8.
- A*inv=[[1,0],[0,1]] (the -0.0 is floating zero) confirms the inverse.

