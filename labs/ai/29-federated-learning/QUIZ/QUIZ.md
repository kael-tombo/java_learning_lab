# Federated Learning — Quiz

Keys follow the questions; standard statements only.

**Q1. State the FedAvg aggregation formula.**
A: `w_{t+1} = sum_{i in S_t} (n_i / sum_j n_j) * w_{t+1}^i` over chosen clients, with
`n_i` each client's data count.

**Q2. What never moves between client and server in classical FL?**
A: The raw training data; only parameter vectors and update tensors are exchanged.

**Q3. Why does non-IID data make uniform averaging misleading?**
A: With skewed client sizes or distributions, the plain mean over clients no longer
approximates any global objective; size-weighted averaging keeps the population balance.

**Q4. What is client drift?**
A: The divergence of participants' local models from the shared state between
aggregation events, growing with local steps and local learning rate.

**Q5. Name the two costs an FL round pays.**
A: The download (server→client) and the upload (client→server) of model weights for each
selected participant.

**Q6. Why refuse stale updates from late clients in practice?**
A: They were computed against an older global model; folding them in ignores the fact
that weights already moved, corrupting the aggregation.

**Q7. What does a proximal local-penalty approach add to the client's own loss?**
A: A quadratic term keeping local weights close to the transmitted global weights, so
drift between aggregation rounds is dampened.

**Q8. When could uniform and weighted averaging coincide exactly?**
A: When all client data counts are equal — the toy's uniform row then equals the
weighted row; otherwise they differ (observed in snippet 1's outputs).
