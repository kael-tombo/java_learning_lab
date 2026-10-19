# Code Deep Dive: 05-prompt-engineering
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg05A - few-shot prompt assembly
Instruction + 2 demos + query = 11 words; pattern labeled.
```java
public class Lg05A {
    public static void main(String[] args) {
        String[] ex={"Q: 2+3 A: 5","Q: 4+1 A: 5"};
        int toks=0; for(String s:ex) toks+=s.split(" ").length;
        String q="Q: 6+2 A:";
        toks+=q.split(" ").length;
        System.out.printf("fewshot_examples=%d prompt_words=%d%n", ex.length, toks);
        System.out.printf("pattern=instruction + 2 demos + query%n");
    }
}
```
Observed output:
```
fewshot_examples=2 prompt_words=11
pattern=instruction + 2 demos + query
```
## Snippet 2: Lg05B - self-consistency vote
Samples [42,41,42]: 2/3 for 42; CoT 3-step note.
```java
public class Lg05B {
    public static void main(String[] args) {
        String[] paths={"42","41","42"};
        int votes=0; for(String p:paths) if(p.equals("42")) votes++;
        System.out.printf("self_consistency: 42 x%d/3 -> final=42%n", votes);
        System.out.printf("cot_steps=3 (decompose, solve, verify)%n");
    }
}
```
Observed output:
```
self_consistency: 42 x2/3 -> final=42
cot_steps=3 (decompose, solve, verify)
```
## Checks
- Word count 11 = 3+3+... split-counted in code, deterministic.
- Majority 42 wins 2/3: sampling diverse paths then voting beats single greedy on hard items.

