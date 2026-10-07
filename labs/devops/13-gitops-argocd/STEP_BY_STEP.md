# ArgoCD Setup: Step by Step

## Step 1: Install ArgoCD
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

## Step 2: Access the UI
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Open https://localhost:8080 in browser
```

## Step 3: Get Admin Password
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## Step 4: Login via CLI
```bash
argocd login localhost:8080 --insecure
# Username: admin, Password: from step 3
```

## Step 5: Register a Cluster
```bash
argocd cluster add my-cluster-context-name
```

## Step 6: Add a Git Repository
```bash
argocd repo add (link removed).git --ssh-private-key-path ~/.ssh/id_rsa
```

## Step 7: Create an Application
```bash
argocd app create myapp \
  --repo (link removed).git \
  --path k8s/overlays/production \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace myapp-production
```

## Step 8: Sync the Application
```bash
argocd app sync myapp
```

## Step 9: Enable Auto-Sync
```bash
argocd app set myapp --sync-policy automated --auto-prune --self-heal
```

## Step 10: Create an ApplicationSet
Create an application-set.yaml file and apply it:
```bash
kubectl apply -f application-set.yaml
```
