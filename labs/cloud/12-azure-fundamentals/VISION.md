# Azure Fundamentals - Vision

## The Big Picture
Azure is a different set of defaults from AWS: resource groups as the unit of lifecycle and
RBAC, managed identity instead of instance profiles, and a naming convention that determines
whether a subscription is navigable or a swamp.

## Why This Matters
Most Azure friction is structural, not technical. Missing tags, inconsistent names, and
resource groups that mix a database with a virtual machine are all cheap to prevent at the
start and expensive to fix later.

## The Vision for This Lab
This lab builds the Azure mental model through Java: provisioning a resource group and
resources, using managed identity instead of secrets, connecting to Azure SQL and Blob
Storage, and deploying to AKS. Every concept is exercised against the real SDK shape.

## Learning Philosophy
1. Resource group is the unit of everything — access, lifecycle, and cost
2. Managed identity is the default; secrets are the exception
3. Naming and tagging are infrastructure, not documentation
4. Prefer platform services over self-managed equivalents

## Future Path
- 14-multi-cloud — where Azure's model differs from the others
- 07-kubernetes — AKS in depth
- 13-gcp-fundamentals — the parallel GCP track

## Success Metrics
You have mastered Azure fundamentals when you can:
- [ ] Create a resource group and provision resources programmatically
- [ ] Authenticate with managed identity and explain the token flow
- [ ] Connect to Azure SQL and Blob Storage from Java
- [ ] Apply RBAC at the right scope, and justify the scope

## The Cloud Mindset
> Two clouds, two sets of defaults. The value of knowing both is not that the tools are the
same — it is that you stop assuming the first one you learned was always true.