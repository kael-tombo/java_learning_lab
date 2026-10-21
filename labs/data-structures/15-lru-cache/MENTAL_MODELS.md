# Mental Models for LRU Cache

## 1. The Pile of Papers Model

Imagine a desk with a limited capacity for papers. When you read a paper, you put it on top of the pile. When the pile is full and you bring a new paper, you remove the paper at the bottom (the one you used least recently).

## 2. The Cafeteria Tray Model

A cafeteria has limited shelf space. Trays are stacked. When you take a tray (get), it goes to the top. New trays (put) go on top. When the stack is full, the bottom tray is removed.

## 3. The Most-Recently-Used-First Model

The head of the linked list is the most recently used item. The tail is the least. Every access moves the item to the head, like bringing an object to the front of a queue.
