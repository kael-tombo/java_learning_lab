# Step-by-Step GitOps Guide

## 1. Install ArgoCD
```powershell
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

## 2. Access ArgoCD UI
```powershell
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Username: admin
# Password:
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | %{[Text.Encoding]::Utf8.GetString([convert]::FromBase64String($_))}
```

## 3. Install ArgoCD CLI
```powershell
# Download argocd CLI
argocd login localhost:8080
```

## 4. Create Git Repository
```powershell
# Create a private repo with your K8s manifests
# Example: (link removed)
```

## 5. Deploy via ArgoCD
```powershell
argocd app create myapp \
  --repo (link removed).git \
  --path k8s/overlays/production \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production \
  --sync-policy automated
```

## 6. Check Sync Status
```powershell
argocd app get myapp
argocd app sync myapp
```

## 7. Install Flux
```powershell
# Using Flux CLI
flux install
# Verify
flux check
```

## 8. Create Flux Source and Kustomization
```powershell
flux create source git myapp \
  --url=(link removed) \
  --branch=main
flux create kustomization myapp \
  --source=myapp \
  --path="./k8s/overlays/production" \
  --prune=true \
  --interval=5m
```

## 9. GitOps Workflow Test
```powershell
# Change image tag in Git
# Commit and push
# Watch ArgoCD/Flux auto-sync
```
