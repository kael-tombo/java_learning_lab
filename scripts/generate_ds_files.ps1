$ErrorActionPreference = "Stop"
$base = "C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\data-science"

function Generate-FileContent {
    param($FileType, $Topic)
    $title = $Topic.Title
    $desc = $Topic.Desc
    $key = $Topic.Key

    switch ($FileType) {
        "README.md" {
            return @"
# $title

Welcome to the atomic mastery lab for **$title**. This lab is part of the Data Science Academy.

## What You Will Master
- $desc
- Core concepts: $key
- Practical implementation in Java
- Real-world application scenarios

## Lab Structure
1. [THEORY.md](./THEORY.md) - Theoretical foundations and intuition
2. [MATH_FOUNDATION.md](./MATH_FOUNDATION.md) - Mathematical underpinnings
3. [CODE_DEEP_DIVE.md](./CODE_DEEP_DIVE.md) - Pure Java implementation
4. [EXERCISES.md](./EXERCISES.md) - Hands-on practice problems
5. [QUIZ.md](./QUIZ.md) - Knowledge assessment
6. [FLASHCARDS.md](./FLASHCARDS.md) - Quick review cards
7. [VISION.md](./VISION.md) - Future applications and trends
8. [MINI_PROJECT.md](./MINI_PROJECT.md) - Guided mini project
9. [REAL_WORLD_PROJECT.md](./REAL_WORLD_PROJECT.md) - Production-grade project

## Prerequisites
- Basic Java programming
- Fundamental statistics knowledge
- Familiarity with data structures

## Estimated Time
- Theory: 2-3 hours
- Exercises: 3-4 hours
- Projects: 4-6 hours
"@
        }
        "THEORY.md" {
            return @"
# $title - Theory & Intuition

## The Big Picture

$desc is a cornerstone of modern data science. Understanding both the theoretical foundations and practical implications is essential for building robust data-driven systems.

## Core Concepts

### 1. Foundations
The field of $title draws from statistics, computer science, and domain expertise. The key challenge is transforming raw, messy data into actionable insights through systematic $key.

### 2. Why It Matters
In production systems, $title directly impacts model quality, business decisions, and operational efficiency. Poor practices lead to inaccurate predictions, biased outcomes, and wasted computational resources.

### 3. Key Principles
- **Reproducibility**: Every step must be documented and repeatable
- **Scalability**: Solutions must handle growing data volumes
- **Robustness**: Systems must gracefully handle edge cases and anomalies
- **Interpretability**: Results must be explainable to stakeholders

## Theoretical Framework

### Statistical Foundations
Understanding probability distributions, sampling theory, and estimation is crucial. The bias-variance tradeoff governs model complexity decisions.

### Computational Considerations
Algorithmic complexity matters. O(n log n) sorting enables efficient processing of large datasets, while O(n^2) approaches become prohibitive at scale.

### Data Quality Dimensions
- **Accuracy**: Correctness of values
- **Completeness**: Absence of missing data
- **Consistency**: Uniformity across sources
- **Timeliness**: Data freshness and relevance

## Common Pitfalls
1. **Overfitting**: Model memorizes training data instead of learning patterns
2. **Data Leakage**: Information from test set influences training
3. **Confounding**: Hidden variables create spurious correlations
4. **Selection Bias**: Non-representative sampling skews results

## Best Practices
- Always validate assumptions before applying techniques
- Document all transformations and decisions
- Use version control for data and code
- Implement automated testing for data pipelines

## Summary
Mastering $title requires balancing theoretical rigor with practical constraints. The following sections provide mathematical foundations and implementation details.
"@
        }
        "EXERCISES.md" {
            return @"
# $title - Exercises

## Exercise 1: Basic Concepts
Implement a Java class that demonstrates fundamental $title operations. Create methods for data input, processing, and output validation.

**Requirements**:
- Use appropriate data structures
- Include input validation
- Add comprehensive error handling
- Write unit tests for each method

## Exercise 2: Data Processing Pipeline
Build a multi-step processing pipeline that chains transformations together. Each step should be independently testable.

**Requirements**:
- Implement at least 3 transformation steps
- Support configurable parameters
- Include logging for each step
- Handle edge cases gracefully

## Exercise 3: Statistical Analysis
Create a utility class that computes descriptive statistics (mean, median, mode, standard deviation, variance) on a dataset.

**Requirements**:
- Handle empty datasets
- Support streaming data
- Optimize for large datasets
- Include confidence interval calculation

## Exercise 4: Visualization Helper
Implement a simple text-based visualization tool that generates ASCII charts from data arrays.

**Requirements**:
- Support bar charts and line charts
- Auto-scale axes
- Add labels and legends
- Export to file

## Exercise 5: Performance Optimization
Take a naive O(n^2) implementation and optimize it to O(n log n) or better.

**Requirements**:
- Benchmark before and after
- Document the optimization strategy
- Verify correctness is maintained
- Measure memory usage

## Exercise 6: Integration Test
Create an end-to-end test that processes a sample dataset through your entire pipeline.

**Requirements**:
- Use realistic test data
- Verify output correctness
- Test error conditions
- Measure execution time

## Exercise 7: Design Pattern Application
Refactor your code to use appropriate design patterns (Strategy, Factory, Observer).

**Requirements**:
- Identify applicable patterns
- Implement clean interfaces
- Document design decisions
- Ensure extensibility

## Exercise 8: Documentation
Write comprehensive JavaDoc for all public classes and methods.

**Requirements**:
- Include usage examples
- Document parameters and return values
- Add @throws annotations
- Create a README for your module
"@
        }
        "QUIZ.md" {
            return @"
# $title - Quiz

## Question 1
What is the primary goal of $title?
A) Data storage optimization
B) $desc
C) Network security
D) User interface design

