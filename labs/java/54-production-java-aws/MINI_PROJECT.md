# MINI_PROJECT — Catalog API on EKS

Deploy the lab-53 service to EKS (Graviton nodes, 3 AZ, private subnets):

1. CDK stack: VPC, EKS, ALB Controller, ECR, Aurora Serverless v2 (or
   provisioned Multi-AZ), ElastiCache, MSK *or* SQS/SNS, Secrets Manager.
2. IRSA roles, HPA (latency+CPU), PodDisruptionBudget (minAvailable 2),
   readiness-gated rolling deploy.
3. Flyway Job migration; load fixture; PITR restore drill with canary diff.
4. CloudWatch RED alarms + X-Ray sampling; load-test to HPA trigger;
   record scale-out time and p99 behavior.
5. Cost-tagged bill after 7 days + rollback drill (previous tag).

Deliverable: repo (CDK + manifests + runbooks) + one-page ops report.
