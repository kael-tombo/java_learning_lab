# Code Deep Dive: 09-clustering-dbscan
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Cml09A - core/border/noise census
5 points, eps=1.5, minPts=3: neighbor counts decide labels.
```java
public class Cml09A {
    public static void main(String[] args) {
        double[][] X={{0,0},{1,0},{0,1},{5,5},{9,9}};
        double eps=1.5; int minPts=3;
        for(int i=0;i<5;i++){int cnt=0;for(int j=0;j<5;j++){double d=Math.hypot(X[i][0]-X[j][0],X[i][1]-X[j][1]);if(d<=eps)cnt++;}
            String t=cnt>=minPts?"core":(cnt>=2?"border":"noise");
            System.out.printf("pt%d neighbors=%d -> %s%n", i, cnt, t);}
    }
}
```
Observed output:
```
pt0 neighbors=3 -> core
pt1 neighbors=3 -> core
pt2 neighbors=3 -> core
pt3 neighbors=1 -> noise
pt4 neighbors=1 -> noise
```
## Snippet 2: Cml09B - cluster expansion
eps=1.0, minPts=2: density-reachable grouping of two triplets/pairs.
```java
public class Cml09B {
    public static void main(String[] args) {
        double[][] X={{0,0},{0.5,0},{0,0.5},{5,5},{5.4,5}};
        double eps=1.0;
        int[] label={-1,-1,-1,-1,-1};
        int cid=0;
        for(int i=0;i<5;i++){
            if(label[i]!=-1) continue;
            java.util.List<Integer> nb=new java.util.ArrayList<>();
            for(int j=0;j<5;j++) if(Math.hypot(X[i][0]-X[j][0],X[i][1]-X[j][1])<=eps) nb.add(j);
            if(nb.size()<2){label[i]=-1;}
            else{for(int k:nb) if(label[k]==-1) label[k]=cid; cid++;}
        }
        for(int i=0;i<5;i++) System.out.printf("pt%d cluster=%d%n", i, label[i]);
    }
}
```
Observed output:
```
pt0 cluster=0
pt1 cluster=0
pt2 cluster=0
pt3 cluster=1
pt4 cluster=1
```
## Checks
- Points 0-2 have 3 neighbors each -> core; (5,5) and (9,9) have 1 -> noise.
- Expansion yields cluster 0 = {0,1,2}, cluster 1 = {3,4}.

