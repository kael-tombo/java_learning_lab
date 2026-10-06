# Data Wrangling - Quiz

## Question 1
You compute a mean after filling missing values with the median of the whole column. What is wrong?
A) Nothing; median imputation is always safe
B) The imputation was fit on data that will also be in the test set (leakage)
C) The median is slower to compute than the mean
D) Median imputation breaks the index alignment

**Answer**: B

## Question 2
Why impute using statistics from the training fold only?
A) Training statistics are more accurate
B) To prevent information from validation/test leaking into training features
C) It is required by scikit-learn
D) CV folds would otherwise have different sizes

**Answer**: B

## Question 3
A categorical column has 1,000 unique values, of which 900 appear once. Best handling?
A) One-hot encode everything
B) Rare-level grouping / target-aware encoding with care
C) Drop the column always
D) Use it raw as a string

**Answer**: B

## Question 4
`df.dropna()` throws away 30% of rows. Main risk?
A) The remaining rows may have systematically different (often non-missing) outcomes
B) DataFrame becomes slower
C) The index is lost
D) Column types change to float

**Answer**: A — missingness itself can be informative (MNAR).

## Question 5
Why does `merge` producing more rows than either left or right input usually indicate a bug?
A) It is always a left join
B) A many-to-many join on a key that should be unique duplicates rows
C) It means NaNs were introduced
D) The index is now a MultiIndex

**Answer**: B

## Question 6
Why track dtypes after loading CSV?
A) To speed up plotting
B) Mixed-type or all-string columns (e.g. IDs stored as strings, comma-separated numbers) silently corrupt later math
C) It is needed for `groupby`
D) It improves the SQL export

**Answer**: B

## Question 7
What is a leaky feature in a wrangle step?
A) A feature that uses only past information
B) A feature whose value at prediction time would require knowing the label or the future
C) A feature with too many NaNs
D) A feature with high cardinality

**Answer**: B

## Question 8
Best practice for outliers when rows are genuine errors (sensor glitches)?
A) Clip silently and keep
B) Investigate, then drop or cap with a logged rule; never silently
C) Set to median
D) Remove the column

**Answer**: B

## Question 9
Why is `fillna(method="ffill")` dangerous on time series with large gaps?
A) It is slower
B) It propagates stale values across long gaps as if they were current
C) It requires a DatetimeIndex
D) It changes the dtype

**Answer**: B

## Question 10
What does `pd.factorize` differ from `get_dummies` in a production pipeline?
A) Nothing
B) Encoded ids are integer codes and don't carry a feature name — new levels at inference map to -1 or must be handled
C) It is slower than one-hot
D) It works only on strings

**Answer**: B

## Question 11
When you reshape with `pivot` and produce NaNs, what happened?
A) A bug in the pivot
B) Some row/column combinations have no observation — masking as implicit rows
C) The columns became datetime
D) The index was not unique

**Answer**: B

## Question 12
Why keep a raw, immutable copy of the input before wrangling?
A) For caching
B) To enable auditability and rerunning the pipeline after fixes
C) To speed up `groupby`
D) It is needed by pandas

**Answer**: B

## Question 13
A `groupby(...).transform("sum")` yields a column aligned to the original rows. What is its main use?
A) Create group-level totals as a new per-row feature
B) Reduce memory
C) Replace NaNs
D) Sort the frame

**Answer**: A

## Question 14
You standardize with the whole dataset's mean/std. What leaks?
A) Nothing
B) Test-set distribution into training feature scaling
C) Feature names
D) Row order

**Answer**: B

## Question 15
Why is row order preserved/duplicated by many `merge_asof`/`join` operations relevant?
A) It isn't
B) Shuffling without a seed breaks reproducibility and any time-based validation
C) It changes column widths
D) It affects SQL dialect

**Answer**: B
