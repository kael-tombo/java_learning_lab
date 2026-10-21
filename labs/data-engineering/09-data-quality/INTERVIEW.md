# Data Quality Interview Questions

## Beginner
**Q**: Why is data quality important?
**A**: Bad data leads to bad decisions. It costs companies millions, wastes engineering time, and erodes trust in data-driven systems.

## Intermediate
**Q**: How would you implement data quality checks in a Spark pipeline?
**A**: Use Deequ library for automated checks, implement custom validation rules, check at each medallion layer (bronze/silver/gold), and alert on threshold violations.

## Advanced
**Q**: Design a data quality monitoring system for 1000+ tables.
**A**: Use a rule engine with declarative YAML configurations, automated profiling, anomaly detection on metrics trends, tiered alerting (Slack/PagerDuty), and a central quality dashboard.
