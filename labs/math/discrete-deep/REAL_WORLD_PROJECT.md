# Real-World Project: Social Network Analysis Tool

## Overview
Build a tool that models social networks as graphs and computes meaningful metrics: influence centrality, community detection, and information flow. This applies discrete mathematics to real-world network data.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Network Science (Barabási): http://networksciencebook.com/
- Stanford Network Analysis Project (SNAP): https://snap.stanford.edu/

## Project Goals
1. Model a social network as a graph
2. Compute degree, betweenness, and closeness centrality
3. Detect communities using modularity optimization
4. Simulate information spread (viral cascades)
5. Visualize the network with communities highlighted

## Mathematical Background

### Graph Representation
- **Adjacency matrix:** A[i][j] = 1 if edge exists between i and j
- **Adjacency list:** Dictionary mapping each node to its neighbors
- **Sparse vs. dense:** Choose representation based on edge density

### Centrality Measures
- **Degree centrality:** Number of direct connections; normalized by n-1
- **Betweenness centrality:** Fraction of shortest paths passing through a node
- **Closeness centrality:** Inverse of average shortest path distance to all others
- **Eigenvector centrality:** Importance based on connections to important nodes (PageRank)

### Community Detection
- **Modularity (Q):** Measures strength of community structure; Q = (1/2m) Σ [A_ij - k_i*k_j/2m] δ(c_i, c_j)
- **Greedy modularity:** Iteratively merge communities that maximize Q
- **Louvain method:** Hierarchical modularity optimization

### Information Spread
- **Independent cascade model:** Each activated node has one chance to activate each neighbor with probability p
- **Linear threshold model:** Node activates when fraction of active neighbors exceeds threshold

## Implementation Plan

### Phase 1: Graph Construction
```python
import networkx as nx
import random

def generate_social_network(n=100, p=0.1):
    """Generate a random social network using Erdős-Rényi model."""
    G = nx.erdos_renyi_graph(n, p)
    # Add weights based on interaction frequency
    for u, v in G.edges():
        G[u][v]['weight'] = random.uniform(0.1, 1.0)
    return G
```

### Phase 2: Centrality Analysis
```python
def analyze_centrality(G):
    degree = nx.degree_centrality(G)
    betweenness = nx.betweenness_centrality(G)
    closeness = nx.closeness_centrality(G)
    eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
    return {'degree': degree, 'betweenness': betweenness,
            'closeness': closeness, 'eigenvector': eigenvector}
```

### Phase 3: Community Detection
```python
import community as community_louvain

def detect_communities(G):
    partition = community_louvain.best_partition(G)
    modularity = community_louvain.modularity(partition, G)
    return partition, modularity
```

### Phase 4: Cascade Simulation
```python
def independent_cascade(G, seeds, p=0.1, steps=20):
    """Simulate information spread from seed nodes."""
    activated = set(seeds)
    newly_activated = set(seeds)
    history = [len(activated)]
    for _ in range(steps):
        next_wave = set()
        for node in newly_activated:
            for neighbor in G.neighbors(node):
                if neighbor not in activated and random.random() < p:
                    next_wave.add(neighbor)
        newly_activated = next_wave
        activated.update(newly_activated)
        history.append(len(activated))
        if not newly_activated:
            break
    return activated, history
```

### Phase 5: Visualization
Use matplotlib or plotly to render the network with:
- Node size proportional to centrality
- Color indicating community membership
- Edge width showing interaction strength

## Validation
- Compare detected communities with ground truth (if available)
- Verify centrality rankings match known influencers
- Check that cascade size follows expected S-curve

## Extensions
- Temporal network analysis (edges appear/disappear over time)
- Sentiment propagation models
- Bot detection using graph anomalies
- Recommendation systems via link prediction

## Deliverables
- `network_analysis.py` — core analysis library
- `centrality.py` — centrality computations
- `communities.py` — community detection
- `cascade.py` — information spread simulation
- `visualize.py` — network rendering
- `README.md` — theory, usage, and results
