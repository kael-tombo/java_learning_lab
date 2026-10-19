# Code Deep Dive: 06-llm-agents
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg06A - ReAct loop trace
thought->act->obs->thought->answer, 5 steps, 2x population task.
```java
public class Lg06A {
    public static void main(String[] args) {
        System.out.printf("thought: need population data -> act: search[city pop]%n");
        System.out.printf("obs: 500k -> thought: compute 2x -> act: calc[2*500k]%n");
        System.out.printf("obs: 1000000 -> answer: 1000000%n");
        System.out.printf("react_steps=5 (thought,act,obs,thought,answer)%n");
    }
}
```
Observed output:
```
thought: need population data -> act: search[city pop]
obs: 500k -> thought: compute 2x -> act: calc[2*500k]
obs: 1000000 -> answer: 1000000
react_steps=5 (thought,act,obs,thought,answer)
```
## Snippet 2: Lg06B - tool scoring
Scores [0.2,0.85,0.4] pick calculator by argmax.
```java
public class Lg06B {
    public static void main(String[] args) {
        double[] scores={0.2,0.85,0.4};
        String[] tools={"search","calculator","calendar"};
        int best=0; for(int i=1;i<3;i++) if(scores[i]>scores[best]) best=i;
        System.out.printf("tool_scores=[%.2f,%.2f,%.2f] pick=%s%n", scores[0],scores[1],scores[2], tools[best]);
    }
}
```
Observed output:
```
tool_scores=[0.20,0.85,0.40] pick=calculator
```
## Checks
- Loop terminates on answer action after consuming observation 1000000.
- Deterministic pick: index 1 max is unambiguous (0.85 > 0.4 > 0.2).

