# History: Cassandra NoSQL

## Evolution

### Pre-2000: The Age of Monoliths
**1970s-1980s:** Relational databases dominate. IBM's System R (1974) and Oracle (1979) run on mainframes. All data lives on a single machine.

**1990s:** Client-server architecture. Databases move to dedicated servers but remain single-instance. Vertical scaling: buy a bigger server.

### 2000-2005: The Web Scale Problem
**2000:** Google indexes 1 billion pages. Single-node search is impossible.

**2001:** Google develops GFS and Bigtable. Internal distributed data at massive scale.

**2003:** Flickr manually shards MySQL. A turning point—mainstream company using distribution in production.

**2004:** Friendster fails to scale due to database limitations.

### 2006-2010: Birth of Distributed Databases
**2006:** Amazon publishes Dynamo paper. Describes consistent hashing for production use.

**2007:** Google publishes Bigtable paper. Range-based partitioning at global scale.

**2008:** Facebook releases Cassandra. Combines Dynamo's hashing with Bigtable's data model.

**2009:** MongoDB introduces auto-sharding. Makes distributed databases accessible.

**2010:** Redis Cluster design published. Introduces hash slots (16384 slots).

### 2011-2015: Maturation
**2012:** Google publishes Spanner paper. Global-scale distribution with external consistency.

**2013:** Vitess open-sourced by YouTube. MySQL-compatible sharding proxy.

**2015:** CockroachDB announced. Built as distributed SQL with automatic rebalancing.

### 2016-2020: Cloud-Native
**2016:** Citus (PostgreSQL sharding) open-sourced.

**2017:** Google Cloud Spanner publicly available.

**2018:** YugabyteDB emerges as cloud-native distributed SQL.

**2020:** PlanetScale launches serverless sharded MySQL.

### 2021-Present: Serverless Era
**2021:** Neon introduces compute-storage separation for PostgreSQL.

**2022:** CockroachDB Serverless with automatic, transparent distribution.

**2023:** AI-assisted routing key recommendations emerge.

**2024:** Edge databases bring distributed data to the network edge.

**2025-2026:** Serverless databases with auto-scaling become mainstream.

## Key Lessons from History
1. Necessity drives innovation: Distributed data emerged from real scalability problems
2. Consistent hashing won: It's now the standard approach
3. SQL can be distributed: Early belief that NoSQL was required proved wrong
4. Cloud reduces complexity: Managed services handle operational aspects
5. Automation is the trend: Manual management is becoming obsolete
6. Trade-offs remain: Consistency vs. availability vs. latency hasn't changed
