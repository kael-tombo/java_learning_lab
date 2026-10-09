## Front: What is a circular buffer?
Back: Fixed-size FIFO buffer with wrap-around pointers. O(1) enqueue/dequeue.

## Front: What is the overwrite policy?
Back: When full, new data overwrites the oldest data, advancing the head.

## Front: What is the blocking policy?
Back: When full, producers block until consumers free space.

## Front: What is an SPSC buffer?
Back: Single Producer, Single Consumer — can be lock-free with volatile.
