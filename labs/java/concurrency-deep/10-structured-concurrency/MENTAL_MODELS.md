# Mental Models: Structured Concurrency

## 1. The nursery, not the playground

Picture a nursery: children check in at the door and must be picked up
before closing. A scope is the nursery, subtasks are the children, and
`close()` is closing time — nobody stays overnight. Unstructured
`thread.start()` is a playground with no fence: children wander off and
nobody notices until something breaks.

## 2. Fork is a loan, join is repayment

Each `fork()` borrows one thread against the block's account; `join()`
settles the account. You may hold many loans at once (fan-out), but the
block cannot exit with debt outstanding — `close()` forecloses by
cancelling leftovers. Counting outstanding forks like debts makes leaks
visible before they happen.

## 3. Policies as trip wires

`ShutdownOnFailure` strings a trip wire across the failure path: the
first subtask to fail yanks it and the whole room powers down. Success
wires work mirrored in `ShutdownOnSuccess`: the first success yanks its
wire and siblings stand down. One event decides the scope; everything
after it is diagnostics.

## 4. The owner holds the only key

Only the creating thread's key fits the `join`/`close`/`result` locks;
copies do not exist (`WrongThreadException` for intruders). Hand out
result values to other threads freely, but never hand out the scope —
whoever holds it must be the one who made it.

## 5. Nesting as Russian dolls

A subtask that opens its own scope is a doll containing smaller dolls.
Crack open the outer doll and every inner one is already sealed: inner
`close()` contained grandchildren before the outer `join()` ever saw
the subtask complete. Depth adds levels, never escape hatches.

## 6. States as sealed envelopes

An `UNAVAILABLE` subtask is a sealed envelope — contents unknown, do not
open (`get()` throws). `SUCCESS` seals a value inside; `FAILED` seals an
exception. `join()` is the delivery round; only after delivery does
opening envelopes make sense.

## 7. Deadlines as last trains

`joinUntil(Instant)` is catching the last train: board by departure or
stay on the platform (`TimeoutException`). Missing it strands nothing —
`close()` still sends every traveller home. The deadline bounds your
wait, never the scope's duty of care.

## 8. Interrupts as fire alarms

`shutdown()` pulls the alarm; subtasks near exits (interruptible calls)
leave at once, while ones wearing earplugs (compute loops ignoring the
flag) linger until dragged out at `close()`. Design subtasks to hear
the alarm: poll the flag or use interruptible waits.
