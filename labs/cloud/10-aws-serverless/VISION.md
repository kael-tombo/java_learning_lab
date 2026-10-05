# AWS Serverless - Vision

## The Big Picture
Serverless changes where your code runs and who manages it — not whether it has state,
connections, or failure modes. The execution model is short-lived and stateless, and every
assumption about warm processes, long transactions, and in-memory sessions has to be
revisited.

## Why This Matters
The majority of serverless production incidents come from three things: assuming the container
stays warm, assuming the execution is isolated from its neighbour, and assuming at-least-once
event delivery will not duplicate your side effects. All three are learnable in a lab.

## The Vision for This Lab
This lab works through the real model: cold starts, concurrency scaling, event-driven
orchestration, timeouts and retries, and dead-letter paths. Then it builds a real Java Lambda
application and measures it against a container-based equivalent.

## Learning Philosophy
1. Stateless or it is not serverless — no in-memory session state, no local disk assumptions
2. Every event invocation is a retry until proven otherwise
3. Concurrency is a scaling parameter, not an accident
4. Measure cold starts; do not assume they are fine

## Future Path
- 58-serverless and 03-serverless-deep — the dedicated serverless track
- 06-distributed-messaging — the event backbone serverless sits on
- 11-aws-observability — X-Ray and distributed tracing for functions

## Success Metrics
You have mastered AWS serverless when you can:
- [ ] Deploy a Java Lambda with a reproducible build and measured cold start
- [ ] Configure concurrency and demonstrate scaling behaviour
- [ ] Implement an idempotent event handler with a DLQ
- [ ] Model a Step Functions workflow with retries, catches, and a DLQ

## The Serverless Mindset
> The function is disposable. Design so that being invoked twice, being killed mid-request,
or being replaced by a new version mid-flight are all boring events rather than incidents.