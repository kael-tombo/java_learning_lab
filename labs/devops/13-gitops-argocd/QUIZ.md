# GitOps & ArgoCD Quiz

## Section 1: GitOps Principles (20 Questions)

1. What are the five core principles of GitOps?
2. How does the pull-based deployment model differ from traditional push-based CI/CD?
3. What is the role of a Git repository in GitOps?
4. Explain how self-healing works in a GitOps workflow.
5. What is configuration drift and how does GitOps prevent it?
6. Why is declarative configuration important for GitOps?
7. How does GitOps provide an audit trail for infrastructure changes?
8. What is the difference between GitOps and Infrastructure as Code?
9. How does GitOps handle rollbacks compared to traditional deployment methods?
10. What is the Kubernetes operator pattern and how does it relate to GitOps?
11. Explain the reconciliation loop in GitOps.
12. What is the difference between automated sync and manual sync?
13. How does GitOps handle secrets management?
14. What are the security implications of a pull-based deployment model?
15. How does GitOps support multi-environment deployments?
16. Explain the concept of progressive delivery in GitOps.
17. What is the role of CI in a GitOps workflow?
18. How does GitOps handle emergency hotfixes?
19. What are the challenges of implementing GitOps in existing infrastructure?
20. Compare ArgoCD and Flux as GitOps operators.

## Section 2: ArgoCD Specific (20 Questions)

21. What are the main components of ArgoCD architecture?
22. How does the ArgoCD repository server work?
23. What is the purpose of the ArgoCD application controller?
24. Explain the Application model in ArgoCD.
25. How does ArgoCD handle authentication and RBAC?
26. What is an ArgoCD Project and how is it used?
27. How does ArgoCD integrate with Helm?
28. What are sync waves and how do you configure them?
29. Explain the difference between sync options: PruneLast vs RespectIgnoreDifferences.
30. How does ArgoCD handle resource pruning?
31. What is the purpose of ignoreDifferences in an ArgoCD Application?
32. How does ArgoCD integrate with external secrets managers?
33. Explain the ArgoCD config management plugin system.
34. How does ArgoCD handle SSO integration with Dex?
35. What is the ArgoCD API server and what endpoints does it expose?
36. How does ArgoCD manage multiple Kubernetes clusters?
37. What is the argocd-cm ConfigMap used for?
38. How does ArgoCD handle webhook events from GitHub?
39. Explain the ArgoCD CLI command structure.
40. How does ArgoCD handle high availability?

## Section 3: ApplicationSet (15 Questions)

41. What is an ApplicationSet and why is it useful?
42. Explain the list generator in ApplicationSet.
43. How does the cluster generator work?
44. What is the Git generator and when would you use it?
45. Explain the matrix generator and its use cases.
46. How does the merge generator differ from the matrix generator?
47. What is the SCM provider generator?
48. How does the pull request generator enable review environments?
49. How do you use Go templates in ApplicationSet specs?
50. What are template patches and how do they work?
51. How does ApplicationSet handle template validation?
52. Can ApplicationSets be nested?
53. How does ApplicationSet handle errors during generation?
54. What is the selector field in ApplicationSet generators?
55. How do you test ApplicationSet templates locally?

## Section 4: Multi-Cluster Management (10 Questions)

56. How do you register a cluster with ArgoCD?
57. What are the authentication methods for registering clusters?
58. How does ArgoCD handle cluster credentials?
59. Explain the multi-cluster sync strategy.
60. How do you manage different configurations per cluster?
61. What is cluster labels and how are they used?
62. How does ArgoCD handle cluster disconnection?
63. Can ArgoCD manage clusters that are behind a firewall?
64. How do you monitor sync status across multiple clusters?
65. Explain the disaster recovery workflow for multi-cluster ArgoCD.

Answers are available in THEORY.md, CODE_DEEP_DIVE.md, and the lab exercises.
