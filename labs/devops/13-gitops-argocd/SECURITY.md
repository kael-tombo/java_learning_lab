# Security in ArgoCD & GitOps

## Authentication Mechanisms

### Single Sign-On (SSO) with Dex
ArgoCD integrates with Dex as an OIDC proxy. Dex supports multiple identity providers:
- LDAP / Active Directory
- GitHub / GitLab / Bitbucket
- Google Workspace
- Microsoft Azure AD
- SAML providers (Okta, OneLogin)
- OpenID Connect providers (Keycloak, Okta, Auth0)

Configuration is done via the argocd-cm ConfigMap where Dex connectors are defined. Users authenticate through their existing identity provider, and ArgoCD receives the user's identity and group memberships as claims.

### Local Users
ArgoCD maintains a local admin user with a bcrypt-hashed password. Additional local users can be configured in argocd-cm with bcrypt-hashed passwords. This is primarily for bootstrapping and backup access.

### Token-Based Authentication
- JWT tokens for CI/CD integration
- Bearer tokens for API access
- Session tokens for web UI
- All tokens are signed by ArgoCD's private key and have configurable time-to-live

## Authorization (RBAC)

### Policy Model
ArgoCD uses a RBAC policy model based on Casbin. Each policy rule has the format:

p, subject, resource, action, object, effect

Example policies:
- p, role:admin, applications, *, */*, allow
- p, role:developer, applications, sync, team-alpha/*, allow
- p, role:viewer, applications, get, */*, allow
- p, role:viewer, clusters, get, *, allow

### Built-in Roles
- role:admin - Full access to all resources
- role:readonly - Read-only access to all resources
- Custom roles can be defined per project

### Scopes
RBAC decisions can use:
- User identity (sub claim)
- Group memberships (groups claim)
- Email domain
- Custom claims from OIDC providers

## Network Security

### TLS Configuration
- All ArgoCD components communicate over TLS
- API Server serves HTTPS with configurable TLS certificates
- Repository Server uses mTLS for gRPC communication
- Redis passwords are required for production deployments

### Network Policies
- Restrict egress from Repository Server to only Git repositories
- Restrict ingress to API Server to known IP ranges
- Application Controller needs egress to all managed cluster API servers
- Separate network zones for control plane vs managed clusters

## Secret Management

### GitOps Secret Challenges
Secrets cannot be stored in plain text in Git. Solutions include:
1. Sealed Secrets: Encrypt secrets with a controller in the cluster
2. External Secrets Operator: Sync secrets from external providers (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, HashiCorp Vault)
3. SOPS: Encrypt individual values in YAML files with age, PGP, or KMS
4. ArgoCD Vault Plugin: Retrieve secrets from Vault during manifest generation

### ArgoCD Secret Storage
- argocd-secret contains: admin password, server signing key, dex client secret
- redis-haproxy password for Redis authentication
- Cluster credentials stored as Kubernetes Secrets in the argocd namespace
- All secrets should be rotated regularly

## Supply Chain Security

### Git Commit Verification
- GPG signature verification for commits
- Signed commits ensure integrity of the source of truth
- ArgoCD can be configured to reject unsigned commits

### Image Security
- Integration with container image scanners (Trivy, Snyk, Aqua)
- Image signature verification with Cosign
- Admission controllers for enforcing image policies

### Kubernetes RBAC Integration
- ArgoCD should run with minimal Kubernetes RBAC permissions
- Applications should use separate service accounts per namespace
- Project-scoped destinations limit blast radius

## Audit Logging

### Audit Events
ArgoCD logs audit events for:
- Application creation, update, deletion
- Sync operations and results
- RBAC changes
- Authentication attempts (success and failure)
- Parameter overrides
- Manual interventions (rollbacks, refreshes)

### Audit Log Storage
- Events are stored in Kubernetes events in the argocd namespace
- Logs are output to stdout/stderr for collection (Fluentd, Logstash, Datadog)
- Webhook notifications can forward audit events to external systems