**Answer**: B

## Question 2
Which of the following is NOT a data quality dimension?
A) Accuracy
B) Completeness
C) Complexity
D) Consistency

**Answer**: C

## Question 3
What does the bias-variance tradeoff describe?
A) Speed vs. accuracy
B) Model complexity vs. generalization
C) Storage vs. computation
D) Input vs. output size

**Answer**: B

## Question 4
Which algorithmic complexity is preferred for large datasets?
A) O(n^2)
B) O(2^n)
C) O(n log n)
D) O(n!)

**Answer**: C

## Question 5
What is data leakage?
A) Data corruption during transfer
B) Test set information influencing training
C) Unauthorized data access
D) Data format incompatibility

**Answer**: B

## Question 6
Which design pattern is best for interchangeable algorithms?
A) Singleton
B) Strategy
C) Observer
D) Factory

**Answer**: B

## Question 7
What is the purpose of cross-validation?
A) Reduce training time
B) Assess model generalization
C) Increase model complexity
D) Simplify data preprocessing

**Answer**: B

## Question 8
Which measure is robust to outliers?
A) Mean
B) Standard deviation
C) Median
D) Range

**Answer**: C

## Question 9
What does reproducibility ensure?
A) Fast execution
B) Consistent results across runs
C) Low memory usage
D) Simple code

**Answer**: B

## Question 10
What is the first step in a data science project?
A) Model training
B) Data collection
C) Problem definition
D) Feature engineering

