# Recommendation Systems - REAL WORLD PROJECT

## Project: Movie Recommendation Engine

Build a complete movie recommendation system.

### Architecture

```
User Ratings → Matrix Factorization → Candidate Generation → Re-ranking → Recommendations
```

### Implementation

```java
public class MovieRecommender {
    private MatrixFactorization mf;
    private ContentBasedFilter contentFilter;
    private ReRanker reRanker;
    
    public void train(List<Rating> ratings) {
        // Build user-item matrix
        double[][] matrix = buildRatingMatrix(ratings);
        
        // Train matrix factorization
        mf = new MatrixFactorization(50, 0.01, 0.02);
        mf.train(matrix, 100);
        
        // Train content-based model
        contentFilter = new ContentBasedFilter();
        contentFilter.train(movieFeatures);
    }
    
    public List<Movie> recommend(User user, int n) {
        // Generate candidates from MF
        List<Integer> candidates = mf.getCandidateItems(user.getId(), 100);
        
        // Score with content-based model
        List<ScoredMovie> scored = candidates.stream()
            .map(m -> new ScoredMovie(m, contentFilter.score(user, m)))
            .collect(Collectors.toList());
        
        // Re-rank with diversity and freshness
        return reRanker.rerank(scored, n);
    }
    
    public double evaluate(List<Rating> testRatings) {
        double rmse = 0;
        for (Rating r : testRatings) {
            double pred = mf.predict(r.getUserId(), r.getMovieId());
            rmse += Math.pow(r.getRating() - pred, 2);
        }
        return Math.sqrt(rmse / testRatings.size());
    }
}
```

### Sourced field notes (fetched Oct 2026 — verify before citing)
- The Netflix Prize popularized matrix factorization techniques for recommendation.
- Reference: https://www.netflixprize.com/
- Reference: https://grouplens.org/datasets/movielens/

## Deliverables

- [x] Matrix factorization model
- [x] Content-based filtering
- [x] Hybrid recommendation approach
- [x] Re-ranking with diversity
- [x] Evaluation with RMSE and NDCG
