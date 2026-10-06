# Exploratory Analysis - Quiz

## Question 1
What is the main goal of exploratory data analysis (EDA)?
A) Tune hyperparameters
B) Understand structure, anomalies, and hypotheses before modeling
C) Deploy the model
D) Clean the database

**Answer**: B

## Question 2
Why visualize distributions before modeling?
A) For aesthetics
B) To spot skew, multimodality, and outliers that dictate transforms and metric choice
C) To fill missing values
D) To train faster

**Answer**: B

## Question 3
What does a bimodal distribution suggest?
A) Two subpopulations or regimes mixed together
B) Good normalization
C) Normality
D) High correlation

**Answer**: A

## Question 4
Why check correlation heatmaps during EDA?
A) To pick features — but high correlation is not causation
B) To prove causation
C) To compute means
D) To plot time

**Answer**: A

## Question 5
What does a flat line in a scatter plot of feature vs target mean?
A) Strong predictive power
B) The feature carries no linear signal for the target
C) Leakage
D) Outlier

**Answer**: B

## Question 6
Why compute missingness by column and by row?
A) For SQL export
B) A few columns may be mostly missing (drop them) vs spread across rows (drop rows or impute)
C) It speeds up plotting
D) It is required

**Answer**: B

## Question 7
Why check for duplicate rows?
A) They inflate metrics and can cause leakage if duplicated into train/test splits
B) They break the index
C) They slow joins
D) They change dtypes

**Answer**: A

## Question 8
What does a sharp drop in a histogram's bin suggest?
A) Data corruption or a floor/ceiling effect worth investigating
B) Normality
C) Good variance
D) High correlation

**Answer**: A

## Question 9
Why look at target distribution before classification?
A) For aesthetics
B) Severe imbalance tells you to change the metric (not accuracy) and sampling strategy
C) It picks the algorithm
D) It fills NaNs

**Answer**: B

## Question 10
Why compute value counts on categoricals?
A) To find rare levels that will break encoders or create unstable features
B) To sort the frame
C) To find NaNs
D) To compute means

**Answer**: A

## Question 11
What does a time series gradually drifting upward indicate for modeling?
A) The target is stationary
B) Distribution shift — a random train/test split will overestimate performance
C) Data is clean
D) High variance

**Answer**: B

## Question 12
Why do pairwise scatter plots miss interactions?
A) They are slow
B) They show 2D slices only; a strong feature interaction (XOR-like) looks flat in each 2D slice
C) They need more memory
D) They ignore color

**Answer**: B

## Question 13
What is the danger of mining the test set during EDA?
A) Nothing
B) Decisions driven by test-set knowledge bias evaluation — treat it as held-out
C) It is slow
D) It breaks the seed

**Answer**: B

## Question 14
Why check feature vs target with a box plot grouped by a categorical?
A) To inspect whether category shifts the continuous target distribution — a signal feature
B) To normalize
C) To fill missing
D) To sort

**Answer**: A

## Question 15
Why record findings of EDA as hypotheses?
A) For the report only
B) It converts observation into testable modeling choices — investigated, not confirmed, until tested
C) It speeds EDA
D) It is required

**Answer**: B
