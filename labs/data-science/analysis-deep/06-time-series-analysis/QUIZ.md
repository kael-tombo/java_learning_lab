# Time Series Analysis - Quiz

## Question 1
Why must train/test splits respect time order in time series?
A) For aesthetics
B) Random splits leak future information into training — validation estimates are optimistic
C) It is faster
D) It changes dtypes

**Answer**: B

## Question 2
What makes a series stationary?
A) Constant mean, variance, and autocorrelation over time — required by many classical models
B) Constant slope
C) No trend
D) No seasonality

**Answer**: A

## Question 3
First differencing removes what?
A) Seasonality
B) Trend — but may over-difference and add noise
C) Outliers
D) Noise

**Answer**: B

## Question 4
Why use rolling-window features (lag values)?
A) For aesthetics
B) Past values of the series are the strongest predictors of future values
C) To remove seasonality
D) To fill missing

**Answer**: B

## Question 5
What does seasonality differ from trend?
A) Trend repeats every period; seasonality is the long-term drift
B) Seasonality repeats at fixed periods; trend is the long-term drift
C) They are the same
D) Seasonality is noise

**Answer**: B

## Question 6
Why check autocorrelation (ACF) before modeling?
A) For aesthetics
B) It tells you which lags carry signal — features or AR-order selection
C) To fill missing
D) To plot

**Answer**: B

## Question 7
Why use an expanding window for validation instead of a fixed split?
A) It is slower
B) Each fold trains on all history available at that time — realistic for retraining on a growing dataset
C) It leaks
D) It changes dtypes

**Answer**: B

## Question 8
What is a lag feature's leakage risk?
A) It is slower
B) If the lag window reaches into the future relative to the target timestamp — off-by-one leakage
C) It is signed
D) It changes dtype

**Answer**: B

## Question 9
Why log-transform a strongly seasonal, exponentially growing series?
A) It makes seasonality additive and variance more stable
B) It speeds up
C) It removes outliers
D) It changes categories

**Answer**: A

## Question 10
What does a holdout period of one full season give you?
A) A metric that misses seasonal behavior
B) A realistic read on whether the model captures the seasonal pattern, not a lucky slice
C) Less data
D) Faster training

**Answer**: B

## Question 11
Why is random CV invalid for time series?
A) It is slower
B) Folds mix past/future → the model "sees the future" → overly optimistic estimates
C) It leaks the seed
D) It changes types

**Answer**: B

## Question 12
What does differencing with period p (seasonal differencing) do?
A) Removes linear trend
B) Removes seasonal autocorrelation by subtracting the value from the same period last cycle
C) Adds noise
D) Imputes

**Answer**: B

## Question 13
Why is walk-forward evaluation a better estimate for production?
A) It is faster
B) It mirrors retraining: train on history up to T, evaluate just after T, advance, repeat
C) It uses more data
D) It removes leakage

**Answer**: B

## Question 14
What is a common failure of ARIMA on series with structural breaks?
A) It fits too fast
B) It assumes stable dynamics; a regime change from a new campaign or outage makes parameters invalid
C) It leaks
D) It is signed

**Answer**: B

## Question 15
Why include calendar features (day of week, holiday)?
A) For aesthetics
B) Periodic human behavior (weekends, holidays) that AR-style lags capture only indirectly
C) To remove trend
D) To impute

**Answer**: B
