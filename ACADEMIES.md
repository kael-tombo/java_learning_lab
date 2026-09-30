# 🎓 Engineering Academies - Complete Guide

Comprehensive deep-dive academies for specialized engineering disciplines. Each academy contains atomic micro-labs with standardized structure:

- **THEORY.md** - Complete theoretical foundation
- **CODE_DEEP_DIVE.md** - Java implementations with explanations
- **MATH_FOUNDATION.md** - Mathematical proofs and derivations (AI/Math academies)
- **EXERCISES.md** - 20+ practice problems with solutions
- **QUIZ.md** - 30 assessment questions with answers
- **FLASHCARDS.md** - Quick review cards for spaced learning
- **MINI_PROJECT.md** - Hands-on mini project
- **REAL_WORLD_PROJECT.md** - Production-ready project

---

## 🚀 AI Academy (`labs/ai/`)

Complete 20-lab curriculum for mastering Machine Learning, Deep Learning, and Generative AI with Java implementations.

### Learning Path

```
Linear Algebra → Probability → Calculus → Optimization
                ↓
            Statistics
                ↓
        ML Fundamentals → Regression → Classification
                ↓                    ↓
            Clustering → Dimensionality Reduction
                ↓
        Neural Networks → CNN → RNN → Transformers
                ↓                    ↓
            LLM Agents ← Fine-tuning ← RAG Systems
```

### Lab Index

| Lab | Topic | Hours | Difficulty |
|-----|-------|-------|------------|
| 01 | [Linear Algebra for ML](./ai/01-linear-algebra-for-ml/) | 10 | ⭐⭐ |
| 02 | [Probability for ML](./ai/02-probability-for-ml/) | 8 | ⭐⭐ |
| 03 | [Calculus for ML](./ai/03-calculus-for-ml/) | 8 | ⭐⭐⭐ |
| 04 | [Optimization](./ai/04-optimization/) | 8 | ⭐⭐⭐ |
| 05 | [Regression](./ai/05-regression/) | 10 | ⭐⭐⭐ |
| 06 | [Classification](./ai/06-classification/) | 10 | ⭐⭐⭐ |
| 07 | [Clustering](./ai/07-clustering/) | 8 | ⭐⭐ |
| 08 | [Dimensionality Reduction](./ai/08-dimensionality-reduction/) | 8 | ⭐⭐⭐ |
| 09 | [Anomaly Detection](./ai/09-anomaly-detection/) | 8 | ⭐⭐⭐ |
| 10 | [Recommendation Systems](./ai/10-recommendation-systems/) | 10 | ⭐⭐⭐ |
| 11 | [Neural Networks Basics](./ai/11-neural-networks-basics/) | 12 | ⭐⭐⭐⭐ |
| 12 | [Backpropagation](./ai/12-backpropagation/) | 12 | ⭐⭐⭐⭐ |
| 13 | [CNN](./ai/13-cnn/) | 12 | ⭐⭐⭐⭐ |
| 14 | [RNN/LSTM](./ai/14-rnn-lstm/) | 12 | ⭐⭐⭐⭐ |
| 15 | [Transformers](./ai/15-transformers/) | 15 | ⭐⭐⭐⭐ |
| 16 | [Embeddings](./ai/16-embeddings/) | 10 | ⭐⭐⭐ |
| 17 | [RAG Systems](./ai/17-rag/) | 10 | ⭐⭐⭐ |
| 18 | [Prompt Engineering](./ai/18-prompt-engineering/) | 6 | ⭐⭐ |
| 19 | [LLM Agents](./ai/19-llm-agents/) | 12 | ⭐⭐⭐⭐ |
| 20 | [Fine-tuning](./ai/20-fine-tuning/) | 15 | ⭐⭐⭐⭐ |

**Total: 200+ hours of hands-on learning**

### Key Concepts by Lab

