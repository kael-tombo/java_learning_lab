# Memory Deep - Micro-Labs

## Overview
This module contains 5 atomic deep-dive micro-labs.

## Lab Index
| # | Lab | Description |
|---|-----|-------------|
| 01 | [JMM Foundations](./01-jmm-foundations/) | JSR-133, happens-before, sequential consistency, causality, observable behavior |
| 02 | [Reordering](./02-reordering/) | Compiler reordering, CPU out-of-order (Tomasulo), store buffer, invalidate queue, memory ordering (TSO/ARM/Power) |
| 03 | [Memory Barriers](./03-memory-barriers/) | LoadLoad/LoadStore/StoreLoad/StoreStore barriers, x86 MFENCE/LFENCE/SFENCE, ARM DMB/DSB, JVM barrier insertion |
| 04 | [Final Field Semantics](./04-final-semantics/) | Final field freeze, write to final + fence, deferred final-store safety (JVMS 17.5), construction safety |
| 05 | [DCL Pattern](./05-dcl-pattern/) | DCL broken in JMM pre-5, volatile fix, static holder idiom, enum singleton, init-on-demand |

## How to Use
Each micro-lab is self-contained with 24 markdown files, Java source code,
JUnit 5 tests, and 7 subdirectories for hands-on work.
Start from lab 01 and progress sequentially.