# Refactoring — Time Ordering

## 1. Extract Clock Interface
**Before:** Inline clock operations
**After:** Common EventClock<T> interface

## 2. Value Objects for Timestamps
**Before:** Raw int timestamps
**After:** Typed Timestamp value objects

## 3. Extract Comparison Logic
**Before:** Inline comparison
**After:** Well-named methods in clock class

## 4. Builder Pattern for HLC
**Before:** Complex constructor parameters
**After:** HLC.builder().physicalTimeProvider(...).build()

## 5. Separate Clock from Communication
**Before:** Clock mixed with network code
**After:** Interceptor pattern separates concerns

## 6. Immutable Snapshots
**Before:** Mutable clocks shared across threads
**After:** Immutable snapshots for external use
