# Code Deep Dive: 05-random-forest
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml05A - bootstrap bags and OOB sets
n=6, seed 7: 3 resamples with replacement; unsampled indices are out-of-bag.
```java
public class Cml05A {
    public static void main(String[] args) {
        java.util.Random r=new java.util.Random(7);
        int n=6;
        for(int t=0;t<3;t++){
            boolean[] in=new boolean[n];
            StringBuilder sb=new StringBuilder();
            for(int i=0;i<n;i++){int k=r.nextInt(n);in[k]=true;sb.append(k).append(" ");}
            StringBuilder oob=new StringBuilder();
            for(int i=0;i<n;i++) if(!in[i]) oob.append(i).append(" ");
            System.out.printf("tree%d bag=[%s] oob=[%s]%n", t, sb.toString().trim(), oob.toString().trim());
        }
    }
}
```
Observed output:
```
tree0 bag=[4 2 3 4 4 4] oob=[0 1 5]
tree1 bag=[4 5 0 0 0 0] oob=[1 2 3]
tree2 bag=[0 1 1 4 3 0] oob=[2 5]
```
## Snippet 2: Cml05B - majority vote
3 fixed stump votes on 4 samples vs truth; ensemble accuracy.
```java
public class Cml05B {
    public static void main(String[] args) {
        int[][] votes={{1,1,0},{0,0,0},{1,0,1},{0,1,1}};
        int[] truth={1,0,1,1};
        int ok=0;
        for(int i=0;i<4;i++){int s=votes[i][0]+votes[i][1]+votes[i][2];int p=s>=2?1:0;if(p==truth[i])ok++;
            System.out.printf("sample%d votes=%d/3 pred=%d true=%d%n", i, s, p, truth[i]);}
        System.out.printf("ensemble_acc=%d/4%n", ok);
    }
}
```
Observed output:
```
sample0 votes=2/3 pred=1 true=1
sample1 votes=0/3 pred=0 true=0
sample2 votes=2/3 pred=1 true=1
sample3 votes=2/3 pred=1 true=1
ensemble_acc=4/4
```
## Checks
- Tree 0 bag [4 2 3 4 4 4], OOB [0 1 5]: duplicates plus unseen indices, as theory predicts (~1/3 OOB).
- Majority vote: 4/4 correct although individual stumps err.

