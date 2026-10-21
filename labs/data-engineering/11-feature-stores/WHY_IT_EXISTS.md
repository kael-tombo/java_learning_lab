# Why Feature Stores Exist

## The Problem
ML teams traditionally built features in silos - each team and model had its own feature engineering code. This led to duplicated work, inconsistent features between training and serving, and no feature sharing.

## Root Cause
- Features built in Jupyter notebooks (not productionized)
- Training/serving skew from inconsistent feature computation
- No central catalog to discover existing features
- Point-in-time join complexity for time-series features

## Feature Store Solution
- **Centralized** feature computation and storage
- **Consistent** computation between training and serving
- **Discoverable** via feature registry
- **Reusable** across teams and models
- **Auditable** with full lineage
