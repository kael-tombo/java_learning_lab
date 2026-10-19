# Mini Project: Server-Sent Events

## Moving parts

- Event-stream response shape supporting the cricket-score live ticker.
- Per-client cursor tracking supporting the cricket-score live ticker.
- Reconnection with replay.
- Heartbeat keep-alive frames.
- Backpressure-aware broadcasting.

## Build brief

This server-sent events mini build produces a working app you can run locally.
Scope stays deliberately small so every server-sent events behavior remains observable.
Budget roughly one focused evening for the implementation.
Success means demonstrating server-sent events judgment, not just compiling code.
Keep a lab journal noting each server-sent events surprise encountered.
Acceptance checks define the edge, and no additions go past them.

## Sequence

1. Stream ball-by-ball cricket scores to browsers for the service.
2. Tag each event with an incrementing identifier.
3. Replay missed overs when a client reconnects.
4. Send heartbeat frames through quiet rain delays.
5. Shed load gracefully when 200 clients connect at once.

## Done when

- [ ] Stream delivers 120 consecutive balls in order in the solution.
- [ ] Reconnect replays exactly the missed balls in the platform.
- [ ] Heartbeat keeps an idle connection alive 10 minutes.
- [ ] 200-client burst stays ordered per client.
- [ ] Dropped client never corrupts other clients streams.

## If time remains

Choose one realistic complication and bolt it onto the project.
Write the two-paragraph retro: which server-sent events decision proved hardest.
Demo time: the peer sees the system with just the acceptance checks as the guide.
