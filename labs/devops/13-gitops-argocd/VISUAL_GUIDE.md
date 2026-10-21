# Visual Guide to ArgoCD

## Architecture Diagram
```
                     Git Repository (Source of Truth)
                              |
                              v
                    +------------------+
                    |  ArgoCD          |
                    |  +------------+  |
                    |  | API Server |  |
                    |  +-----+------+  |
                    |        |         |
                    |  +-----v------+  |
                    |  |  Repo      |  |
                    |  |  Server    |  |
                    |  +-----+------+  |
                    |        |         |
                    |  +-----v------+  |
                    |  | Controller |  |
                    |  +-----+------+  |
                    +------------------+
                              |
                    +---------+---------+
                    |         |         |
                    v         v         v
               +--------+ +--------+ +--------+
               |Cluster1| |Cluster2| |Cluster3|
               +--------+ +--------+ +--------+
```

## Application Lifecycle
```
Created -> Syncing -> Synced -> OutOfSync -> Syncing -> Synced
                          |                    ^
                          v                    |
                       Degraded              Healthy
                          |                    ^
                          v                    |
                       Deleted                 |
                          |                    |
                          +--------------------+
```

## Sync Strategy Visualization
```
Manual Sync:  Git Change -> Wait -> Manual Trigger -> Sync -> Health Check
Auto Sync:    Git Change -> Webhook -> Auto Sync -> Health Check -> Self Heal
Self Heal:    Drift Detected -> Auto Correct -> Reconcile
```
