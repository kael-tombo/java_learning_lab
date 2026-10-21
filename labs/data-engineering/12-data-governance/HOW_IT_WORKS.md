# How Data Governance Works

## Data Catalog Implementation
`java
@Component
public class DataCatalogService {

    private final CatalogRepository repository;
    private final MetadataExtractor extractor;

    @EventListener
    public void onTableCreated(TableCreatedEvent event) {
        // Automatically register new tables in catalog
        DataAsset asset = DataAsset.builder()
            .name(event.getTableName())
            .type(AssetType.TABLE)
            .schema(extractor.extractSchema(event))
            .owner(event.getOwner())
            .createdAt(Instant.now())
            .tags(extractTags(event))
            .build();

        repository.save(asset);
        log.info("Registered new asset: {}", asset.getName());
    }

    public List<DataAsset> search(String query, String domain, String owner) {
        Specification<DataAsset> spec = Specification.where(null);

        if (query != null) {
            spec = spec.and((root, q, cb) ->
                cb.like(cb.lower(root.get("name")), "%" + query.toLowerCase() + "%"));
        }
        if (domain != null) {
            spec = spec.and((root, q, cb) ->
                cb.equal(root.get("domain"), domain));
        }
        if (owner != null) {
            spec = spec.and((root, q, cb) ->
                cb.equal(root.get("owner"), owner));
        }
        return repository.findAll(spec);
    }
}
`

## Data Lineage Tracking
`java
@Component
public class LineageTracker {

    private final LineageRepository lineageRepo;

    @EventListener
    public void onPipelineExecution(PipelineExecutionEvent event) {
        // Record lineage edges
        for (InputSource input : event.getInputs()) {
            for (OutputTarget output : event.getOutputs()) {
                LineageEdge edge = LineageEdge.builder()
                    .sourceDataset(input.getDataset())
                    .sourceColumns(input.getColumns())
                    .targetDataset(output.getDataset())
                    .targetColumns(output.getColumns())
                    .transformation(event.getTransformation())
                    .executionId(event.getExecutionId())
                    .timestamp(event.getTimestamp())
                    .build();
                lineageRepo.save(edge);
            }
        }
    }

    public LineageGraph getLineage(String dataset, LineageDirection direction) {
        Set<LineageNode> nodes = new HashSet<>();
        Set<LineageEdge> edges = new HashSet<>();

        Queue<String> queue = new LinkedList<>();
        queue.add(dataset);

        while (!queue.isEmpty()) {
            String current = queue.poll();
            List<LineageEdge> connected = (direction == LineageDirection.UPSTREAM)
                ? lineageRepo.findByTargetDataset(current)
                : lineageRepo.findBySourceDataset(current);

            for (LineageEdge edge : connected) {
                nodes.add(new LineageNode(
                    direction == LineageDirection.UPSTREAM
                        ? edge.getSourceDataset() : edge.getTargetDataset()));
                edges.add(edge);

                queue.add(direction == LineageDirection.UPSTREAM
                    ? edge.getSourceDataset() : edge.getTargetDataset());
            }
        }
        return new LineageGraph(nodes, edges);
    }
}
`

