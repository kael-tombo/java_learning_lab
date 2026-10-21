# History of Fenwick Tree

## Discovery (1994)

The Binary Indexed Tree was invented by Peter M. Fenwick while working at IBM. He published the data structure in the paper "A New Data Structure for Cumulative Frequency Tables" in the journal Software: Practice and Experience in 1994.

## The Problem Fenwick Solved

Fenwick was working on maintaining cumulative frequency tables for data compression algorithms. The existing approaches were either too slow (linear scan) or too memory-intensive. He needed a structure that could:
1. Update individual frequencies quickly
2. Compute cumulative frequencies quickly
3. Use minimal memory

## Early Adoption

The BIT was quickly adopted by the algorithms community due to its elegance:
- 1995: Incorporated into algorithm textbooks
- 1998: Used in IOI (International Olympiad in Informatics)
- 2000: Became a standard tool in competitive programming

## Name Evolution

The data structure goes by several names:
- **Fenwick Tree** (after the inventor)
- **Binary Indexed Tree** (BIT) (describing its structure)
- **Fenwick's Array** (alternative naming)

## Extensions Over Time

- **1995**: 2D BIT developed for matrix operations
- **2000**: Range update + range query using two BITs
- **2005**: BIT with coordinate compression for sparse data
- **2010**: Persistent BIT for versioned queries
- **2015**: Cache-optimized BIT variants

## Recognition

Today, the Fenwick tree is taught in every algorithms course and is a standard tool in competitive programming. It appears in the standard libraries of many programming contest environments.