**Answer**: C
"@
        }
        "FLASHCARDS.md" {
            return @"
# $title - Flashcards

## Card 1
**Q**: What is $title?
**A**: $desc

## Card 2
**Q**: Name three data quality dimensions.
**A**: Accuracy, Completeness, Consistency

## Card 3
**Q**: What is the bias-variance tradeoff?
**A**: The balance between model simplicity (high bias) and complexity (high variance) to achieve optimal generalization.

## Card 4
**Q**: What is overfitting?
**A**: When a model learns training data too well, including noise, and fails to generalize to new data.

## Card 5
**Q**: What is data leakage?
**A**: When information from outside the training dataset (especially test data) is used to create the model.

## Card 6
**Q**: What does O(n log n) represent?
**A**: Algorithmic complexity that scales efficiently, typical of efficient sorting and divide-and-conquer algorithms.

## Card 7
**Q**: What is cross-validation?
**A**: A technique to assess model performance by partitioning data into subsets, training on some and validating on others.

## Card 8
**Q**: Why is the median robust to outliers?
**A**: It represents the middle value and is not affected by extreme values, unlike the mean.

## Card 9
**Q**: What is reproducibility in data science?
**A**: The ability to obtain consistent results when repeating an analysis with the same data and methods.

## Card 10
**Q**: What is the Strategy pattern?
**A**: A design pattern that defines a family of algorithms, encapsulates each one, and makes them interchangeable.

## Card 11
**Q**: What is a confounding variable?
**A**: An extraneous variable that affects both the dependent and independent variables, creating a spurious association.

## Card 12
**Q**: What is selection bias?
**A**: Error introduced by selecting non-representative samples from a population.

## Card 13
**Q**: What is the purpose of feature scaling?
**A**: To normalize the range of independent variables so that distance-based algorithms perform correctly.

## Card 14
**Q**: What is an imputation strategy?
**A**: A method for filling in missing data values, such as mean, median, or predictive imputation.

## Card 15
**Q**: What is the CRISP-DM methodology?
**A**: Cross-Industry Standard Process for Data Mining - a six-phase process model for data science projects.
"@
        }
        "MATH_FOUNDATION.md" {
            return @"
# $title - Mathematical Foundations

## Probability Theory

### Basic Probability
The foundation of $title rests on probability theory. For events A and B:
- P(A union B) = P(A) + P(B) - P(A intersect B)
- P(A|B) = P(A intersect B) / P(B) (Conditional probability)

### Bayes' Theorem
P(A|B) = P(B|A) x P(A) / P(B)

This is fundamental for updating beliefs with new evidence, central to many $key techniques.

## Descriptive Statistics

### Measures of Central Tendency
- **Mean**: mu = (sum of x_i) / n
- **Median**: Middle value of ordered data
- **Mode**: Most frequent value

### Measures of Dispersion
- **Variance**: sigma^2 = sum of (x_i - mu)^2 / n
- **Standard Deviation**: sigma = sqrt(sigma^2)
- **IQR**: Q3 - Q1 (Interquartile Range)

## Linear Algebra

### Vectors and Matrices
Feature spaces are represented as vectors. Operations include:
- Dot product: a.b = sum of a_i * b_i
- Matrix multiplication: C[i,j] = sum of A[i,k] * B[k,j]
- Transpose: A^T where A^T[i,j] = A[j,i]

### Eigenvalues and Eigenvectors
Av = lambda * v

Critical for dimensionality reduction techniques like PCA, which identify directions of maximum variance.

## Calculus

### Derivatives
Used in optimization algorithms:
- Gradient: grad(f) points in direction of steepest ascent
- Partial derivatives: df/dx_i for multivariate functions

### Chain Rule
df/dx = df/dg * dg/dx

Essential for backpropagation in neural networks and gradient-based optimization.

## Optimization

### Gradient Descent
theta_next = theta - alpha * grad(J(theta))

Where alpha is the learning rate. This iterative approach minimizes loss functions in model training.

### Convexity
A function is convex if f(lambda*x + (1-lambda)*y) <= lambda*f(x) + (1-lambda)*f(y). Convex problems have unique global minima.

## Information Theory

### Entropy
H(X) = -sum of p(x) * log(p(x))

Measures uncertainty in a random variable, foundational for decision trees and feature selection.

### Mutual Information
I(X;Y) = H(X) - H(X|Y)

Quantifies the information gained about one variable through another.

## Summary
These mathematical foundations enable rigorous understanding of $title algorithms and their behavior under various conditions.
"@
        }
        "CODE_DEEP_DIVE.md" {
            return @"
# $title - Code Deep Dive

## Architecture Overview

The Java implementation of $title follows clean architecture principles with clear separation of concerns.

## Core Classes

### DataProcessor Interface
```java
public interface DataProcessor<T, R> {
    R process(T input);
    void validate(T input);
    default R processWithLogging(T input) {
        long start = System.nanoTime();
        R result = process(input);
        long duration = System.nanoTime() - start;
        System.out.printf("Processed in %d ns%n", duration);
        return result;
    }
}
```

### Pipeline Pattern
```java
public class ProcessingPipeline<T> {
    private final List<DataProcessor<T, T>> steps = new ArrayList<>();

    public ProcessingPipeline<T> addStep(DataProcessor<T, T> step) {
        steps.add(step);
        return this;
    }

    public T execute(T input) {
        T result = input;
        for (DataProcessor<T, T> step : steps) {
            step.validate(result);
            result = step.process(result);
        }
        return result;
    }
}
```

## Implementation Details

### Memory Management
- Use primitive arrays where possible to avoid boxing overhead
- Implement streaming for large datasets
- Leverage Java's garbage collection with proper scoping

### Concurrency
```java
public class ParallelProcessor {
    private final ExecutorService executor = Executors.newFixedThreadPool(
        Runtime.getRuntime().availableProcessors()
    );

    public List<Future<Result>> processBatch(List<Task> tasks) {
        return tasks.stream()
            .map(t -> executor.submit(() -> t.execute()))
            .collect(Collectors.toList());
    }
}
```

### Error Handling
- Use custom exceptions for domain-specific errors
- Implement retry logic with exponential backoff
- Log errors with context for debugging

## Performance Considerations

### Benchmarking
Use JMH (Java Microbenchmark Harness) for accurate performance measurement:
```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
public class ProcessorBenchmark {
    @Benchmark
    public void testProcess() {
        // benchmark code
    }
}
```

### Optimization Strategies
1. **Lazy evaluation**: Defer computation until needed
2. **Memoization**: Cache expensive function results
3. **Parallel streams**: Leverage multi-core processors
4. **Primitive specialization**: Avoid autoboxing

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Use JUnit 5 with parameterized tests
- Mock dependencies with Mockito

### Integration Tests
- Test component interactions
- Use test containers for external dependencies
- Verify end-to-end data flow

### Property-Based Tests
- Use jqwik for generating test cases
- Verify invariants hold across inputs
- Find edge cases automatically

## Summary
This implementation provides a robust, scalable foundation for $title with clean APIs, comprehensive testing, and production-ready error handling.
"@
        }
        "VISION.md" {
            return @"
# $title - Vision & Future Directions

## Current State

$title continues to evolve rapidly with new algorithms, tools, and methodologies emerging regularly. The field is moving toward greater automation, interpretability, and accessibility.

## Emerging Trends

### Automated Machine Learning (AutoML)
AutoML platforms are democratizing $title by automating feature selection, model selection, and hyperparameter tuning. This enables domain experts to build models without deep ML expertise.

### Explainable AI (XAI)
As models become more complex, the demand for interpretability grows. Techniques like SHAP, LIME, and attention visualization are becoming standard requirements.

### Federated Learning
Privacy-preserving techniques allow model training across decentralized data sources without centralizing sensitive information.

### Edge Computing
Deploying $title capabilities on edge devices reduces latency and bandwidth requirements, enabling real-time decision making.

## Technology Evolution

### Language Models
Large language models are transforming how we interact with data, enabling natural language interfaces for $title tasks.

### Vector Databases
Specialized databases for similarity search are enabling efficient retrieval-augmented generation and semantic search.

### Real-Time Processing
Stream processing frameworks are enabling real-time $title with sub-second latency requirements.

## Future Applications

### Personalized Medicine
$title will enable treatment plans tailored to individual genetic profiles and medical histories.

### Climate Modeling
Advanced techniques will improve climate predictions and help develop mitigation strategies.

### Scientific Discovery
Automated hypothesis generation and testing will accelerate scientific research across domains.

## Skills for the Future

To stay relevant, practitioners should develop:
- Strong software engineering fundamentals
- Cloud computing and distributed systems expertise
- Domain knowledge in their area of application
- Communication and storytelling skills

## Conclusion

The future of $title is bright, with expanding applications across every industry. Continuous learning and adaptation will be essential for success in this dynamic field.
"@
        }
        "MINI_PROJECT.md" {
            return @"
# $title - Mini Project

## Project Overview

Build a complete $title application that demonstrates core concepts through a practical, self-contained implementation.

## Project Goals
- Apply theoretical knowledge to a concrete problem
- Practice software engineering best skills
- Create a portfolio-worthy deliverable
- Demonstrate end-to-end understanding

## Requirements

### Functional Requirements
1. **Data Ingestion**: Load data from CSV/JSON files
2. **Processing Pipeline**: Implement at least 3 transformation steps
3. **Analysis**: Compute relevant statistics and metrics
4. **Output**: Generate reports and visualizations
5. **CLI Interface**: Accept command-line arguments

### Non-Functional Requirements
1. **Performance**: Process 10,000 records in under 5 seconds
2. **Test Coverage**: Minimum 80% code coverage
3. **Documentation**: Complete JavaDoc and README
4. **Error Handling**: Graceful handling of all error cases

## Project Structure
```
src/
+-- main/java/com/ds/mini/
|   +-- Main.java
|   +-- data/
|   |   +-- DataLoader.java
|   |   +-- DataValidator.java
|   +-- processing/
|   |   +-- Pipeline.java
|   |   +-- transformers/
|   +-- analysis/
|   |   +-- StatisticsEngine.java
|   +-- report/
|       +-- ReportGenerator.java
+-- test/java/com/ds/mini/
    +-- (corresponding tests)
```

## Implementation Steps

### Step 1: Project Setup
- Create Maven/Gradle project structure
- Configure dependencies (JUnit, Apache Commons, etc.)
- Set up logging framework

### Step 2: Data Layer
- Implement DataLoader with support for multiple formats
- Create DataValidator with comprehensive checks
- Add custom exceptions for data errors

### Step 3: Processing Pipeline
- Design transformer interface
- Implement concrete transformers
- Add pipeline orchestration

### Step 4: Analysis Engine
- Implement statistical calculations
- Add aggregation functions
- Create result data structures

### Step 5: Reporting
- Generate text-based reports
- Create simple visualizations
- Export results to files

### Step 6: Testing
- Write unit tests for all components
- Add integration tests
- Verify performance requirements

## Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Functionality | 30% | All features work correctly |
| Code Quality | 25% | Clean, maintainable, well-documented |
| Testing | 20% | Comprehensive test coverage |
| Performance | 15% | Meets performance requirements |
| Documentation | 10% | Clear, complete documentation |

## Submission
- Source code in Git repository
- README with setup instructions
- Demo video or screenshots
- Test results report

## Timeline
- Week 1: Setup and data layer
- Week 2: Processing pipeline
- Week 3: Analysis and reporting
- Week 4: Testing and documentation
"@
        }
        "REAL_WORLD_PROJECT.md" {
            return @"
# $title - Real-World Project

## Project Overview

This project implements a production-grade $title system designed for real-world deployment. It addresses practical challenges including scalability, reliability, and maintainability.

## Sourced field notes (fetched Oct 2026 - verify before citing)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/) - Production workflow orchestration patterns
- [Google MLOps Guide](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) - CI/CD for machine learning best practices

## System Architecture

### High-Level Design
```
+-------------+     +--------------+     +-------------+
| Data Sources |---->| Ingestion    |---->| Processing  |
| (DB, API,    |     | Layer        |     | Engine      |
|  Files)      |     |              |     |             |
+-------------+     +--------------+     +------+------+
                                               |
                    +--------------+     +------v------+
                    | Monitoring   |<----| Storage     |
                    | & Alerting   |     | Layer       |
                    +--------------+     +-------------+
```

### Components

#### 1. Data Ingestion Service
- REST API endpoints for data submission
- Message queue integration for async processing
- Data validation and schema enforcement
- Rate limiting and authentication

#### 2. Processing Engine
- Distributed task execution
- Fault tolerance with retry mechanisms
- Horizontal scaling support
- Real-time and batch processing modes

#### 3. Storage Layer
- Relational database for structured data
- Object storage for large files
- Cache layer for frequently accessed data
- Data versioning and lineage tracking

#### 4. Monitoring & Observability
- Metrics collection (Prometheus)
- Distributed tracing (OpenTelemetry)
- Centralized logging (ELK stack)
- Alerting and dashboards (Grafana)

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Java 21 | Core development |
| Framework | Spring Boot | Application framework |
| Database | PostgreSQL | Primary data store |
| Cache | Redis | Caching layer |
| Queue | Apache Kafka | Message streaming |
| Orchestration | Apache Airflow | Workflow management |
| Container | Docker | Deployment |
| Orchestration | Kubernetes | Container orchestration |

## Implementation Details

### API Design
```java
@RestController
@RequestMapping("/api/v1/processing")
public class ProcessingController {

    @PostMapping("/jobs")
    public ResponseEntity<JobResponse> submitJob(
        @Valid @RequestBody JobRequest request
    ) {
        // Implementation
    }

    @GetMapping("/jobs/{jobId}")
    public ResponseEntity<JobStatus> getJobStatus(
        @PathVariable String jobId
    ) {
        // Implementation
    }
}
```

### Data Models
```java
@Entity
@Table(name = "processing_jobs")
public class ProcessingJob {
    @Id
    private String jobId;
    private JobStatus status;
    private String inputPath;
    private String outputPath;
    private Instant createdAt;
    private Instant updatedAt;
    // Getters, setters, builders
}
```

### Error Handling
- Global exception handler with structured error responses
- Circuit breaker pattern for external service calls
- Dead letter queue for failed messages
- Comprehensive audit logging

## Deployment

### Docker Configuration
```dockerfile
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-XX:+UseG1GC", "-jar", "app.jar"]
```

### Kubernetes Deployment
- Horizontal Pod Autoscaler for dynamic scaling
- Rolling updates for zero-downtime deployments
- ConfigMaps and Secrets for configuration
- Persistent volumes for data storage

## Security Considerations

### Authentication & Authorization
- OAuth 2.0 / JWT for API authentication
- Role-based access control (RBAC)
- API key management for service-to-service communication

### Data Protection
- Encryption at rest and in transit
- PII detection and masking
- Data retention policies
- GDPR compliance measures

## Performance Optimization

### Caching Strategy
- Multi-level caching (in-memory + distributed)
- Cache invalidation patterns
- Pre-computation of expensive queries

### Database Optimization
- Indexing strategy for common queries
- Connection pooling
- Read replicas for query scaling
- Partitioning for large tables

## Testing Strategy

### Test Pyramid
- Unit tests: 70% coverage
- Integration tests: 20% coverage
- End-to-end tests: 10% coverage

### Quality Gates
- Static code analysis (SonarQube)
- Dependency vulnerability scanning
- Performance regression testing
- Chaos engineering experiments

## Monitoring & Alerting

### Key Metrics
- Request rate and latency
- Error rates
- Resource utilization
- Business KPIs

### Alert Rules
- Error rate > 5% for 5 minutes
- Latency p99 > 1 second
- Disk usage > 80%
- Failed job count > threshold

## Maintenance

### Backup Strategy
- Automated daily backups
- Point-in-time recovery
- Cross-region replication
- Regular restore testing

### Disaster Recovery
- RPO: 1 hour
- RTO: 4 hours
- Failover procedures
- Regular DR drills

## Future Enhancements
- Machine learning for anomaly detection
- Auto-scaling based on predictive models
- Multi-region deployment
- Advanced analytics and reporting
"@
        }
    }
}

