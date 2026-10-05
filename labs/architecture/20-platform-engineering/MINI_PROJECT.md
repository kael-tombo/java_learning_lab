# Mini Project — Platform Engineering

## Goal

Build a minimal internal developer platform (IDP) that provides
self-service infrastructure provisioning, CI/CD pipelines, and
standardized application templates. Demonstrate how platform
engineering reduces developer friction.

## Requirements

### Self-Service Infrastructure

**Infrastructure as Code:**
- Terraform templates for common resources (databases, caches, queues)
- Self-service portal or CLI for provisioning
- Environment management (dev, staging, production)

### CI/CD Pipelines

**Automated Workflows:**
- Build and test on every pull request
- Automated deployment to staging
- Manual approval for production
- Rollback capability

### Application Templates

**Golden Path Templates:**
- Service template with standard structure
- Built-in observability (logging, metrics, tracing)
- Pre-configured CI/CD pipeline
- Security scanning integration

### Platform Services

**Shared Services:**
- Container registry
- Secret management
- Monitoring and alerting
- Service catalog

## Technical Specifications

1. **Self-service portal**
   - Web UI or CLI for resource provisioning
   - Terraform/CloudFormation templates
   - Approval workflows for production

2. **CI/CD automation**
   - Pipeline as code (GitHub Actions, GitLab CI, etc.)
   - Automated testing and security scanning
   - Deployment automation with rollback

3. **Templates**
   - Cookiecutter or similar for service scaffolding
   - Standardized project structure
   - Built-in best practices

4. **Platform APIs**
   - APIs for resource provisioning
   - Service catalog API
   - Usage and cost tracking

## Steps

1. Design platform architecture
2. Create infrastructure templates
3. Build self-service provisioning flow
4. Implement CI/CD pipeline templates
5. Create application templates
6. Add monitoring and alerting
7. Build service catalog
8. Document platform usage
9. Test end-to-end workflow

## Acceptance Criteria

- [ ] Developers can provision infrastructure self-service
- [ ] CI/CD pipelines are automated and reliable
- [ ] Application templates follow golden path
- [ ] Platform services are available to all teams
- [ ] Platform usage is monitored
- [ ] Documentation is clear and complete

## Stretch Goals

- Implement GitOps-based deployments
- Add cost optimization recommendations
- Implement platform-level policies (security, compliance)
- Add developer portal with self-service documentation
