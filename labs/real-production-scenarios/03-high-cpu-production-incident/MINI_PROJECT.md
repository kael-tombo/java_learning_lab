# MINI_PROJECT — Reproduce, Profile, Fix High CPU

## Objective
Inject a regex + spin-loop CPU hog, identify the exact method via profiler, and fix. ~75 min.

## 1. Setup (10 min)
JDK 17 + async-profiler binary. Single Java file, no framework.

## 2. Inject (15 min)
```java
// HotCpu.java
import java.util.regex.*;
public class HotCpu {
  static final Pattern EVIL = Pattern.compile("(a+)+b");
  public static void main(String[] a){
    Thread t = new Thread(()->{ while(true){ EVIL.matcher("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!").matches(); }});
    t.setName("regex-hog"); t.start();
    System.out.println("pid=" + ProcessHandle.current().pid());
  }
}
```
`javac HotCpu.java && java HotCpu` — one core pegged.

## 3. Detect (20 min)
```bash
top -H -p <pid>
printf '%x\n' <hot-tid>
jstack -l <pid> | grep -A15 "nid=0x<hex>" | head -20
./profiler.sh -e cpu -d 30 -f /tmp/mini-cpu.html <pid>
```
Open flame: widest plateau = `Pattern$Curly.match` ← `HotCpu` frame. Screenshot it.

## 4. Fix (20 min)
- Fix A: change to `(a++)b` or pre-validate length + `Pattern` with timeout logic.
- Add input guard: `if(s.length()>100) reject`. Re-profile 30s — CPU flat.
- Bonus: add spin-loop variant `while(!flag){}` → fix with `parkNanos` + measure.

## 5. Harden (10 min)
Write a 10-line script: top-thread → hex → jstack excerpt. Save as team runbook snippet.

## Deliverables
Flame before/after, hot-thread mapping, fix diff, CPU graphs.

## Grading
Reproduce (20%), map hot thread (30%), flame proof (30%), fix+verify (20%).
