# GitOps Refactoring

## Before (Traditional CI/CD Push)
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp .
      - run: docker push myapp
      - run: kubectl set image deployment/myapp myapp=myapp:${{ github.sha }}
      - run: kubectl rollout status deployment/myapp
```

## After (GitOps Workflow)
```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t myapp:${{ github.sha }} .
      - run: docker push myapp:${{ github.sha }}
      - run: |
          # Update image tag in Git config repo
          git clone (link removed)
          cd myapp-config
          sed -i "s|tag:.*|tag: ${{ github.sha }}|" k8s/overlays/production/values.yaml
          git commit -am "Update image to ${{ github.sha }}"
          git push

# GitOps Operator (ArgoCD/Flux) automatically deploys
```

## Gains
- No cluster credentials in CI/CD
- Full audit trail (Git history)
- Easy rollback (git revert)
- Self-healing cluster
- Multi-cluster: same Git repo, different overlays
- Separation of CI (build/test) from CD (deploy)
