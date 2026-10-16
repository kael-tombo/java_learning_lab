# Model Serving - Visual Guide

## Online path
```text
client -> [gateway] -> [preprocess] -> [model] -> [postprocess] -> response
                        (validate)      (warmed)                  (log version)
```

## Batch vs online vs streaming
```text
batch:     [partition] ==> [shards] ==> [prediction table]   (slow, huge)
online:    request --> score --> response                    (fast, single)
streaming: events ~~~> [stateful scorer] ~~~> actions        (continuous)
```

## Rollout ladder
```text
shadow (0% acted) -> canary (small %) -> stepped shift -> full (rollback = route back)
```

## Batching tradeoff sketch
```text
throughput ^                                latency ^
          /                                          /
         /                                          /
        +---> batch size                            +---> batch size
```

## Latency legs
```text
budget:  [preprocess | model | postprocess | network+queue]  = p99 cap
alert:        owner1    owner2     owner3        owner4
```

## Cache key
```text
key = hash(request fields + model version + schema version)
promote -> invalidate keys with old version -> verify with bump test
```

## Version pools during shift
```text
old pool (90%) ===> responses tagged v3
new pool (10%) ===> responses tagged v4   (compare p50/p99 + errors)
rollback = route 100% back to old pool (warm, tested)
```

## Queue depth warning
```text
depth:  low ...... knee ...... flood
action: watch    warn+add      shed shadow, then shift back
```
