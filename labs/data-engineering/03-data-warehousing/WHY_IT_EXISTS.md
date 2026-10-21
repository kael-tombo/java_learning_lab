# Why Data Warehousing Exists

## The Problem
Transactional databases are optimized for writes, not analytical queries. Running complex aggregations on OLTP systems degrades performance for both operational and analytical users.

## Root Cause
- OLTP schemas are normalized for transaction efficiency
- Historical data is purged from operational systems
- Cross-system joins require data integration
- Query performance degrades with large historical datasets

## Solutions
`java
// Data warehouse enables complex analytics without impacting production
spark.sql("""
    SELECT 
        d.category,
        d.region,
        DATE_TRUNC('month', f.order_date) as month,
        SUM(f.revenue) as revenue,
        COUNT(DISTINCT f.customer_id) as customers
    FROM wh.fact_orders f
    JOIN wh.dim_product d ON f.product_id = d.id
    JOIN wh.dim_date dt ON f.date_id = dt.id
    GROUP BY d.category, d.region, DATE_TRUNC('month', f.order_date)
""").show();
`
"@

System.Collections.Hashtable["WHY_IT_MATTERS.md"] = @"
# Why Data Warehousing Matters

## Business Impact
- **Single Source of Truth**: Consistent data definitions across the organization
- **Query Performance**: Optimized for analytical queries, sub-second response
- **Historical Analysis**: Years of data available for trend analysis
- **Data Governance**: Centralized security, quality, and lineage

## Key Metrics
| Metric | Description |
|--------|-------------|
| Query Latency | Time to return analytical results |
| Data Freshness | How current is warehouse data |
| Concurrency | Number of simultaneous queries supported |
| Storage Efficiency | Compression ratios, partition pruning |

## Java Integration
`java
// Spring JDBC for warehouse queries
@Repository
public class WarehouseRepository {
    private final JdbcTemplate whJdbc;

    public List<SalesSummary> getMonthlySales(String year) {
        return whJdbc.query(
            "SELECT d.region, SUM(f.amount) as total " +
            "FROM fact_sales f " +
            "JOIN dim_store d ON f.store_id = d.id " +
            "WHERE f.year = ? " +
            "GROUP BY d.region",
            new Object[]{year},
            new BeanPropertyRowMapper<>(SalesSummary.class));
    }
}
`
"@

System.Collections.Hashtable["HISTORY.md"] = @"
# History of Data Warehousing

## Timeline
- **1960s**: Decision Support Systems (DSS) concept
- **1988**: "Data Warehouse" term coined by Bill Inmon
- **1996**: Kimball's "The Data Warehouse Toolkit" published
- **2000s**: Enterprise data warehouses (Teradata, Netezza, Greenplum)
- **2012**: Cloud data warehouses (Redshift, BigQuery, Snowflake)
- **2019**: Lakehouse paradigm (Databricks Delta Lake)

## Key Milestones
1. **1992**: Inmon defines data warehouse as "subject-oriented, integrated"
2. **1996**: Kimball introduces dimensional modeling
3. **2008**: MapReduce enables new approaches to warehousing
4. **2020**: Snowflake IPO validates cloud warehouse model
