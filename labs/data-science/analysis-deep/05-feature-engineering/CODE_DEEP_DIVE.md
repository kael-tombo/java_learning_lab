# Feature Engineering - Code Deep Dive (JDK-only; outputs observed)

## 1. One-hot with fixed vocabulary

```java
import java.util.Arrays;
import java.util.List;

public class FeatOneHot {
    public static void main(String[] args) {
        List<String> cats = List.of("red", "green", "blue");
        String[] col = {"red", "blue", "green", "red"};
        for (String v : col) {
            int[] row = new int[cats.size()];
            row[cats.indexOf(v)] = 1;
            System.out.println(v + " -> " + Arrays.toString(row));
        }
        System.out.println("ordinal alternative: red=0 green=1 blue=2 (implies order; use only if ordered)");
        System.out.println("target encoding warning: fit means on train folds only, never full labels");
    }
}
```

```text
red -> [1, 0, 0]
blue -> [0, 0, 1]
green -> [0, 1, 0]
red -> [1, 0, 0]
ordinal alternative: red=0 green=1 blue=2 (implies order; use only if ordered)
target encoding warning: fit means on train folds only, never full labels
```

## 2. Train-only fit, frozen apply

```java
public class FeatTrainOnly {
    public static void main(String[] args) {
        double[] train = {10, 20, 30, 40};
        double[] test = {25, 100};
        double sum = 0;
        for (double v : train) sum += v;
        double mean = sum / train.length;
        double ss = 0;
        for (double v : train) ss += (v - mean) * (v - mean);
        double sd = Math.sqrt(ss / train.length);
        System.out.println("train mean=" + mean + " sd=" + sd);
        for (double v : test) {
            System.out.println("test " + v + " -> z=" + ((v - mean) / sd));
        }
        // Leakage demo: mean fitted on train+test would be 37.5, shifting every z.
        double leakMean = (10 + 20 + 30 + 40 + 25 + 100) / 6.0;
        System.out.println("leaky all-data mean=" + leakMean + " (do NOT use)");
        System.out.println("rule: fit on train only; apply same transform to test/folds");
    }
}
```

```text
train mean=25.0 sd=11.180339887498949
test 25.0 -> z=0.0
test 100.0 -> z=6.7082039324993685
leaky all-data mean=37.5 (do NOT use)
rule: fit on train only; apply same transform to test/folds
```

## 3. Interactions plus log

```java
public class FeatInteractions {
    public static void main(String[] args) {
        double[] area = {50, 80, 120};
        double[] rooms = {2, 3, 4};
        for (int i = 0; i < area.length; i++) {
            double inter = area[i] * rooms[i];
            double logArea = Math.log(area[i]);
            System.out.println("area=" + area[i] + " rooms=" + rooms[i]
                + " area_x_rooms=" + inter + " log(area)=" + logArea);
        }
        System.out.println("log compresses right skew; interaction lets linear model price big-many-room homes");
    }
}
```

```text
area=50.0 rooms=2.0 area_x_rooms=100.0 log(area)=3.912023005428146
area=80.0 rooms=3.0 area_x_rooms=240.0 log(area)=4.382026634673881
area=120.0 rooms=4.0 area_x_rooms=480.0 log(area)=4.787491742782046
log compresses right skew; interaction lets linear model price big-many-room homes
```