## Policy Enforcement
`java
@Component
public class PolicyEngine {

    private final PolicyRepository policyRepo;
    private final UserContext userContext;

    public AccessDecision evaluate(AccessRequest request) {
        // 1. Get applicable policies
        List<Policy> policies = policyRepo.findByResourceAndActive(
            request.getResource(), true);

        // 2. Evaluate each policy
        for (Policy policy : policies) {
            if (!matchesCondition(policy, request)) continue;

            if (!policy.isAllow()) {
                return AccessDecision.deny(
                    "Denied by policy: " + policy.getName());
            }
        }

        // 3. Check data classification
        DataAsset asset = catalogService.getAsset(request.getResource());
        if (asset.getClassification() == Classification.PII &&
            !userContext.hasRole("PII_ACCESS")) {
            return AccessDecision.deny("PII access requires special role");
        }

        return AccessDecision.allow("Access granted");
    }

    private boolean matchesCondition(Policy policy, AccessRequest request) {
        // Evaluate policy conditions (user, role, time, location, etc.)
        return request.getUser().equals(policy.getUser()) ||
               request.getRole().equals(policy.getRole());
    }
}
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Data Governance Internals

## Metadata Storage
`java
@Entity
@Table(name = "data_assets")
public class DataAsset {
    @Id private String id;
    private String name;
    private String description;
    private String domain;
    private String owner;
    private String steward;
    @Enumerated(EnumType.STRING)
    private AssetType type;
    @Enumerated(EnumType.STRING)
    private Classification classification;
    private String schemaJson;
    private String tags;
    private Instant createdAt;
    private Instant updatedAt;
    private int qualityScore;
    private long recordCount;
    private long sizeBytes;
}

@Entity
@Table(name = "lineage_edges")
public class LineageEdge {
    @Id private String id;
    private String sourceDataset;
    private String targetDataset;
    private String sourceColumns;  // JSON array
    private String targetColumns;  // JSON array
    private String transformation;
    private String executionId;
    private Instant timestamp;
}

@Entity
@Table(name = "governance_policies")
public class Policy {
    @Id private String id;
    private String name;
    private String description;
    private String resource;  // Dataset, column, or pattern
    private String user;
    private String role;
    private boolean isAllow;
    private boolean active;
    private Instant effectiveFrom;
    private Instant effectiveTo;
    private String createdBy;
    private Instant createdAt;
}
`

## OpenLineage Integration
`java
// OpenLineage standard for emitting lineage
// library: io.openlineage:openlineage-java
OpenLineageClient client = OpenLineageClient.builder()
    .transport(transport)
    .build();

OpenLineage.RunEvent event = openLineage.newRunEventBuilder()
    .eventType(EventType.COMPLETE)
    .run(openLineage.newRun(runId))
    .job(openLineage.newJob("my-job", "spark"))
    .inputs(openLineage.newDataset("source-table", "postgresql"))
    .outputs(openLineage.newDataset("target-table", "delta-lake"))
    .build();

client.emit(event);
`
"@

System.Collections.Hashtable["MATH_FOUNDATION.md"] = @"
# Math Foundation for Data Governance

## Compliance Risk
`
RiskScore = Sigma(Regulation * Likelihood * Impact)
NonComplianceCost = Probability * FineAmount + RemediationCost

GDPR Fine = max(10M EUR, 2% global revenue) or max(20M EUR, 4% global revenue)
`

## Data Classification Coverage
`
ClassifiedData = TaggedData + AutoDiscoveredData
DiscoveredRate = NewClassified / TotalNewData
ClassificationAccuracy = CorrectlyClassified / TotalClassified

Target: >95% discovery rate, >99% accuracy
`

## Catalog Coverage
`
CatalogCoverage = CatalogedAssets / TotalAssets * 100
LineageCoverage = TrackedAssets / CatalogedAssets * 100
PolicyCoverage = GovernedData / TotalData * 100

DataSwampRatio = 1 - CatalogCoverage
Target: CatalogCoverage > 90%
`

## Data Lifecycle Costs
`
StorageCost = Size * CostPerGB * RetentionDays
ArchiveCost = Size * ArchiveCostPerGB * ArchiveDays
DeletionSavings = Size * CostPerGB * EliminationDays

