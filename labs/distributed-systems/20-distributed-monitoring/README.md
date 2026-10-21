# 20 - Distributed Monitoring

## Overview
Distributed monitoring provides observability at scale across distributed systems. This lab covers Prometheus federation, Thanos, Cortex, distributed tracing with OpenTelemetry, and metrics aggregation at scale.

## Prerequisites
- Java 21+
- Maven 3.8+
- Understanding of distributed systems and microservices
- Basic monitoring and observability concepts

## Topics Covered
- Prometheus architecture and metric model
- Prometheus federation and hierarchical monitoring
- Thanos for global query and long-term storage
- Cortex for multi-tenant metrics
- OpenTelemetry distributed tracing
- Metrics aggregation and downsampling
- Alerting at scale (Alertmanager)
- Service-level objectives (SLOs) and burn rates

## Package Structure
- com.distributed.monitoring — Core implementations
  - MetricRegistry.java — Custom metric registry
  - PrometheusClient.java — Prometheus HTTP API client
  - TracingSpan.java — Distributed tracing span
  - TracerProvider.java — OpenTelemetry integration
  - AlertEvaluator.java — Alert rule evaluation
  - AggregationPipeline.java — Metric aggregation
