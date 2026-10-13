# Step by Step: Class Loading

## Step 1 — Print the tree

```bash
mkdir -p /tmp/cl && cd /tmp/cl
cat > LoaderTree.java <<'EOF'
public class LoaderTree {
    public static void main(String[] args) {
        ClassLoader app = ClassLoader.getSystemClassLoader();
        ClassLoader platform = ClassLoader.getPlatformClassLoader();
        System.out.println("bootstrap = " + String.class.getClassLoader());
        System.out.println("platform = " + platform.getName());
        System.out.println("app = " + app.getName());
        System.out.println("app parent is platform: " + (app.getParent() == platform));
        System.out.println("platform parent is null: " + (platform.getParent() == null));
    }
}
EOF
javac LoaderTree.java && java LoaderTree
```

Expect `null / platform / app / true / true`. No extension rung.

## Step 2 — Separate load from init

Write `InitVsLoad` (CODE_DEEP_DIVE snippet 2), compile, run. Confirm
the marker prints with no `<clinit>` line above it, then the
`<clinit>` line, then `initialized=true`, `same Class=true`.

## Step 3 — Split one class into two identities

```bash
mkdir -p split/src && cd split
cat > src/Widget.java <<'EOF'
public class Widget { public int x = 5; }
EOF
javac -d classes src/Widget.java
```

Write `SplitIdentity` (snippet 3) pointing at `classes/`. Run:
expect `different Class objects: true`, `cast rejected: true`.
Print both loaders; confirm neither is the app loader.

## Step 4 — Show constants skipping init

Write `ConstNoInit` (snippet 4), run. Expect `PORT = 8080` first
with no `<clinit>` line, then the `<clinit>` line with the computed
read. Run `javap -c ConstNoInit.class | grep -A2 PORT` and find the
inlined literal at the use site.

## Step 5 — Show the one-directional wall

Write `ContextVsOwn` (snippet 5), run. Expect `context is app:
true`, `context sees app: true`, `framework sees app: false`. State
the rule aloud: delegation looks up; the context loader looks down.

## Step 6 — Map a failure to its phase

Pick one observed error (or induce `NoSuchMethodError` by compiling
against a two-method `Widget` and running against a one-method
build). Classify it: load (`ClassNotFoundException`), link-verify
(`VerifyError`), link-resolve (`NoSuchMethodError`), or init
(`ExceptionInInitializerError`). The phase names the fix layer.
