# Feature Store Flashcards

## Card 1
**Front**: What is a feature store?
**Back**: A centralized platform for managing, computing, and serving ML features for both training and inference.

## Card 2
**Front**: What is the difference between online and offline stores?
**Back**: Online store serves features with low latency for real-time inference. Offline store stores historical features for batch training.

## Card 3
**Front**: What is point-in-time correctness?
**Back**: A join strategy that ensures no future data is used when creating training datasets, preventing data leakage.

## Card 4
**Front**: What is training/serving skew?
**Back**: A mismatch between feature values computed during training vs. production serving, leading to model performance degradation.

## Card 5
**Front**: What is a feature registry?
**Back**: A catalog of all feature definitions, including metadata, lineage, ownership, and transformation logic.