#### Mathematical Foundations
- **Lab 01**: Vectors, matrices, operations, eigenvalues, SVD, PCA
- **Lab 02**: Bayes theorem, distributions (Normal, Bernoulli, Poisson), entropy
- **Lab 03**: Derivatives, partial derivatives, chain rule, gradients
- **Lab 04**: Gradient descent, Adam, RMSProp, loss landscapes

#### Machine Learning
- **Lab 06**: Supervised vs unsupervised, overfitting, cross-validation
- **Lab 07**: Linear regression, Ridge, Lasso, polynomial regression
- **Lab 08**: Logistic regression, SVM, decision trees, random forests
- **Lab 09**: K-means, DBSCAN, hierarchical clustering, silhouette score

#### Deep Learning
- **Lab 11**: Perceptron, activation functions, backpropagation, optimizers
- **Lab 12**: Convolutions, pooling, ResNet, transfer learning
- **Lab 13**: LSTM, GRU, seq2seq, attention mechanism

#### Generative AI
- **Lab 14**: Attention, multi-head attention, BERT, GPT, transformer architecture
- **Lab 15**: Retrieval systems, chunking, hybrid search, reranking
- **Lab 16**: Tool use, chain-of-thought, ReAct, planning agents
- **Lab 17**: LoRA, QLoRA, PEFT, domain adaptation

---

## ☁️ Cloud Engineering Academy (`labs/cloud/`)

Master cloud infrastructure, containers, and Kubernetes with hands-on labs.

### Learning Path

```
AWS Fundamentals → AWS Compute → AWS Storage → AWS Database
        ↓               ↓            ↓           ↓
    Networking     Docker      Kubernetes   Terraform
        ↓
    Service Mesh (Istio)
```

### Lab Index

| Lab | Topic | Hours | Focus Area |
|-----|-------|-------|------------|
| 01 | [AWS Fundamentals](./cloud/01-aws-fundamentals/) | 6 | EC2, S3, IAM, VPC |
| 02 | [AWS Compute](./cloud/02-aws-compute/) | 6 | Lambda, ECS, Fargate |
| 03 | [AWS Storage](./cloud/03-aws-storage/) | 5 | EFS, EBS, Glacier |
| 04 | [AWS Database](./cloud/04-aws-database/) | 6 | RDS, DynamoDB, ElastiCache |
| 05 | [AWS Networking](./cloud/05-aws-networking/) | 5 | Route 53, CloudFront |
| 06 | [Docker & Containers](./cloud/06-docker-containers/) | 8 | Images, compose, networking |
| 07 | [Kubernetes](./cloud/07-kubernetes/) | 10 | Pods, services, Helm |
| 08 | [Terraform IaC](./cloud/08-terraform/) | 8 | Modules, state, providers |

### Key Concepts by Lab

#### AWS Core Services
- **Lab 01**: IAM policies, VPC subnets, security groups, availability zones
- **Lab 02**: Serverless functions, container orchestration, auto-scaling
- **Lab 03**: Object storage lifecycle, block storage, archive tiers
- **Lab 04**: Relational vs NoSQL, caching strategies, replication

#### Container Technologies
- **Lab 06**: Multi-stage builds, Docker Compose, overlay networks, volumes
- **Lab 07**: Deployments, services, ingress, ConfigMaps, secrets, Helm charts
- **Lab 08**: Infrastructure as code, modules, state management, workspaces

---

## 🧮 Math Academy (`labs/math/`)

Mathematical foundations for ML and data science with Java implementations.

### Lab Index

| Lab | Topic | Applications |
|-----|-------|-------------|
| 01 | [Linear Algebra](./math/01-linear-algebra/) | ML transformations, PCA |
| 02 | [Calculus](./math/02-calculus/) | Gradient descent, backprop |
| 03 | [Probability](./math/03-probability/) | Bayesian inference |
| 04 | [Statistics](./math/04-statistics/) | Hypothesis testing |
| 05 | [Optimization](./math/05-optimization/) | Training algorithms |
| 06 | [Information Theory](./math/06-information-theory/) | Entropy, cross-entropy |
| 07 | [Graph Theory](./math/07-graph-theory/) | Networks, recommendations |
| 08 | [Number Theory](./math/08-number-theory/) | Cryptography, hashing |
| 09 | [Combinatorics](./math/09-combinatorics/) | Counting, algorithms |
| 10 | [Signal Processing](./math/10-signal-processing/) | FFT, filters |