OptimalRetention = Cost(Storage) - Benefit(DataValue)
TotalDataFootprint = Sigma(AllDatasets) over time
`
"@

System.Collections.Hashtable["VISUAL_GUIDE.md"] = @"
# Visual Guide to Data Governance

## Data Governance Framework
`
+-------------------------------------------------------+
|                    DATA GOVERNANCE                      |
+----------+---------+----------+---------+-------------+
| Catalog  | Lineage | Policies | Quality | Compliance  |
+----------+---------+----------+---------+-------------+
|          |         |          |         |             |
| Find     | Track   | Control  | Trust   | Regulations |
| data     | origin  | access   | metrics | adherence   |
| assets   | & usage |          |         |             |
+----------+---------+----------+---------+-------------+
`

## Lineage Visualization
`
Source Systems        ETL Pipeline         Data Warehouse
+----------+     +--------------+     +----------------+
| MySQL    |     |              |     | fact_orders    |
| orders   |---->| Spark Job    |---->| dim_customer   |
+----------+     | daily_prices |     | dim_product    |
                 |              |     +----------------+
+----------+     +--------------+            |
| CRM API  |          |                     v
| customers|----------+              +----------------+
+----------+     +--------------+     | BI Dashboard  |
                 | Data Quality |     | Revenue KPIs  |
+----------+     | Validation   |---->| Customer 360  |
| CSV Files |     +--------------+     +----------------+
| products  |----------+
+----------+
`

## Compliance Data Flow
`
+------------------+     +------------------+     +------------------+
| PII Detection    |     | Access Control   |     | Audit Log        |
| - Regex patterns |---->| - Role-based     |---->| - All access     |
| - ML classifier  |     | - Column masking |     |   recorded       |
| - Manual tags    |     | - Encryption     |     | - Retention      |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        v                        v                        v
+-----------------------------------------------------------+
|                  Compliance Report                          |
| GDPR: All PII tagged, access logged, right to delete       |
| CCPA: Consumer data mapped, opt-out mechanism in place    |
| SOX: Financial data lineage complete, access audited      |
+-----------------------------------------------------------+
`
"@

System.Collections.Hashtable["CODE_DEEP_DIVE.md"] = @"
# Code Deep Dive: Data Governance Platform

## Complete Governance Platform
`java
@SpringBootApplication
@EnableJpaAuditing
@EnableScheduling
public class GovernanceApplication {
    public static void main(String[] args) {
        SpringApplication.run(GovernanceApplication.class, args);
    }

    @Bean
    public MetadataExtractor metadataExtractor(SparkSession spark) {
        return new SparkMetadataExtractor(spark);
    }

    @Bean
    public OpenLineageClient openLineageClient() {
        return OpenLineageClient.builder()
            .transport(new HttpTransport("http://marquez:5000"))
            .build();
    }
}

// REST API for governance operations
@RestController
@RequestMapping("/api/v1/governance")
public class GovernanceApi {

    private final CatalogService catalog;
    private final LineageService lineage;
    private final PolicyService policies;
    private final ComplianceService compliance;

    // Data Catalog Endpoints
    @GetMapping("/catalog")
    public ResponseEntity<Page<DataAsset>> searchCatalog(
            @RequestParam(required = false) String q,
            @RequestParam(required = false) String domain,
            @RequestParam(required = false) String owner,
            Pageable pageable) {
        return ResponseEntity.ok(catalog.search(q, domain, owner, pageable));
    }

    @GetMapping("/catalog/{id}")
    public ResponseEntity<DataAsset> getAsset(@PathVariable String id) {
        return ResponseEntity.ok(catalog.getAsset(id));
    }

    @PostMapping("/catalog")
    public ResponseEntity<DataAsset> registerAsset(@RequestBody DataAsset asset) {
        return ResponseEntity.ok(catalog.register(asset));
    }

    @PostMapping("/catalog/bulk")
    public ResponseEntity<List<DataAsset>> bulkRegister(
            @RequestBody List<DataAsset> assets) {
        return ResponseEntity.ok(catalog.bulkRegister(assets));
    }

