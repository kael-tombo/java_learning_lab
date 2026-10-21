# How It Works
Greedy coloring: process vertices sequentially, assign lowest-numbered color not used by neighbors. Welsh-Powell: sort by degree, color each with first available, repeat for remaining. DSatur: maintain saturation degree (number of distinct colors in neighborhood), pick highest sat, assign lowest available color.
