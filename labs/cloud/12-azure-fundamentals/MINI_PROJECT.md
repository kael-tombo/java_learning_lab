# Azure Fundamentals - Mini Project

## Project: A Java Service on Azure with Managed Identity

### Objective
Deploy a Java service that authenticates to Azure SQL and Blob Storage using managed identity,
provisioned through infrastructure as code, with tags and RBAC applied at the correct scopes.

### Requirements
1. Resource group with a naming and tagging standard applied to every resource
2. Java application using managed identity to acquire tokens — no keys in configuration
3. Azure SQL Database with least-privilege RBAC for the app identity
4. Blob Storage container with the app granted only the operations it uses
5. Tests verifying the identity flow and the RBAC boundaries

### Steps

**Step 1: Naming and tags first**
```
Pattern: {env}-{service}-{resource}-{region}
  prod-orders-sql-db-westeurope
  prod-orders-storage-westeurope
Required tags on everything: env, service, owner, costCentre, dataClassification
```
A resource created without tags should fail the deployment pipeline, not survive to be found
six months later by a cost audit. Add the tag check to your IaC plan output — a resource
without the required tags is a failed deployment.

**Step 2: Provision the resource group**
```hcl
resource "azurerm_resource_group" "app" {
  name     = "rg-prod-orders-westeurope"
  location = "westeurope"
  tags     = local.required_tags
}
```
Every resource goes inside it. Resource groups are the RBAC scope and the lifecycle boundary,
so getting this right once prevents a pile of one-off assignments later.

**Step 3: Managed identity, not a connection string**
```java
public record AzureClients(AzServices clients, TokenCredential credential) {}

public static AzureClients connect() {
    // In App Service / AKS, this picks up the workload identity automatically
    var credential = new DefaultAzureCredentialBuilder().build();
    var clients = new AzServices(credential);   // no key anywhere in this code
    return new AzureClients(clients, credential);
}
```
Then verify by finding the real permission: the app identity needs a role assignment, not a
password. A managed-identity-only system has no secret to rotate and nothing to leak in
source control — that is the entire point.

**Step 4: RBAC at the correct scope**
```java
record RoleAssignment(String principalId, String roleDefinitionId, String scope) {}
// scope = the SQL database, NOT the subscription
var sql = new RoleAssignment(appPrincipalId, "SQL DB Contributor",
        "https://management.azure.com" + databaseId);
// storage: only the container needs Blob Data Reader, not the whole storage account
var blob = new RoleAssignment(appPrincipalId, "Storage Blob Data Reader",
        "https://management.azure.com" + containerId);
```
Scope the assignment to the resource, not the subscription. Two tests follow directly:
the app can read the container, and the app cannot read a *different* container.

**Step 5: Connect and verify**
```java
// Azure SQL: connection built from token, no password
var token = credential.getToken(new TokenRequestContext()
        .addScopes("https://database.windows.net/.default")).getToken();
var dataSource = createDataSource(token.getTokenValue());

// Blob: SDK handles the credential
var container = clients.getBlobServiceClient()
        .getBlobContainerClient(containerName);
container.listBlobs().forEach(b -> System.out.println(b.getName()));
```

**Step 6: Test the boundaries**
```java
@Test
void appCanReadItsOwnContainerButNotAnother() {
    assertThat(canRead(container("orders-in"))).isTrue();
    assertThat(canRead(container("finance-out"))).isFalse();   // scope, not convenience
}

@Test
void noSecretExistsInTheRepositoryOrEnvironment() {
    assertThat(scanConfigAndSourceFor("AccountKey=")).isEmpty();
    assertThat(scanConfigAndSourceFor("password=")).isEmpty();
}
```
That second test is the one to keep in CI permanently. It makes "no secrets" an enforced
property rather than an intention.

### Deliverables
1. IaC with naming and required tags enforced at plan time
2. Java application authenticating entirely through managed identity
3. Scoped RBAC assignments with the boundary tests proving isolation
4. CI check that fails if any credential appears in source or config

### Extension (CHALLENGE)
Deploy the same service to AKS with workload identity and compare the token flow with the App
Service case — then document which is harder and why.

### Estimated Time
3-4 hours