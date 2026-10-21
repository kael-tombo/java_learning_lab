# Why Immutable & Persistent Data Structures Exist

## The Problem: Shared Mutable State

Mutable state causes bugs in concurrent and functional programming. Two threads sharing a mutable list can interfere. A function that receives a mutable list can inadvertently modify the caller's data.

## The Solution

Persistence makes all operations safe: modifications return new structures without affecting existing ones. This eliminates entire categories of bugs.

## Functional Programming Roots

Persistent data structures are fundamental to functional programming (Clojure, Haskell, Scala). They enable pure functions that operate on data without side effects.

## Why Not Just Copy Everything?

Naive copying is O(n). Structural sharing makes persistence efficient: only O(log n) nodes are copied per operation. The rest is shared.
