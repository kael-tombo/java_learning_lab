# Why Circular Buffers Exist

## The Problem

Linear queues require shifting elements on dequeue (O(n)), or they waste space. A linked list avoids shifting but has allocation overhead and poor cache locality.

## The Solution

Circular buffers provide O(1) enqueue and dequeue with a fixed memory allocation. No elements are shifted, no dynamic allocation occurs at runtime (after initialization).

## Use Cases

- Audio/video streaming (real-time data)
- Producer-consumer patterns
- Logging (fixed-size history)
- Network packet buffering
- Hardware FIFOs (UART, SPI)