    // Lineage Endpoints
    @GetMapping("/lineage/{assetId}")
    public ResponseEntity<LineageGraph> getLineage(
            @PathVariable String assetId,
            @RequestParam(defaultValue = "UPSTREAM") LineageDirection direction,
            @RequestParam(defaultValue = "3") int depth) {
        return ResponseEntity.ok(lineage.getLineage(assetId, direction, depth));
    }

    @GetMapping("/lineage/impact/{assetId}")
    public ResponseEntity<List<ImpactAnalysis>> impactAnalysis(
            @PathVariable String assetId) {
        return ResponseEntity.ok(lineage.analyzeImpact(assetId));
    }

    // Policy Endpoints
    @GetMapping("/policies")
    public ResponseEntity<List<Policy>> getPolicies(
            @RequestParam(required = false) String resource) {
        return ResponseEntity.ok(policies.findByResource(resource));
    }

    @PostMapping("/policies/evaluate")
    public ResponseEntity<AccessDecision> evaluatePolicy(
            @RequestBody AccessRequest request) {
        return ResponseEntity.ok(policies.evaluate(request));
    }

    @PostMapping("/policies")
    public ResponseEntity<Policy> createPolicy(@RequestBody Policy policy) {
        return ResponseEntity.ok(policies.create(policy));
    }

    // Compliance Endpoints
    @GetMapping("/compliance/{regulation}")
    public ResponseEntity<ComplianceReport> complianceReport(
            @PathVariable String regulation) {
        return ResponseEntity.ok(compliance.generateReport(regulation));
    }

    @PostMapping("/compliance/gdpr/delete-request")
    public ResponseEntity<Void> handleGdprDeleteRequest(
            @RequestBody GdprRequest request) {
        compliance.handleDeleteRequest(request);
        return ResponseEntity.accepted().build();
    }

    // Quality Endpoints
    @GetMapping("/quality/{datasetId}")
    public ResponseEntity<QualityReport> getQuality(
            @PathVariable String datasetId) {
        return ResponseEntity.ok(catalog.getQualityReport(datasetId));
    }

    @GetMapping("/metrics")
    public ResponseEntity<GovernanceMetrics> getMetrics() {
        return ResponseEntity.ok(catalog.getGovernanceMetrics());
    }
}

// Scheduled governance tasks
@Component
public class GovernanceScheduler {

    @Scheduled(cron = "0 0 2 * * ?") // Daily at 2 AM
    public void runAutoDiscovery() {
        // Discover new data assets
        List<DataAsset> discovered = metadataExtractor.discoverNewAssets();
        catalog.bulkRegister(discovered);
    }

    @Scheduled(cron = "0 0 3 * * ?") // Daily at 3 AM
    public void runPiiDetection() {
        // Scan for unclassified PII
        List<PiiFinding> findings = piiDetector.scanAllAssets();
        for (PiiFinding finding : findings) {
            catalog.updateClassification(
                finding.getAssetId(), Classification.PII);
        }
    }

    @Scheduled(cron = "0 0 4 * * ?") // Daily at 4 AM
    public void generateComplianceReports() {
        for (Regulation reg : Regulation.values()) {
            ComplianceReport report = compliance.generateReport(reg);
            reportRepository.save(report);
        }
    }
}
`
"@

System.Collections.Hashtable["STEP_BY_STEP.md"] = @"
# Step-by-Step Data Governance Setup

## Step 1: Define Data Domains
`yaml
# domains.yaml
domains:
  - name: Sales
    owner: sales-team@company.com
    steward: data-steward@company.com
    description: Sales and revenue data
  - name: Marketing
    owner: marketing-team@company.com
    description: Campaign and customer data
  - name: Finance
    owner: finance-team@company.com
    steward: finance-da@company.com
    description: Financial data (SOX governed)
