# ArgoCD Architecture

## System Architecture Overview

```
+-------------------+     +-------------------+     +-------------------+
|   Git Repository   |     |   Web Browser      |     |   kubectl/CLI     |
| (Source of Truth)  |     | (ArgoCD UI)        |     | (argocd CLI)      |
+--------+----------+     +---------+---------+     +---------+---------+
         |                          |                           |
         v                          v                           v
+--------+----------+     +---------+---------+     +---------+---------+
|   Repository       |<----+   API Server       |<----+   API Server      |
|   Server           |     |   (gRPC + REST)    |     |   (Auth + TLS)    |
|                    |     |   Port 443          |     |   Port 8080       |
| - Git clone/cache  |     |   - Auth (SSO/OIDC)|     |                   |
| - Helm processing  |     |   - RBAC           |     +--------------------+
| - Kustomize build  |     |   - CRUD operations|
| - Jsonnet eval     |     |   - Web UI serving |
+--------------------+     +---------+----------+
                                      |
                                      v
                         +-----------+----------+
                         | Application Controller|
                         |                      |
                         | - State comparison   |
                         | - Sync orchestration |
                         | - Health assessment  |
                         | - Drift detection    |
                         | - Self-healing       |
                         +------+--------+------+
                                |        |
                     +----------+  +-----+--------+
                     v               v              v
              +-----------+    +-----------+  +-----------+
              | Cluster A  |    | Cluster B  |  | Cluster C |
              | (K8s)      |    | (K8s)      |  | (K8s)     |
              +-----------+    +-----------+  +-----------+
```

## Component Interaction Flow

### Sync Operation Flow
1. User commits changes to Git repository
2. Webhook event sent to ArgoCD API Server (or poll interval triggers)
3. API Server notifies Application Controller
4. Controller requests Repository Server to generate manifests from Git
5. Repository Server clones repo, processes templates, returns rendered manifests
6. Controller compares rendered manifests against live cluster state
7. If OutOfSync, controller applies the manifests to the target cluster
8. Controller monitors resource health until sync completes

### Authentication Flow
1. User accesses ArgoCD UI/CLI
2. Request routed to API Server
3. API Server redirects to Dex/OIDC provider for authentication
4. User authenticates with credentials
5. OIDC provider returns ID token
6. API Server validates token and extracts user claims
7. RBAC engine evaluates authorization based on user claims
8. Authorized requests are processed by the API Server

## Data Flow

### Configuration Data Flow
- Git repositories are cloned and cached by Repository Server
- Repository Server maintains a local cache of repository contents
- When manifests are requested, Repository Server processes them using the configured config management tool
- Processed manifests are returned to the Application Controller
- Application Controller compares and applies manifests to the target cluster

### State Data Flow
- Application Controller watches cluster state via Kubernetes API
- Controller compares live state against desired state from Repository Server
- Differences are logged and reported in the application status
- Self-healing corrections are applied when configured
- Status updates are stored in Redis and served by the API Server

## Network Architecture

### Ports and Protocols
- 443: HTTPS (API Server - UI and API)
- 8080: HTTP (API Server - internal)
- 8443: HTTPS (Repository Server - gRPC)
- 6379: Redis (internal, not exposed)
- 8082: Metrics port for Prometheus scraping

### Network Policies
- API Server: accessible from end users and CI systems
- Repository Server: outbound to Git servers, inbound from API Server and Controller
- Application Controller: outbound to Kubernetes API servers of all managed clusters
- Redis: only accessible within the ArgoCD service mesh

## Storage Architecture

### Redis Cache
- Application state cache
- Repository data cache
- Session information
- JWT token cache

### Kubernetes Resources (ArgoCD namespace)
- argocd-secret: TLS certificates, admin password, signing keys
- argocd-cm: ArgoCD configuration
- argocd-rbac-cm: RBAC configuration
- argocd-ssh-known-hosts-cm: SSH known hosts for Git
- argocd-tls-certs-cm: Custom TLS certificates for Git servers
- argocd-gpg-keys-cm: GPG keys for commit verification
- Various Application, ApplicationSet, and Project CRDs

## High Availability Architecture

### Component Redundancy
- API Server: multiple replicas behind a service
- Repository Server: multiple replicas with distributed caching
- Application Controller: leader election for active-passive, sharding for active-active
- Redis: sentinel or cluster mode for high availability

### Disaster Recovery
- Backup argocd-secret, argocd-cm, argocd-rbac-cm
- Export all Application and ApplicationSet resources
- Git is the source of truth - re-syncing from Git recovers all application state
- Cluster credentials can be re-added from kubeconfig files