$topics = @{
    "01-data-wrangling" = @{ Title = "Data Wrangling"; Desc = "Cleaning, transforming, and preparing raw data for analysis"; Key = "data cleaning, missing values, normalization, encoding" }
    "02-eda" = @{ Title = "Exploratory Data Analysis"; Desc = "Systematic exploration of data to discover patterns and anomalies"; Key = "EDA, summary statistics, distribution analysis, correlation" }
    "02-visualization" = @{ Title = "Data Visualization"; Desc = "Visual representation of data for insight communication"; Key = "charts, plots, dashboards, visual encoding" }
    "03-exploratory-analysis" = @{ Title = "Exploratory Analysis"; Desc = "Deep dive into data exploration techniques and pattern discovery"; Key = "pattern discovery, hypothesis generation, data profiling" }
    "03-feature-engineering" = @{ Title = "Feature Engineering"; Desc = "Creating and selecting features to improve model performance"; Key = "feature creation, transformation, selection" }
    "04-feature-engineering" = @{ Title = "Feature Engineering"; Desc = "Advanced feature engineering techniques for ML pipelines"; Key = "polynomial features, interaction terms, domain features" }
    "04-time-series" = @{ Title = "Time Series Analysis"; Desc = "Analyzing time-ordered data for forecasting and trends"; Key = "trend, seasonality, autocorrelation, forecasting" }
    "05-time-series" = @{ Title = "Time Series Forecasting"; Desc = "Advanced forecasting methods and temporal pattern modeling"; Key = "ARIMA, exponential smoothing, Prophet" }
    "06-causal-inference" = @{ Title = "Causal Inference"; Desc = "Determining cause-effect relationships from observational data"; Key = "causality, counterfactuals, treatment effects" }
    "07-experimentation" = @{ Title = "Experimentation"; Desc = "Designing and analyzing experiments including A/B testing"; Key = "A/B testing, hypothesis testing, statistical significance" }
    "08-bayesian-statistics" = @{ Title = "Bayesian Statistics"; Desc = "Probabilistic reasoning with prior knowledge and updating beliefs"; Key = "Bayes theorem, priors, posteriors, MCMC" }
    "09-dimension-reduction" = @{ Title = "Dimensionality Reduction"; Desc = "Reducing feature space while preserving information"; Key = "PCA, t-SNE, UMAP, feature selection" }
    "10-clustering-advanced" = @{ Title = "Advanced Clustering"; Desc = "Sophisticated clustering algorithms and evaluation techniques"; Key = "DBSCAN, hierarchical clustering, silhouette score" }
    "11-nlp-advanced" = @{ Title = "Advanced NLP"; Desc = "Deep learning and transformer-based natural language processing"; Key = "transformers, BERT, embeddings, attention" }
    "12-ensemble-methods" = @{ Title = "Ensemble Methods"; Desc = "Combining multiple models for improved predictions"; Key = "bagging, boosting, stacking, random forest" }
    "13-model-evaluation" = @{ Title = "Model Evaluation"; Desc = "Metrics and techniques for assessing model performance"; Key = "precision, recall, F1, ROC-AUC, cross-validation" }
    "14-unsupervised-learning" = @{ Title = "Unsupervised Learning"; Desc = "Finding structure in unlabeled data"; Key = "clustering, anomaly detection, association rules" }
    "15-data-pipelines" = @{ Title = "Data Pipelines"; Desc = "Building robust ETL and data processing workflows"; Key = "ETL, Apache Airflow, data orchestration" }
    "analysis-deep" = @{ Title = "Analysis Deep Dive"; Desc = "Comprehensive analytical techniques and methodologies"; Key = "deep analysis, statistical modeling, insight generation" }
    "data-science-deep" = @{ Title = "Data Science Deep Dive"; Desc = "End-to-end data science methodology and best practices"; Key = "CRISP-DM, data science lifecycle, best practices" }
    "ml-pipelines-deep" = @{ Title = "ML Pipelines Deep Dive"; Desc = "Production machine learning pipeline architecture and MLOps"; Key = "MLOps, model serving, feature stores, monitoring" }
}

$fileTypes = @("README.md","THEORY.md","EXERCISES.md","QUIZ.md","FLASHCARDS.md","MATH_FOUNDATION.md","CODE_DEEP_DIVE.md","VISION.md","MINI_PROJECT.md","REAL_WORLD_PROJECT.md")

foreach ($dir in $topics.Keys | Sort-Object) {
    $topic = $topics[$dir]
    $dirPath = Join-Path $base $dir
    if (-not (Test-Path $dirPath)) { New-Item -ItemType Directory -Path $dirPath -Force | Out-Null }

    foreach ($ft in $fileTypes) {
        $filePath = Join-Path $dirPath $ft
        if (Test-Path $filePath) { continue }

        $content = Generate-FileContent -FileType $ft -Topic $topic
        Set-Content -Path $filePath -Value $content -Encoding UTF8
        Write-Output "Created: $dir/$ft"
    }
}