---

## 🏗️ System Design Academy (`labs/system-design/`)

Master distributed systems architecture and design patterns.

### Lab Index

| Lab | Topic | Key Concepts |
|-----|-------|-------------|
| 01 | [Architecture Patterns](./system-design/01-architecture-patterns/) | Layered, microservices, CQRS |
| 02 | [Scalability](./system-design/02-scalability/) | Sharding, partitioning |
| 03 | [Availability](./system-design/03-availability/) | Failover, redundancy |

### Design Principles

1. **Scalability**: Horizontal scaling, caching, async processing
2. **Availability**: Redundancy, failover, circuit breakers
3. **Consistency**: CAP theorem, eventual consistency, consensus
4. **Maintainability**: Modularity, observability, automation

---

## 📊 Data Science Academy (`labs/data-science/`)

End-to-end data science with Java-based implementations.

### Lab Index

| Lab | Topic | Focus |
|-----|-------|-------|
| 01 | Data Wrangling | Cleaning, transformation |
| 02 | EDA | Visualization, patterns |
| 03 | Feature Engineering | Scaling, encoding |
| 04 | Model Training | Cross-validation |
| 05 | Model Evaluation | Metrics, benchmarking |
| 06 | Pipelines | Orchestration |
| 07 | Production ML | Serving, monitoring |

---

## 🏆 Portfolio Capstone Projects (`capstones/`)

Real-world projects demonstrating production-ready skills.

| # | Project | Domain | Complexity |
|---|---------|--------|------------|
| 01 | Banking Platform | Financial services | ⭐⭐⭐⭐ |
| 02 | Fraud Detection | Security/ML | ⭐⭐⭐⭐ |
| 03 | Recommendation Engine | ML | ⭐⭐⭐ |
| 04 | Vector Database | Search | ⭐⭐⭐⭐ |
| 05 | RAG Platform | GenAI | ⭐⭐⭐⭐ |
| 06 | Distributed Cache | Infrastructure | ⭐⭐⭐ |
| 07 | Event Streaming | Messaging | ⭐⭐⭐ |
| 08 | Search Engine | Search | ⭐⭐⭐⭐ |
| 09 | ML Platform | MLOps | ⭐⭐⭐⭐⭐ |
| 10 | AI Assistant | GenAI | ⭐⭐⭐⭐⭐ |

---

## 📚 Learning Resources

### Prerequisites
- **Java**: 21+ proficiency
- **Mathematics**: High school level for math academy
- **Data Structures**: Arrays, lists, maps, trees

### Recommended Order
1. Start with **AI Academy Lab 01-05** (math foundations)
2. Continue with **AI Academy Lab 06-10** (ML basics)
3. Progress to **AI Academy Lab 11-14** (deep learning)
4. Explore **GenAI topics** (Labs 15-20)
5. Parallel: Cloud Academy for deployment skills

### Assessment
- Each lab includes 30-question quiz
- Flashcards for spaced repetition
- Mini-projects for hands-on practice
- Real-world projects for portfolio building

---

## 🏭 Production Engineering Academy (`labs/production-engineering/`)

Senior Java Architect track — everything that matters in real production systems.

> **Target Audience**: Senior Java engineers, Staff engineers, Principal architects  
> **Level**: Advanced to Expert | **Total**: 200+ hours

### Lab Index