`

## Step 2: Set Up Data Catalog
`java
@Bean
public DataCatalog catalog() {
    return new ApacheAtlasCatalog("http://atlas:21000");
    // or: return new AmundsenCatalog("neo4j://amundsen:7687");
    // or: return new DataHubCatalog("http://datahub:8080");
}
`

## Step 3: Configure Lineage
`properties
# lineage.properties
lineage.openlineage.url=http://marquez:5000
lineage.spark.listener.enabled=true
lineage.auto.capture=true
lineage.retention.days=90
`

## Step 4: Define Policies
`java
@PostConstruct
public void initDefaultPolicies() {
    policyService.create(Policy.builder()
        .name("PII Access Restriction")
        .resource("*.pii.*")
        .role("PII_ACCESS")
        .isAllow(true)
        .description("Only users with PII_ACCESS role can view PII data")
        .active(true)
        .build());

    policyService.create(Policy.builder()
        .name("Finance Data Audit")
        .resource("finance.*")
        .condition("data_classification == 'SOX'")
        .isAllow(true)
        .description("All access to finance data is audited")
        .active(true)
        .build());
}
`

## Step 5: Compliance Setup
`java
@Bean
public PiiDetector piiDetector() {
    return new PiiDetector(Arrays.asList(
        new RegexPiiRule("EMAIL", "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"),
        new RegexPiiRule("SSN", "\\d{3}-\\d{2}-\\d{4}"),
        new RegexPiiRule("CREDIT_CARD", "\\d{4}-\\d{4}-\\d{4}-\\d{4}"),
        new MLPiiClassifier("pii-model.bin")
    ));
}
`

## Step 6: Setup Monitoring
`java
@Bean
public GovernanceDashboard dashboard() {
    return new GovernanceDashboard(metricRegistry);
}

// Metrics to track:
// governance.catalog.coverage
// governance.lineage.coverage
// governance.policy.enforcement.count
// governance.compliance.score
// governance.pii.discovery.rate
// governance.quality.score
`
"@

System.Collections.Hashtable["COMMON_MISTAKES.md"] = @"
# Common Data Governance Mistakes

## 1. Governance as a One-Time Project
`java
// WRONG - set up catalog once, never update
catalogService.importAllAssets();

// RIGHT - continuous discovery and updates
@Scheduled(cron = "0 0 2 * * ?")
public void continuousDiscovery() {
    catalogService.discoverAndUpdate();
}
`

## 2. Too Restrictive
`java
// WRONG - block everything
policyService.create(Policy.denyAll());

// RIGHT - enable with guardrails
policyService.create(Policy.builder()
    .effect(Effect.ALLOW)
    .condition("role != 'ANALYST' OR classification != 'PII'")
    .build());
`

## 3. Ignoring Business Metadata
`java
// WRONG - only technical metadata
// Table: fact_orders (name, type, size)

// RIGHT - include business context
// Table: fact_orders
// Business Name: Daily Order Summary
// Description: Aggregated order metrics by day
// Domain: Sales
// Owner: John Smith
// Steward: Jane Doe
`

## 4. No Automated Enforcement
`java
// WRONG - manual review process
// "Please review this data access request"

// RIGHT - automated policy evaluation
AccessDecision decision = policyEngine.evaluate(request);
// decision.isAllowed() returns immediately
`
"@

System.Collections.Hashtable["DEBUGGING.md"] = @"
# Debugging Data Governance

## Common Issues

### Missing Catalog Entries
`java
// Check if auto-discovery is running
@Scheduled(cron = "0 0 2 * * ?")
public void autoDiscovery() {
    List<DataAsset> assets = metadataExtractor.discover();
    log.info("Discovered {} new assets", assets.size());
}
`

### Broken Lineage
`java
// Verify Spark lineage listener
spark.conf().set("spark.extraListeners",
    "io.openlineage.spark.agent.OpenLineageSparkListener");

// Check lineage database
lineageRepo.findAll().forEach(edge -> {
    log.info("{} -> {} via {}", edge.getSource(),
        edge.getTarget(), edge.getTransformation());
});
`

### Policy Not Working
`java
// Test policy evaluation
AccessDecision result = policyEngine.evaluate(
    AccessRequest.builder()
        .user("test_user")
        .resource("finance.revenue")
        .action(Action.READ)
        .build());
