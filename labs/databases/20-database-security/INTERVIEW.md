# Interview Questions: Database Security (Oracle Focus)

## Oracle-Specific Questions
- Explain Oracle's security architecture: authentication, authorization, and auditing (AAA).
- How does Oracle Transparent Data Encryption (TDE) work? Explain column-level and tablespace-level encryption.
- What is Oracle Database Vault? How does it prevent privileged user access to application data?
- Explain Oracle's fine-grained access control (VPD) with `DBMS_RLS` for row-level security.
- How does Oracle auditing work? Compare standard auditing, fine-grained auditing (FGA), and unified auditing.
- What is Oracle Data Redaction? How does it mask sensitive data at query time?
- Explain Oracle's network encryption: Oracle Net Services encryption and integrity settings.
- How does Oracle key management work with Oracle Wallet and Oracle Key Vault?

## Google Cloud / Technical
- Cloud CMEK vs Oracle TDE for encryption key management
- Cloud Audit Logs vs Oracle Unified Auditing
- Cloud IAM vs Oracle Database Vault for access control

## Microsoft / Azure
- Azure SQL TDE vs Oracle TDE comparison
- Azure Defender for SQL vs Oracle Database Security
- Azure Key Vault vs Oracle Wallet for key management

## Amazon / AWS
- AWS KMS vs Oracle TDE for encryption at rest
- Amazon GuardDuty vs Oracle Database Security monitoring
- RDS Oracle encryption options and limitations

## Apple
- Apple's data privacy requirements for database security
- Database encryption for Apple user data compliance

## LeetCode-Style Problems
| Problem | Topic | Difficulty | Pattern |
|---------|-------|-----------|---------|
| Encryption | TDE Setup | Medium | Key Management |
| Auditing | FGA Policy | Medium | Security Monitoring |
| Access Control | VPD Policy | Hard | Row-Level Security |
| Password Mgmt | Password Hash | Medium | Secure Storage |

## Production Scenarios
- Scenario 1: "TDE master key lost after server recovery — data inaccessible"
- Scenario 2: "VPD policy causing query performance regression across all queries"
- Scenario 3: "Database Vault blocking legitimate DBA maintenance operations"
- Scenario 4: "Unified Auditing filling SYSTEM tablespace — database crash"

## Interview Patterns & Tips
- Oracle security interviews cover TDE, VPD, Database Vault, and Auditing
- Expect scenario-based questions about data breaches and compliance
- OCP Database Security certification covers all Oracle security features
- Security specialists: $130K-$200K; CISSP + Oracle skills: $150K-$220K
- Oracle Key Vault and Database Vault knowledge is highly valued