| Lab | Title | Domain | Hours | Level |
|-----|-------|---------|-------|-------|
| 01 | [JVM Memory Architecture & GC Mastery](./production-engineering/01-jvm-memory-gc/) | JVM Internals | 12h | ⭐⭐⭐⭐⭐ |
| 02 | [Thread Concurrency & Virtual Threads in Prod](./production-engineering/02-concurrency-production/) | Concurrency | 10h | ⭐⭐⭐⭐⭐ |
| 03 | [Production Debugging & Profiling](./production-engineering/03-production-debugging/) | Observability | 12h | ⭐⭐⭐⭐⭐ |
| 04 | [Distributed Systems Failures & Resilience](./production-engineering/04-distributed-resilience/) | Architecture | 10h | ⭐⭐⭐⭐⭐ |
| 05 | [Database Performance & Connection Pools](./production-engineering/05-database-production/) | Data Layer | 10h | ⭐⭐⭐⭐⭐ |
| 06 | [Microservices Architecture at Scale](./production-engineering/06-microservices-scale/) | Architecture | 12h | ⭐⭐⭐⭐⭐ |
| 07 | [Kubernetes for Java Architects](./production-engineering/07-kubernetes-java/) | Infrastructure | 10h | ⭐⭐⭐⭐⭐ |
| 08 | [Observability — Logs, Metrics, Traces](./production-engineering/08-observability-sre/) | SRE | 10h | ⭐⭐⭐⭐⭐ |
| 09 | [Security Engineering in Production](./production-engineering/09-security-production/) | Security | 10h | ⭐⭐⭐⭐⭐ |
| 10 | [API Design & Evolution at Scale](./production-engineering/10-api-design-scale/) | Architecture | 8h | ⭐⭐⭐⭐ |
| 11 | [Event-Driven Architecture & Kafka in Prod](./production-engineering/11-event-driven-production/) | Messaging | 10h | ⭐⭐⭐⭐⭐ |
| 12 | [Caching Strategies & Cache Invalidation](./production-engineering/12-caching-production/) | Performance | 8h | ⭐⭐⭐⭐ |
| 13 | [CI/CD Pipelines & Release Engineering](./production-engineering/13-cicd-release-engineering/) | DevOps | 8h | ⭐⭐⭐⭐ |
| 14 | [Production Incident Response & RCA](./production-engineering/14-incident-response/) | SRE | 10h | ⭐⭐⭐⭐⭐ |
| 15 | [Performance Engineering & Load Testing](./production-engineering/15-performance-engineering/) | Performance | 10h | ⭐⭐⭐⭐⭐ |
| 16 | [Cost Engineering & Cloud Optimization](./production-engineering/16-cost-engineering/) | Infrastructure | 8h | ⭐⭐⭐⭐ |
| 17 | [Data Architecture & Migration Patterns](./production-engineering/17-data-architecture/) | Data | 10h | ⭐⭐⭐⭐⭐ |
| 18 | [Chaos Engineering & Fault Injection](./production-engineering/18-chaos-engineering/) | SRE | 8h | ⭐⭐⭐⭐ |
| 19 | [Java Architect Decision Framework](./production-engineering/19-architect-decisions/) | Architecture | 10h | ⭐⭐⭐⭐⭐ |
| 20 | [Production Readiness & SLO Engineering](./production-engineering/20-production-readiness/) | SRE | 10h | ⭐⭐⭐⭐⭐ |

### Per-Lab Structure

Each lab contains 9 files:
`README.md` · `THEORY.md` · `PRODUCTION_SCENARIOS.md` · `CODE_DEEP_DIVE.md` · `ARCHITECTURE_DECISIONS.md` · `RUNBOOKS.md` · `INTERVIEW_QUESTIONS.md` · `EXERCISES.md` · `ANTI_PATTERNS.md` · `CHECKLIST.md`

---

## 🎯 Quick Navigation

| Academy | Labs | Hours |
|---------|------|-------|
| AI Academy | 20 | 200+ |
| Cloud Academy | 8 | 54 |
| Math Academy | 10 | 80 |
| System Design | 8 | 64 |
| Data Science | 7 | 56 |
| **Production Engineering** | **20** | **200+** |

**Total: 73 labs, 650+ hours of content**