log.info("Policy result: {}", result);
`

### Compliance Issues
`java
// Find untagged PII
piiDetector.scanUnclassified()
    .forEach(finding -> log.warn("Found PII in {}: {}",
        finding.getAssetId(), finding.getColumn()));
`
"@

System.Collections.Hashtable["REFACTORING.md"] = @"
# Refactoring Data Governance

## Before: No Governance
`java
// Anyone can access any data
spark.sql("SELECT * FROM customers").show();
`

## After: Policy Enforced
`java
// Access control at the catalog level
spark.sql("SELECT * FROM governed.customers").show();
// Automatically filtered by policies
`

## Before: Manual Documentation
`sql
-- README.txt: "This table contains orders..."
-- (out of date within days)
`

## After: Automated Catalog
`java
// Schema, description, lineage auto-captured
catalog.getAsset("fact_orders");
// Returns: schema, owner, domain, lineage, quality score
`

## Before: No Lineage
`
// "Where does this data come from?"
// 2-hour investigation
`

## After: Automated Lineage
`
lineageService.getLineage("fact_orders");
// Returns: CRM -> ETL -> fact_orders -> BI Dashboard
`
"@

System.Collections.Hashtable["PERFORMANCE.md"] = @"
# Data Governance Performance

## Catalog Optimization
`java
// Index catalog for fast search
@Entity
@Table(name = "data_assets", indexes = {
    @Index(name = "idx_name", columnList = "name"),
    @Index(name = "idx_domain", columnList = "domain"),
    @Index(name = "idx_owner", columnList = "owner"),
    @Index(name = "idx_classification", columnList = "classification")
})
public class DataAsset { ... }
`

## Lineage Query Performance
`java
// Cache lineage graphs for popular assets
@Cacheable(value = "lineage", key = "#assetId + ':' + #direction")
public LineageGraph getLineage(String assetId, LineageDirection direction) {
    return computeLineage(assetId, direction);
}

// Batch lineage updates
@EventListener
public void onBatchComplete(BatchExecutionEvent event) {
    List<LineageEdge> edges = event.getEdges();
    lineageRepo.saveAll(edges); // Batch insert
}
`

## Policy Evaluation Performance
`java
// Cache policy decisions
@Cacheable(value = "policies", key = "#request.cacheKey()")
public AccessDecision evaluate(AccessRequest request) {
    return evaluatePolicies(request);
}

// Policy evaluation with decision trees
// Instead of O(n) policy iteration, use indexed policy matching
`

## Metadata Storage
`java
// Use read-optimized storage
// Technical metadata: Hive Metastore / AWS Glue
// Business metadata: Neo4j / Elasticsearch
// Operational metadata: TimescaleDB / InfluxDB
`
"@

System.Collections.Hashtable["SECURITY.md"] = @"
# Data Governance Security

## Authentication & Authorization
`java
@Configuration
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        http.authorizeRequests()
            .antMatchers("/api/v1/governance/policies/**")
            .hasRole("GOVERNANCE_ADMIN")
            .antMatchers("/api/v1/governance/compliance/**")
            .hasRole("COMPLIANCE_OFFICER")
            .antMatchers("/api/v1/governance/catalog/**")
            .hasAnyRole("DATA_ENGINEER", "DATA_ANALYST")
            .anyRequest().authenticated()
            .and().oauth2ResourceServer().jwt();
        return http.build();
    }
}
`

## Data Masking
`java
// Dynamic data masking based on classification
@Aspect
@Component
public class DataMaskingAspect {
    @Around("@annotation(MaskedQuery)")
    public Object maskResults(ProceedingJoinPoint pjp) throws Throwable {
        Object result = pjp.proceed();
        if (result instanceof Dataset) {
            Dataset<Row> data = (Dataset<Row>) result;
            // Apply masking based on user's role
            if (!userContext.hasRole("PII_ACCESS")) {
                data = data.withColumn("email",
                    functions.regexp_replace(col("email"),
                        "(?<=.{3}).(?=.*@)", "*"));
                data = data.withColumn("phone",
                    functions.regexp_replace(col("phone"),
                        "\\d{3}", "***"));
            }
            return data;
        }
        return result;
    }
}
`

## Audit Logging
`java
@Aspect
@Component
public class AuditAspect {
    @Around("@annotation(Audited)")
    public Object audit(ProceedingJoinPoint pjp) throws Throwable {
        String user = SecurityContextHolder.getContext()
            .getAuthentication().getName();
        String method = pjp.getSignature().getName();
        Object[] args = pjp.getArgs();

        auditService.log(AuditEntry.builder()
            .user(user)
            .action(method)
            .resource(args.length > 0 ? args[0].toString() : null)
            .timestamp(Instant.now())
            .build());

        return pjp.proceed();
    }
}
`

## Encryption
`java
// Encrypt sensitive metadata
@Entity
public class DataAsset {
    @Convert(converter = EncryptionConverter.class)
    private String description; // Encrypted at rest

