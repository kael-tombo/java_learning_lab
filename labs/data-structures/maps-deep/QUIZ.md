# QUIZ — Maps Deep

## Q1
HashMap average get is:
a) O(1)  b) O(log n)  c) O(n)  d) O(n²)

## Q2
HashMap treeifies a bucket at:
a) 4  b) 8 (with cap ≥ 64)  c) 2  d) never

## Q3
HashMap load factor default:
a) 0.5  b) 0.75  c) 1.0  d) 0.9

## Q4
TreeMap ops bound:
a) O(1)  b) O(log n)  c) O(n)  d) O(n log n)

## Q5
LinkedHashMap preserves:
a) sorted order  b) insertion/access order  c) no order  d) heap order

## Q6
ConcurrentHashMap Java 8 bucket lock model?
a) CAS on head + sync on head node  b) single lock  c) segment locks  d) no sync

## Q7
HashMap allows null keys?
a) one  b) many  c) zero  d) at capacity edge

## Q8
TreeMap allows null keys?
a) yes  b) no (natural order)  c) one  d) always

## Q9
ConcurrentHashMap null keys?
a) one  b) many  c) zero  d) yes but unsafe

## Q10
Bloom filter FPR depends on:
a) m/n and k  b) only n  c) only m  d) not on k

## Q11
HashMap resize doubles:
a) keys  b) capacity and rehashes  c) values  d) threads

## Q12
LinkedHashMap accessOrder=true gives:
a) insertion order  b) access order  c) sorted  d) heap

## Q13
HashMap iteration order is:
a) undefined  b) insertion  c) sorted  d) heap

## Q14
ConcurrentHashMap iterators are:
a) fail-fast  b) weakly consistent  c) snapshot-only  d) none

## Q15
HashMap vs Hashtable key difference:
a) Hashtable synchronized+no nulls  b) HashMap slower  c) equal  d) Hashtable bigger

## Answer Key
1-a, 2-b, 3-b, 4-b, 5-b, 6-a, 7-a, 8-b, 9-c, 10-a, 11-b, 12-b, 13-a, 14-b, 15-a
