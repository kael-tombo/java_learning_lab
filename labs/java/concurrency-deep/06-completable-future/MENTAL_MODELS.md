# Mental Models: CompletableFuture

## 1. Dominoes, not phone calls

A CF chain is a domino row: completing the first tips the next, in the same
motion (same thread). Nobody "calls" the next stage — it falls because the
previous one fell. `*Async` inserts a gap: the domino tips a *message* onto
another table (executor) instead.

## 2. Map vs flatMap (streams instincts transfer)

`thenApply` wraps: `CF<User>` + `User→String` = `CF<String>`. `thenCompose`
unwraps one level: `CF<User>` + `User→CF<Orders>` = `CF<Orders>`. If your
lambda returns a future and you used `thenApply`, picture a box inside a
box — open it with `thenCompose`.

## 3. allOf as a turnstile, not a bag

`allOf` is the exit turnstile that clicks when everyone has passed — it holds
no shopping (values). Collect the bags afterwards by visiting each shopper
(`join()` on inputs). Asking the turnstile for values is the category error.

## 4. anyOf as a photo finish

First nose across wins — even if that nose is an exception. The photo
(`CF<Object>`) records *who* won; stragglers keep running the race (and
billing you) until explicitly cancelled.

## 5. Handlers as three airport staff

`exceptionally` = rebooking desk (only sees stranded passengers, issues a new
ticket or strands them again). `handle` = customs (sees everyone, stamps one
unified form). `whenComplete` = CCTV (watches everything, changes nothing).

## 6. Cancel as a starting gun recalled

`cancel()` only works before the gun: once the runner (`supplyAsync` body) is
moving, recalling the gun changes the scoreboard (`CancellationException` for
dependents) but the runner finishes the lap. Real mid-race tackles need your
own `Thread`/`FutureTask`.

## 7. The common pool as a shared kitchen

Default `*Async` cooks in the building's shared kitchen (parallel streams eat
there too). A 90-minute blocking stew blocks everyone's lunch. Blocking
recipes bring their own kitchen (dedicated executor) — always.
