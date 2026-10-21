# History: Spring Cloud

## Origins (2014-2015)
Spring Cloud emerged from Netflix's open-source contributions. Netflix had built a comprehensive microservices infrastructure internally, and in 2014 began releasing components like Eureka, Hystrix, and Ribbon to open source. Spring Cloud wrapped these Netflix components with Spring Boot auto-configuration, making them accessible to the broader Java community.

## The Netflix Stack Era (2015-2018)
Spring Cloud became the de facto standard for Java microservices. The Netflix OSS stack (Eureka, Hystrix, Ribbon, Zuul, Feign) was the go-to solution. Companies adopted it widely. Spring Cloud Edgware and Finchley releases stabilized the ecosystem.

## The Shift Away from Netflix (2018-2020)
Netflix announced maintenance mode for Hystrix and Ribbon in 2018. Spring Cloud began replacing Netflix components:
- Spring Cloud LoadBalancer replaced Ribbon
- Resilience4J replaced Hystrix
- Spring Cloud Gateway replaced Zuul
- Spring Cloud Circuit Breaker provided abstraction

## Cloud-Native Era (2020-2023)
Spring Cloud 2020.0 (Ilford) removed Netflix dependencies entirely. New patterns emerged:
- Kubernetes-native discovery (replacing Eureka)
- Spring Cloud Kubernetes
- Service mesh integration
- Spring Cloud Function for serverless

## Current State (2024+)
Spring Cloud 2023.0 focuses on:
- Virtual threads support
- Observability with Micrometer
- Spring Boot 3.x compatibility
- GraalVM native image support
- Simplified configuration with property-driven setup

## Key Milestones
| Year | Event |
|------|-------|
| 2014 | Netflix open-sources Eureka, Hystrix |
| 2015 | Spring Cloud 1.0 released |
| 2016 | Spring Cloud Brixton, Camden |
| 2017 | Spring Cloud Dalston, Edgware |
| 2018 | Hystrix enters maintenance mode |
| 2019 | Spring Cloud Hoxton, Resilience4J integration |
| 2020 | Spring Cloud 2020.0 (Ilford) without Netflix |
| 2021 | Spring Cloud 2021.0 (Jubilee) |
| 2022 | Spring Cloud 2022.0 (Kilburn) |
| 2023 | Spring Cloud 2023.0 with virtual threads |
