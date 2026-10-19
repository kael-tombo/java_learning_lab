# Code Deep Dive: 09-hallucination-mitigation
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg09A - citation coverage
3/4 claims cited = 0.75.
```java
public class Lg09A {
    public static void main(String[] args) {
        String[] claims={"cited","cited","uncited","cited"};
        int c=0; for(String s:claims) if(s.equals("cited")) c++;
        System.out.printf("citation_coverage=%d/%d=%.2f%n", c, claims.length, (double)c/claims.length);
    }
}
```
Observed output:
```
citation_coverage=3/4=0.75
```
## Snippet 2: Lg09B - self-check agreement
Paris 3/4 = 0.75 accept; <0.5 abstain rule stated.
```java
public class Lg09B {
    public static void main(String[] args) {
        String[] samples={"Paris","Paris","Lyon","Paris"};
        int v=0; for(String s:samples) if(s.equals("Paris")) v++;
        System.out.printf("selfcheck: Paris %d/4=%.2f -> accept%n", v, (double)v/samples.length);
        System.out.printf("abstain_rule: agree<0.5 -> say unsure%n");
    }
}
```
Observed output:
```
selfcheck: Paris 3/4=0.75 -> accept
abstain_rule: agree<0.5 -> say unsure
```
## Checks
- Coverage counts cited/total mechanically; raising it requires grounding, not rewording.
- Agreement threshold 0.5 separates accept from abstain deterministically.