    @Convert(converter = EncryptionConverter.class)
    private String schemaJson; // Contains column descriptions
}
`
"@

System.Collections.Hashtable["ARCHITECTURE.md"] = @"
# Data Governance Architecture

## Governance Platform Architecture
`
+----------------------------------------------------------+
|                   Governance Platform                      |
+------------+-------------+-------------+------------------+
| Data       | Data        | Policy      | Compliance       |
| Catalog    | Lineage     | Engine      | Engine           |
| - Search   | - Tracking  | - Evaluate  | - GDPR           |
| - Browse   | - Impact    | - Enforce   | - CCPA           |
| - Register | - Debug     | - Audit     | - SOX            |
+------------+-------------+-------------+------------------+
|            |             |             |                  |
+------------+-------------+-------------+------------------+
|              Metadata Storage Layer                        |
| PostgreSQL  | Neo4j       | Elasticsearch | Kafka         |
+----------------------------------------------------------+
|              Data Collection Layer                         |
| Spark Listeners | Kafka Connect | JDBC | REST APIs        |
+----------------------------------------------------------+
`

## Spring Boot Integration
`java
@SpringBootApplication
@EnableGovernance
public class GovernanceApplication {
    public static void main(String[] args) {
        SpringApplication.run(GovernanceApplication.class, args);
    }

    @Bean
    public DataPlatformMetadataExtractor metadataExtractor() {
        return new DataPlatformMetadataExtractor(
            Environment.getCatalogs(),
            Environment.getLineageListeners()
        );
    }
}
`

## Integration with Data Platforms
`yaml
# Integration with common tools
governance:
  catalog:
    type: datahub  # datahub, amundsen, atlas, collibra
    url: http://datahub:8080
  lineage:
    openlineage:
      enabled: true
      url: http://marquez:5000
  quality:
    great-expectations:
      datasource: spark
  policies:
    ranger:
      url: http://ranger:6080
  metadata:
    hive:
      metastore: thrift://hive-metastore:9083
`
"@

System.Collections.Hashtable["EXERCISES.md"] = @"
# Data Governance Exercises

## Exercise 1: Data Catalog
Build a simple data catalog with search functionality and metadata management.

## Exercise 2: Lineage Tracking
Implement lineage capture for a Spark ETL pipeline using OpenLineage.

## Exercise 3: Policy Enforcement
Create a policy engine that evaluates access requests based on user role and data classification.

## Exercise 4: PII Detection
Build a classifier that automatically identifies PII columns in datasets.

## Exercise 5: Compliance Report
Generate a GDPR compliance report showing all PII data and access history.
