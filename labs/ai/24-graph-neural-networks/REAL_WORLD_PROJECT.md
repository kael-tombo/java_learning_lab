# Graph Neural Networks - REAL WORLD PROJECT

## Project: Social Network Analysis

Build a GNN-based system for social network analysis and recommendation.

### Architecture

```
Social Graph → GCN → Node Embeddings → Link Prediction → Friend Recommendations
```

### Implementation

```java
public class SocialNetworkAnalyzer {
    private GCN gcn;
    private LinkPredictor predictor;
    
    public void buildGraph(SocialNetwork network) {
        // Build adjacency matrix from friendships
        double[][] adjacency = buildAdjacencyMatrix(network);
        double[][] features = buildNodeFeatures(network);
        
        // Train GCN
        gcn = new GCN(features[0].length, 64, 32);
        gcn.setGraph(adjacency, features);
        gcn.train(network.getLabels(), 200);
    }
    
    public List<User> recommendFriends(User user, int n) {
        // Get node embedding
        double[] embedding = gcn.getNodeEmbedding(user.getId());
        
        // Score all non-friends
        List<ScoredUser> candidates = new ArrayList<>();
        for (User candidate : getAllUsers()) {
            if (!user.isFriend(candidate)) {
                double[] candidateEmb = gcn.getNodeEmbedding(candidate.getId());
                double score = predictor.predict(embedding, candidateEmb);
                candidates.add(new ScoredUser(candidate, score));
            }
        }
        
        // Return top-n
        return candidates.stream()
            .sorted(Comparator.comparing(ScoredUser::getScore).reversed())
            .limit(n)
            .map(ScoredUser::getUser)
            .collect(Collectors.toList());
    }
    
    public Community detectCommunity(User user) {
        double[] embedding = gcn.getNodeEmbedding(user.getId());
        return communityDetector.classify(embedding);
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- GNNs are powerful for social network analysis due to their ability to capture graph structure.
- Reference: https://arxiv.org/abs/1609.02907
- Reference: https://pytorch-geometric.readthedocs.io/en/latest/

## Deliverables

- [x] Social graph construction
- [x] GCN training
- [x] Node embedding extraction
- [x] Link prediction
- [x] Friend recommendation system
