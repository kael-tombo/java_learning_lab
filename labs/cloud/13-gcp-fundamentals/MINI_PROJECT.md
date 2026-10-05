# GCP Fundamentals - Mini Project

## Project: A Private Java Service on Compute Engine and Cloud SQL

### Objective
Deploy a Java service with no external IP address, authenticating to Cloud SQL with a service
account, and prove the network posture is actually private.

### Requirements
1. Project with labels, and a service account with least-privilege roles
2. Compute Engine instance with no external IP; access via IAP TCP forwarding
3. Cloud SQL with private IP only, reached through a VPC private range
4. Java application using application default credentials — no key files
5. Tests verifying the instance is unreachable from the internet and the DB has no public IP

### Steps

**Step 1: Project and labels**
```bash
gcloud projects create orders-prod \
    --labels=env=prod,team=commerce,costcentre=cc-4471
```
Labels control quota, billing export, and policy targeting. Set them at creation, because a
labelled project is auditable and an unlabelled one is a mystery during the first cost review.

**Step 2: Service account, not a key**
```bash
gcloud iam service-accounts create orders-runtime \
    --display-name="Orders service runtime"
gcloud projects add-iam-policy-binding orders-prod \
    --member="serviceAccount:orders-runtime@orders-prod.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"
```
One role. Note what is *not* granted: not `roles/sqladmin`, not owner, not editor. Least
privilege at the role level is the whole exercise.

**Step 3: The instance, with no external IP**
```bash
gcloud compute instances create orders-1 \
    --zone=europe-west1-b \
    --service-account="orders-runtime@orders-prod.iam.gserviceaccount.com" \
    --no-address                       # the flag that matters most in this lab
    --scopes=cloud-platform
```
`--no-address` is the default posture and the default that people disable under time pressure.
Keep it. Access becomes:
```bash
gcloud compute ssh orders-1 --zone=europe-west1-b --tunnel-through-iap
```

**Step 4: Cloud SQL, private only**
```bash
gcloud sql instances create orders-db \
    --availability-type=REGIONAL \
    --network=projects/$PROJECT/global/networks/default \
    --no-assign-ip \
    --enable-private-network
```
1. `REGIONAL` gives a standby in another zone — verify the failover test in phase 5
2. `--no-assign-ip` removes the public endpoint entirely
3. The VPC needs a private services access range first; this ordering trips people up

**Step 5: Java with application default credentials**
```java
public record GcpClients(ComputeClient compute, SqlAdminClient sql, StorageClient storage) {}

public static GcpClients connect() throws IOException {
    // Picks up the attached service account -- no key file, no JSON credential
    var credentials = GoogleCredentials.getApplicationDefault();
    var transport = GoogleHttpTransport.newTrustedTransport();
    return new GcpClients(compute(credentials, transport), sql(credentials, transport),
                          StorageOptions.newBuilder()
                              .setCredentials(credentials).setProjectId(PROJECT).build()
                              .getService());
}
```
Test it: the application starts with no credential file anywhere on disk. That is the claim
worth asserting.

**Step 6: Prove the posture**
```java
@Test
void instanceHasNoExternalAddress() {
    var instance = compute.instances().get(PROJECT, ZONE, "orders-1").execute();
    var accessConfigs = instance.getNetworkInterfaces(0).getAccessConfigs();
    assertThat(accessConfigs).isEmpty();                 // no external IP
}

@Test
void databaseHasNoPublicAddress() {
    var ip = sql.instances().get("orders-db").execute().getIpAddresses();
    assertThat(ip).noneMatch(a -> "PRIMARY".equals(a.getType()));  // public endpoint gone
}
```
Assert the negative properties, not just the positive ones. "It works" does not prove privacy.

### Deliverables
1. Labelled project, service account, and a documented role justification
2. Instance with no external IP, reachable via IAP
3. Cloud SQL with private IP only, and the VPC prerequisite documented
4. Tests asserting no external address on either resource, plus ADC-only authentication

### Extension (CHALLENGE)
Deploy the same service to Cloud Run with the same service account and compare cold start,
instance management, and cost at low and high traffic.

### Estimated Time
3 hours