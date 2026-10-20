# How Skip Lists Work

## Level Structure

A skip list with MAX_LEVEL = 4:
`
Level 3: header â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€→ [5] â”€→ null
Level 2: header â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€→ [3] â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€→ [5] â”€→ null
Level 1: header â”€â”€â”€→ [1] â”€→ [3] â”€â”€â”€→ [4] â”€â”€â”€→ [5] â”€→ [7] â”€→ null
Level 0: header → [1] → [2] → [3] → [4] → [5] → [6] → [7] → null
`

## Random Level Generation

`java
int randomLevel() {
    int level = 1;
    while (Math.random() < 0.5 && level < MAX_LEVEL) {
        level++;
    }
    return level;
}
`

## Search Process

To search for 6:
1. Start at header, level 3: forward[3] = 5, 5 < 6, move to 5
2. At 5, level 3: forward[3] = null, drop to level 2
3. At 5, level 2: forward[2] = null, drop to level 1
4. At 5, level 1: forward[1] = 7, 7 >= 6, drop to level 0
5. At 5, level 0: forward[0] = 6, found!
