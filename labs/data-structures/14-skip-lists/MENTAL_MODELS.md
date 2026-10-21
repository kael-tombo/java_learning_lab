# Mental Models for Skip Lists

## 1. The Multi-Lane Highway Model

Skip lists are like a multi-lane highway:
- Level 0 (local roads): All elements, slow to traverse
- Level 1 (highway): Every other element, faster
- Level 2 (express lane): Every fourth element, even faster
- Higher levels: Faster and fewer exits

Searching is like taking the express lane as far as possible, then dropping to lower levels for local exits.

## 2. The Express Elevator Model

Like an elevator that only stops at certain floors:
- Top level: Stops at foyers
- Middle level: Stops at every 5th floor
- Bottom level: Stops at every floor

To find your floor, take the highest elevator as far as it goes, then switch to progressively lower ones.

## 3. The Book Index Model

Like a book's table of contents + index:
- Table of contents (high level): Chapter-level granularity
- Section headings (mid level): Section-level
- Index (low level): Page-level detail

You start broad and narrow down.
