# Lab 22: GraphQL with Netflix DGS

## Overview
Netflix DGS (Domain Graph Service) framework simplifies building GraphQL services. Learn schema-first development, data loaders, federated GraphQL, and subscriptions.

## Topics Covered
- GraphQL fundamentals (queries, mutations, subscriptions)
- Schema-first design with SDL
- Netflix DGS framework
- Data loaders for N+1 problem
- DGS entities and federation
- Subscriptions with WebSocket
- Exception handling and error types
- Testing with DGS

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- GraphQL basics

## Key Dependencies
`xml
<dependency>
    <groupId>com.netflix.graphql.dgs</groupId>
    <artifactId>graphql-dgs-spring-boot-starter</artifactId>
    <version>8.4.1</version>
</dependency>
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\22-graphql-dgs "THEORY.md") @"
# Theory: GraphQL DGS

## 1. GraphQL Fundamentals

- **Query**: Read data (GET equivalent)
- **Mutation**: Write data (POST/PUT/DELETE equivalent)
- **Subscription**: Real-time events
- **Schema**: Type system defining available data
- **Resolver**: Function that returns data for a field

## 2. Schema-First Design

Define the API contract in SDL (Schema Definition Language) first:
`graphql
type Query {
    shows: [Show]
    show(id: ID!): Show
}

type Show {
    id: ID!
    title: String!
    releaseYear: Int!
    reviews: [Review]
}
`

## 3. Data Loaders

Solve N+1 problem by batching and caching database queries:
- Batch per request
- Cache within same request
- Automatically deduplicate
- Configurable batch size

## 4. DGS Annotations

- @DgsComponent: Mark resolver component
- @DgsQuery: Query resolver
- @DgsMutation: Mutation resolver
- @DgsSubscription: Subscription resolver
- @InputArgument: Input argument binding
- @DgsData: Custom field resolver
- @DgsEntityLoader: Entity loader for federation

## 5. Federation

Divide GraphQL schema across services:
- Type extension: Add fields to types defined elsewhere
- Entity resolution: Fetch entities from other services
- Schema stitching: Combine schemas at gateway
