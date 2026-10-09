# 09 — AWS Security — Visual Guide

## System Overview

`
                    +-----------+
                    |   User    |
                    +-----+-----+
                          |
                    +-----v-----+
                    |   HTTP    |
                    +-----+-----+
                          |
            +-------------v-------------+
            |      Load Balancer        |
            +-------------+-------------+
                          |
            +-------------v-------------+
            |     Application Service   |
            +---+---------+----------+--+
                |         |          |
        +-------v-+  +---v----+  +--v-------+
        | Module A |  | Module B|  | Module C |
        +----+-----+  +---+----+  +-----+----+
             |            |             |
        +----v------------v-------------v----+
        |          Data Store               |
        +-----------------------------------+
`

## Component Diagram

`
+----------------------------+
| ServiceApplication         |
|  +----------------------+  |
|  | WebController        |  |
|  | (REST Endpoints)     |  |
|  +----------+-----------+  |
|             |              |
|  +----------v-----------+  |
|  | ServiceFacade        |  |
|  | (Orchestration)      |  |
|  +---+------+------+---+  |
|      |      |      |      |
|  +---v-+ +--v--+ +-v---+  |
|  |RepoA| |RepoB| |RepoC|  |
|  +---+-+ +--+--+ +-+---+  |
|      |      |      |      |
+------+------+------+------+
       |      |      |
   +---v------v------v---+
   |     Data Store      |
   +---------------------+
`

## Request Sequence

`
Client    Service    Database    External
  |          |           |           |
  |--HTTP---->           |           |
  |          |---SQL----->           |
  |          |<--Result----           |
  |          |---API------------------>
  |          |<--Response-------------
  |          |           |           |
  |<--JSON---            |           |
`

## Data Model

`
+------------------+       +------------------+
| ServiceConfig    |       | ServiceMetric    |
+------------------+       +------------------+
| endpoint: string |       | name: string     |
| timeout: int     |       | value: double    |
| retries: int     |       | timestamp: long  |
| region: string   |       | tags: map        |
+------------------+       +------------------+
`

## Deployment Topology

`
+-- Load Balancer (port 80/443) --+
|                                  |
+--------+------------------------+
         |
   +-----v------+      +-----v------+
   | App Node 1 |      | App Node 2 |
   | :8080      |      | :8080      |
   +-----+------+      +-----+------+
         |                    |
         +--------+-----------+
                  |
          +-------v--------+
          | Database (R/A) |
          +----------------+
`

