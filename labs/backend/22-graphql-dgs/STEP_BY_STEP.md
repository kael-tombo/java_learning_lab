# Step by Step: GraphQL DGS

## Step 1: Schema
`graphql
# schema/show-schema.graphqls
type Query {
    shows: [Show]
    show(id: ID!): Show
}

type Show {
    id: ID!
    title: String!
    releaseYear: Int!
    rating: Float
}
`

## Step 2: Resolver
`java
@DgsComponent
public class ShowResolver {
    private final ShowService showService;

    @DgsQuery
    public List<Show> shows() {
        return showService.getAllShows();
    }

    @DgsQuery
    public Show show(@InputArgument String id) {
        return showService.getShow(id);
    }
}
`

## Step 3: Data Loader
`java
@DgsDataLoader(name = "reviewLoader")
public class ReviewLoader implements BatchLoader<String, List<Review>> {
    @Override
    public CompletionStage<List<List<Review>>> load(List<String> showIds) {
        return CompletableFuture.supplyAsync(() -> reviewService.getReviewsForShows(showIds));
    }
}
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\22-graphql-dgs "CODE_DEEP_DIVE.md") @"
# Code Deep Dive: GraphQL DGS

## DGS Framework Internals
DGS uses GraphQL-Java underneath. The framework:
1. Parses schema files (.graphqls) on startup
2. Creates GraphQLSchema object
3. Scans for @DgsComponent classes
4. Registers data fetchers for each field
5. Handles request execution pipeline

## Data Loader Batching
DataLoaderRegistry creates DataLoader instances. Each DataLoader:
- Collects keys until flush point
- Executes batch load function
- Caches results for same request
- Returns CompletableFuture per key
