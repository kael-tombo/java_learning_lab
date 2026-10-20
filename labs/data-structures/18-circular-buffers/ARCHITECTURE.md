# Architecture

Circular buffers integrate as:
`
Producer → CircularBuffer → Consumer
`

Used in pipelines:
`
Network → PacketBuffer → Decoder → AudioBuffer → Speaker
`

Design patterns:
- Producer-Consumer pattern
- Pipeline pattern
- Observer pattern (with buffer)
