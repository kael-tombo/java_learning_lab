# Databricks AI/ML Interview Guide

## Table of Contents
1. [Company Overview](#company-overview)
2. [Company Background & Platform](#company-background--platform)
3. [Interview Process Overview](#interview-process-overview)
4. [Role Types](#role-types)
5. [MLflow Architecture & Internals](#mlflow-architecture--internals)
6. [Delta Lake for ML](#delta-lake-for-ml)
7. [Spark ML Pipelines](#spark-ml-pipelines)
8. [Feature Stores & Unity Catalog](#feature-stores--unity-catalog)
9. [ML System Design Topics](#ml-system-design-topics)
10. [MLOps & Model Serving](#mlops--model-serving)
11. [Coding Expectations](#coding-expectations)
12. [Behavioral Questions](#behavioral-questions)
13. [Sample Questions & Answers](#sample-questions--answers)
14. [Resources & Further Reading](#resources--further-reading)

---

## Company Overview

- **Founded:** 2013
- **Founders:** Ion Stoica, Matei Zaharia, Patrick Wendell, Reynold Xin, Andy Konwinski, Arsalan Tavakoli
- **Headquarters:** San Francisco, CA
- **Key Product:** Databricks Lakehouse Platform (unifies data + AI)
- **Funding:** Over $3.5B raised
- **Valuation:** $43B (2023)
- **Employees:** ~5,000+
- **Key Open Source:** Apache Spark, MLflow, Delta Lake, Unity Catalog

Databricks originated as the commercial entity behind Apache Spark and has evolved into a comprehensive data and AI platform combining data engineering, data science, and ML on a unified lakehouse architecture.

---

## Company Background & Platform

### The Lakehouse Vision
Databricks pioneered the lakehouse architecture, combining the flexibility of a data lake (cheap storage, all data types) with the reliability and ACID guarantees of a data warehouse.

### Key Platform Components

1. **Apache Spark:** Unified analytics engine for large-scale data processing
2. **Delta Lake:** Open-source storage layer with ACID transactions
3. **MLflow:** Open-source ML lifecycle management
4. **Unity Catalog:** Unified governance layer
5. **Databricks SQL:** SQL analytics on the lakehouse
6. **Feature Store:** Centralized feature management for ML
7. **Model Serving:** Production ML inference infrastructure
8. **AutoML:** Automated model development

### Competitive Positioning
- **vs Snowflake:** Databricks is stronger for ML/AI workloads; Snowflake stronger for pure SQL analytics
- **vs AWS SageMaker:** Databricks integrates data engineering and ML on one platform; SageMaker is pure ML
- **vs Google Vertex AI:** Similar full-stack ML platform with different cloud ecosystems

---

## Interview Process Overview

### Stage 1: Recruiter Screen (30 minutes)
- Background and experience
- Role expectations
- Interest in data + AI platform work

### Stage 2: Technical Phone Screen (60 minutes)
- **ML-focused roles:** ML coding, ML concepts
- **Engineering roles:** Algorithms and data structures
- May include system design for senior roles

### Stage 3: Virtual Onsite (4-5 hours)

**Typical schedule:**

1. **ML Coding (60 min)**
   - Implement ML algorithms from scratch
   - PySpark coding for ML pipelines
   - Distributed ML implementation

2. **ML System Design (60 min)**
   - Building ML platforms at scale
   - Feature engineering and serving pipelines
   - Model deployment and monitoring

3. **Algorithms & Data Structures (45-60 min)**
   - LeetCode medium-hard problems
   - Focus on data-intensive algorithms

4. **Behavioral & Leadership (45 min)**
   - Technical leadership
   - Cross-functional collaboration
   - Product thinking

5. **ML Fundamentals (45-60 min)**
   - Deep learning, classical ML, MLOps
   - Distributed training concepts
   - Model evaluation and validation

---

## Role Types

### 1. Machine Learning Engineer (MLE)
- **Focus:** Building ML infrastructure, deploying models at scale
- **Key Skills:** PySpark, MLflow, distributed systems, MLOps
- **Interview Weight:** ML System Design (35%), ML Coding (30%), Fundamentals (20%), Behavioral (15%)

### 2. Applied ML Scientist
- **Focus:** Developing ML models for Databricks products and customer use cases
- **Key Skills:** Deep learning, NLP, classical ML, experiment design
- **Interview Weight:** ML Knowledge (40%), ML Coding (30%), Design (15%), Behavioral (15%)

### 3. ML Platform Engineer
- **Focus:** Building the platforms that power Databricks ML offerings
- **Key Skills:** Distributed systems, infrastructure, Spark, MLflow
- **Interview Weight:** System Design (40%), Coding (35%), ML Knowledge (25%)

### 4. Software Engineer (Data/Spark)
- **Focus:** Core platform engineering (Spark, Delta Lake, SQL)
- **Key Skills:** Scala/Java, distributed systems, query optimization
- **Interview Weight:** Coding (50%), System Design (30%), Distributed Systems (20%)

### 5. Solutions Architect / Customer Engineer
- **Focus:** Helping customers adopt Databricks for ML
- **Key Skills:** Full-stack ML knowledge, communication, hands-on coding
- **Interview Weight:** ML Knowledge (35%), Communication (30%), Technical (20%), Design (15%)

---

## MLflow Architecture & Internals

### MLflow Overview
MLflow is an open-source platform for managing the ML lifecycle with four core components:

### 1. MLflow Tracking

**Architecture:**
- **Client:** Python, R, Java, REST APIs
- **Backend Store:** Stores experiment metadata (SQL database)
- **Artifact Store:** Stores models, data, plots (S3, DBFS, ADLS, GCS)

**Key Concepts:**
- **Experiments:** Logical grouping of runs
- **Runs:** Single execution of ML code
- **Parameters:** Key-value pairs for hyperparameters
- **Metrics:** Numerical values tracked over time
- **Artifacts:** Files (model checkpoints, plots, data)
- **Tags:** Custom metadata for organization

**Tracing:**
- Automatic logging for popular frameworks (Keras, PyTorch, Sklearn)
- Custom metric logging with `log_metric()`
- Nested runs for hierarchical experiments
- Search and compare across experiments

### 2. MLflow Projects

**Purpose:** Reproducible packaging of ML code

**Format:**
- `MLproject` file specifying environment and entry points
- Conda environment or Docker container
- Parameters with types and defaults

**Execution:**
- Local runs
- Remote runs (Databricks, Kubernetes)
- Parameter passing and logging integration

### 3. MLflow Models

**Model Format:**
- **MLmodel file:** YAML describing model flavor, signature, dependencies
- **Model flavors:** python_function, sklearn, pytorch, tensorflow, keras, onnx
- **Signature:** Input/output schema with column names and types

**Model Registry:**
- Centralized model versioning
- Stage transitions (Staging → Production → Archived)
- Approval workflows for model promotion
- Model lineage tracking

**Deployment:**
- Local serving with `mlflow models serve`
- Docker container export
- Integration with Databricks Model Serving
- AWS SageMaker, Azure ML, GCP Vertex AI deployment

### 4. MLflow Evaluation

**Purpose:** Evaluate models and compare results

**Features:**
- Built-in evaluation metrics (regression, classification, ranking)
- Automated model comparison
- Explainability (SHAP, permutation importance)
- Custom metric definition

### MLflow at Scale

**Enterprise Features:**
- RBAC for experiments and models
- Multi-user collaboration
- Integration with Unity Catalog
- Audit logging
- Cross-workspace sharing

---

## Delta Lake for ML

### Delta Lake Fundamentals

**Purpose:** Reliable data lake storage with ACID transactions

**Key Features:**
- ACID transactions on data lakes
- Schema enforcement and evolution
- Time travel (data versioning)
- Upserts and merge operations
- Unified batch and streaming
- Data compaction with OPTIMIZE
- Z-ordering for data clustering

### Delta Lake for ML Workloads

**Training Data Management:**
- Store training/validation/test splits as Delta tables
- Version datasets with time travel for reproducibility
- Incremental updates to training data
- Feature data stored in Delta format

**Benefits for ML:**
- **Reproducibility:** Time travel lets you recreate exact training datasets
- **Freshness:** Streaming data updates keep features current
- **Scale:** Handles petabytes of training data
- **Governance:** Unity Catalog integration for data discovery

### Delta Sharing for ML

- Share training datasets across teams
- Share features between models
- Open protocol (works across platforms)

---

## Spark ML Pipelines

### Spark MLlib

**Core Components:**
- **Transformer:** Transforms DataFrames (e.g., tokenizer, vector assembler)
- **Estimator:** Learns from data (e.g., regression, classification)
- **Pipeline:** Chains transformers and estimators
- **Param:** Shared parameter interface
- **Evaluator:** Evaluates model performance

**Common MLlib Algorithms:**
- Linear/Logistic Regression
- Decision Trees, Random Forests, GBT
- K-means, Bisecting K-means
- ALS for recommendation
- PCA, SVD for dimensionality reduction
- TF-IDF, Word2Vec for text

### Building ML Pipelines

```python
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier

# Define stages
assembler = VectorAssembler(inputCols=['feature1', 'feature2'], outputCol='features')
scaler = StandardScaler(inputCol='features', outputCol='scaled_features')
classifier = RandomForestClassifier(featuresCol='scaled_features', labelCol='label')

# Create and run pipeline
pipeline = Pipeline(stages=[assembler, scaler, classifier])
model = pipeline.fit(training_data)
```

**Pipeline Advantages:**
- Reproducible workflows
- Easy hyperparameter tuning with `CrossValidator`/`TrainValidationSplit`
- Clear separation of preprocessing and model
- Integrated with MLflow for tracking

### Distributed Training on Spark

**TorchDistributor:**
- Distributed PyTorch training on Spark clusters
- Supports Horovod and TorchDistributed
- Scales across GPU nodes in cluster

**Spark + Deep Learning:**
- Petastorm for efficient data loading from Parquet
- HorovodRunner for distributed TensorFlow/PyTorch
- Hyperopt for distributed hyperparameter optimization

### Hyperparameter Tuning at Scale

**Hyperopt Integration:**
- Distributed hyperparameter search on Spark
- Support for random, TPE, and annealing search algorithms
- Parallel trials across cluster
- MLflow integration for tracking

---

## Feature Stores & Unity Catalog

### Databricks Feature Store

**Purpose:** Centralized repository for ML features

**Key Concepts:**
- **Feature Table:** Logical grouping of features with metadata
- **Feature Function:** On-demand feature computation
- **Feature Lookup:** Serve features for training and inference

**Architecture:**
- Features stored as Delta tables
- Point-in-time correct feature retrieval
- Automatic feature logging during training
- Feature serving with low-latency endpoints

**Workflow:**
1. Create feature table
2. Compute features (batch or streaming)
3. Register features with metadata
4. Create training dataset using `FeatureStoreClient.create_training_set()`
5. Log model with feature lineage
6. Serve features for inference

**Training-Serving Consistency:**
- Same feature computation code for training and inference
- Feature lookup handles point-in-time correctness
- Automatic timestamp alignment

### Unity Catalog

**Purpose:** Unified governance across data, ML, and AI assets

**Key Features:**
- **Three-level namespace:** Catalog → Schema → Object
- **RBAC:** Fine-grained access control
- **Lineage:** Track data sources through transformations to models
- **Discovery:** Search and discover datasets, features, models
- **Audit:** Complete audit trail of access and changes

**ML-Specific:**
- Manage models as first-class catalog objects
- Track model lineage to training data and features
- Govern feature tables alongside other data assets
- Share models across workspaces

---

## ML System Design Topics

### Building ML Platforms at Scale

**Architecture Components:**

1. **Data Layer:**
   - Ingestion pipelines (batch + streaming)
   - Data quality monitoring
   - Data catalog and discovery
   - Feature engineering and storage

2. **Training Layer:**
   - Experiment tracking (MLflow)
   - Distributed training infrastructure
   - Hyperparameter optimization
   - Model evaluation framework

3. **Deployment Layer:**
   - Model registry and versioning
   - A/B testing infrastructure
   - Canary deployments
   - Model monitoring and alerting

4. **Serving Layer:**
   - Real-time inference endpoints
   - Batch inference pipelines
   - Feature serving
   - Model caching

**Key Design Considerations:**
- **Scalability:** Handle thousands of models, millions of predictions
- **Latency:** Real-time vs batch trade-offs
- **Freshness:** Feature staleness requirements
- **Cost:** Compute and storage optimization
- **Governance:** Compliance and audit requirements

### Feature Engineering Pipeline

**Design challenges:**
- Point-in-time correctness for training data
- Handling late-arriving data
- Feature backfilling for historical data
- Online/offline feature consistency

**Approach:**
- Use Delta Lake for immutable feature storage
- Stream or batch compute features with defined windows
- Store feature metadata (computation logic, freshness requirements)
- Use feature store for consistent lookup

### Model Serving Architecture

**Real-time serving:**
- REST endpoints with low-latency requirements
- Model loading and caching strategies
- Autoscaling based on request load
- Shadow traffic for model validation

**Batch serving:**
- Scheduled Spark jobs for periodic inference
- Delta table as input/output
- Incremental processing for new data

**Monitoring and observability:**
- Prediction drift monitoring
- Feature drift detection
- Model performance tracking
- Data quality checks on predictions

### Training Infrastructure

**Distributed training design:**
- Data parallelism for large datasets
- Model parallelism for large models
- Hybrid parallelism for largest workloads
- GPU cluster management and scheduling

**Resource optimization:**
- Spot instance usage for training
- Automatic cluster scaling
- GPU memory profiling
- Training checkpoint strategies

---

## MLOps & Model Serving

### MLOps Maturity Model

**Level 1: Manual**
- Notebook-based development
- Manual deployment
- No monitoring

**Level 2: Automated**
- CI/CD for ML pipelines
- MLflow tracking
- Automated model validation

**Level 3: Governed**
- Model registry with stages
- A/B testing infrastructure
- Automated rollback

**Level 4: Continuous**
- Continuous training and deployment
- Automated retraining triggers
- Full observability

### Model Deployment Strategies

**Blue-Green Deployment:**
- Two identical environments
- Route traffic from blue to green
- Instant rollback capability

**Canary Deployment:**
- Gradually shift traffic percentage
- Monitor performance metrics
- Rollback if degradation detected

**Shadow Deployment:**
- Run new model alongside existing
- Compare results without serving users
- Validate before production traffic

### Model Monitoring

**Key Metrics:**
- **Data drift:** Distribution changes in input features
- **Concept drift:** Changes in relationship between features and target
- **Performance metrics:** Accuracy, precision, recall over time
- **Operational metrics:** Latency, throughput, error rates

**Monitoring Infrastructure:**
- Log predictions and features to Delta tables
- Scheduled monitoring jobs for drift detection
- Alerting on metric thresholds
- Dashboard for model health

### Model Retraining

**Trigger Strategies:**
- Time-based (daily, weekly, monthly)
- Performance-based (degradation threshold)
- Data-based (significant new data arrival)
- Event-based (data distribution shift detected)

**Retraining Pipeline:**
- Automated data refresh
- Hyperparameter re-optimization
- Validation against current production model
- Registry update if improved

---

## Coding Expectations

### PySpark Coding

**Must Know:**
- DataFrame operations (select, filter, groupBy, join, union)
- User-Defined Functions (UDFs) — Python and Pandas UDFs
- Window functions for time-series
- Aggregation and pivoting
- Reading/writing to Delta format
- Spark SQL queries

**Distributed Computing Concepts:**
- Shuffle operations and their cost
- Partitioning and repartitioning
- Broadcast variables and accumulators
- Catalyst optimizer basics
- Tungsten execution engine

**Performance Optimization:**
- Predicate pushdown
- Partition pruning
- Bucketing for joins
- Avoiding shuffles
- Caching strategies
- Adaptive Query Execution (AQE)

### ML Coding

**Common Questions:**
1. **Implement from scratch:**
   - Linear regression with gradient descent
   - Logistic regression
   - Decision tree
   - K-means clustering
   - PCA

2. **Using Spark MLlib:**
   - Build a pipeline with feature engineering
   - Cross-validation with hyperparameter grid
   - Evaluate with multiple metrics
   - Handle categorical and missing data

3. **Feature Engineering:**
   - Write feature computation logic
   - Handle time-series features
   - Implement point-in-time lookups
   - Create feature store integration

### Algorithmic Coding

**Focus for Databricks:**
- Data-intensive algorithms
- Distributed algorithm design
- MapReduce pattern questions

**Typical Topics:**
- Sorting and searching at scale
- Graph processing (PageRank, shortest paths)
- Set operations (union, intersection, distinct)
- Top-K and frequency estimation
- Streaming algorithms

### Example Coding Question

```
"Implement a distributed version of k-means clustering.
Explain how you would parallelize it in Spark."
```

Key points:
- Data parallel: partition points across workers
- Broadcast centroids to all workers
- Map: assign points to nearest centroid
- Reduce: compute new centroids
- Iterate until convergence
- Convergence criteria and initialization strategies

---

## Behavioral Questions

### Technical Leadership

**Expected Questions:**
- "Describe a time you influenced the technical direction of a team."
- "How do you approach technical decision-making?"
- "Tell me about a system you designed and what trade-offs you made."
- "How do you keep up with the rapidly evolving ML landscape?"

**How to Answer Well:**
- Show structured decision-making
- Demonstrate ability to evaluate trade-offs
- Reference specific technical decisions and outcomes
- Show ongoing learning and adaptation

### Cross-Functional Collaboration

**Expected Questions:**
- "How do you work with data engineers vs data scientists vs product managers?"
- "Describe a project where you had to align multiple teams."
- "How do you communicate technical concepts to non-technical stakeholders?"
- "Tell me about a conflict you resolved between engineering and business needs."

**How to Answer Well:**
- Demonstrate empathy for different roles
- Show translation skills between technical and business
- Reference specific cross-functional projects
- Show collaboration over competition

### Product Thinking

**Expected Questions:**
- "How do you decide which ML problems to work on?"
- "Describe a time you identified a product opportunity others missed."
- "How do you measure the business impact of ML models?"
- "Tell me about a time you simplified a complex ML solution."

**How to Answer Well:**
- Connect ML work to business outcomes
- Show prioritization skills
- Demonstrate user-centric thinking
- Balance technical sophistication with practical impact

### Customer Focus

**Expected Questions:**
- "How do you approach understanding customer needs for ML?"
- "Describe a time you helped a customer solve a difficult ML problem."
- "How do you handle customer expectations about ML?"
- "What's your approach to customer-facing ML documentation?"

**How to Answer Well:**
- Show genuine interest in customer outcomes
- Demonstrate ability to scope ML problems
- Reference specific customer interactions
- Balance honesty (manage expectations) with ambition

---

## Sample Questions & Answers

### Technical: MLflow

**Q:** "How does MLflow Tracking handle concurrent experiments and what happens if the tracking server goes down?"

**A:** "MLflow Tracking has a few key design decisions for reliability:

**Concurrent experiments:**
- MLflow uses SQL database transactions for metadata updates
- Each run gets a unique run_id (UUID)
- Metric logging is append-only with timestamps
- Concurrent writes to different runs don't conflict
- Parameter logging to the same run is idempotent (last write wins)

**Reliability:**
- If the tracking server fails, the experiment data may be lost for that window
- Best practice: use a resilient backend (RDS, Aurora, Cloud SQL with multi-AZ)
- Clients have retry logic for failed tracking API calls
- Consider local file tracking as fallback for critical experiments
- Artifact store (S3/ADLS) is separate from backend store and has its own reliability

**Design recommendation:**
- Use a managed database with backups
- Implement client-side logging as backup
- Consider MLflow with high-availability configuration for production"

### Technical: ML System Design

**Q:** "Design a real-time model serving platform for 1000+ models."

**A:** "Key components:

1. **Model Registry:** Central metadata store with versioning, stage transitions
2. **Model Cache:** Pre-load frequently used models; LRU eviction
3. **Serving Infrastructure:**
   - Kubernetes cluster with GPU nodes
   - Model-specific containers or shared containers
   - Autoscaling based on request volume per model
4. **Request Routing:**
   - API gateway routes by model ID: `/predict/{model_id}`
   - Load balancer distributes across replicas
5. **Feature Serving:**
   - Low-latency feature store (Redis/Memorystore)
   - Feature lookup by entity key
6. **Production Considerations:**
   - Canary deployments for model updates
   - Shadow traffic for validation
   - Circuit breakers for failing models
   - Request logging to Delta Lake for monitoring
   - Drift detection on prediction distributions"

### Behavioral: Technical Decision

**Q:** "Tell me about a difficult technical decision you made in an ML project."

**How to structure answer (STAR):**
- **Situation:** Building a real-time fraud detection system
- **Task:** Choose between batch inference latency (2 min) vs real-time (50ms)
- **Action:** Evaluated trade-offs — cost, complexity, business impact. Chose hybrid approach: real-time for high-risk transactions, batch for lower priority
- **Result:** 99.9% of fraud caught in real-time, 40% cost savings vs full real-time
- **Learning:** Sometimes the right answer is a mix, not a binary choice

### Technical: Distributed Training

**Q:** "How would you train a large model on a Spark cluster with GPUs?"

**A:** "Several approaches:

1. **Spark + PyTorch with TorchDistributor:**
   - Each executor launches a PyTorch process
   - Spark handles data loading
   - PyTorch handles distributed training across GPUs within/ across nodes
   - MLflow tracks experiments

2. **HorovodRunner:**
   - Use Horovod for distributed deep learning
   - Integrates with Spark for data loading
   - Supports TensorFlow, PyTorch, Keras
   - Handles all-reduce across GPU workers

3. **Considerations:**
   - Data locality: minimize data movement
   - GPU memory: batch size, gradient accumulation
   - Communication: InfiniBand vs Ethernet bandwidth
   - Checkpointing: save to distributed storage

4. **Best practice:**
   - Use Delta for training data
   - Log all experiments with MLflow
   - Use cluster auto-scaling for cost efficiency"

---

## Resources & Further Reading

### Databricks Documentation
- MLflow Documentation: https://mlflow.org/docs
- Delta Lake Documentation: https://web.archive.org/web/20240811162307/https://delta.io/docs
- Databricks ML Guide: https://docs.databricks.com/machine-learning

### Key Papers
1. "Spark: Cluster Computing with Working Sets" (Zaharia et al., 2010)
2. "Resilient Distributed Datasets" (Zaharia et al., 2012)
3. "Delta Lake: High-Performance ACID Table Storage over Cloud Object Stores" (Armbrust et al., 2020)
4. "MLflow: Reducing the Barrier to Machine Learning at Scale" (Zaharia et al., 2018)

### Preparation Resources
- Apache Spark documentation and tutorials
- LeetCode (Medium — algorithm and data structure)
- PySpark coding practice
- MLflow tutorials and examples
- Databricks Academy (free courses)

### Key Technical Areas to Master
1. Spark internals (execution model, memory management, optimization)
2. MLflow components and usage
3. Delta Lake architecture and ML use cases
4. Feature engineering at scale
5. ML system design patterns
6. MLOps best practices

---

*Databricks interviews reward deep knowledge of data engineering and ML platform concepts, strong coding skills in PySpark, and the ability to design ML systems at scale. Show that you understand both the data infrastructure and the ML lifecycle. Good luck!*
