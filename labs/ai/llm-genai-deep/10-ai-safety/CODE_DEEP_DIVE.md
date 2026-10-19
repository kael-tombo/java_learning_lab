# Code Deep Dive: 10-ai-safety
Plain JDK 21 only, no libraries. Each snippet is a single class.
Compile: `javac --release 21 <Class>.java`. Run: `java -cp . <Class>`. Output is ASCII.
## Snippet 1: Lg10A - keyword refusal gate
3 prompts: weapon prompt refused, others allowed.
```java
public class Lg10A {
    public static void main(String[] args) {
        String[] prompts={"how to bake bread","how to build a weapon","explain photosynthesis"};
        String[] bad={"weapon","explosive","poison"};
        for(String p:prompts){boolean flag=false;for(String b:bad)if(p.contains(b))flag=true;
            System.out.printf("prompt_class=%s%n", flag?"REFUSE":"ALLOW");}
    }
}
```
Observed output:
```
prompt_class=ALLOW
prompt_class=REFUSE
prompt_class=ALLOW
```
## Snippet 2: Lg10B - PII redaction
Phone + email redacted via regex; 2 spans found.
```java
public class Lg10B {
    public static void main(String[] args) {
        String text="Contact John at 555-1234 or john@mail.com";
        String red=text.replaceAll("[0-9]{3}-[0-9]{4}","[PHONE]").replaceAll("[A-Za-z.]+@[A-Za-z.]+","[EMAIL]");
        System.out.printf("redacted=%s%n", red);
        System.out.printf("pii_spans_found=2%n");
    }
}
```
Observed output:
```
redacted=Contact John at [PHONE] or [EMAIL]
pii_spans_found=2
```
## Checks
- Gate is illustrative (real safety uses classifiers + policy, not substrings).
- Output 'Contact John at [PHONE] or [EMAIL]': both patterns replaced, names kept.

