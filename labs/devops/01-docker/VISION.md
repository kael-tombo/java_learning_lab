# Vision — Docker

## Why this lab exists
Docker is the substrate every other DevOps lab stands on. If you cannot
package an app reliably, nothing downstream (Kubernetes, CI/CD, GitOps)
will behave predictably.

## What we are building toward
- A developer at this lab should be able to take a fresh repo and produce
  a reproducible, small, secure image without copy-pasting folklore.
- Container builds should be boring: same command, same result, every time.

## Principles
- Immutability over snowflake servers.
- Small images ship faster and break less (fewer CVEs, faster pulls).
- The image is the contract between developers and operators.
- One process per container; state lives in volumes or backing services.

## Anti-patterns to retire
- `docker exec` into prod containers to fix things by hand.
- `latest` as the only tag ever used.
- Baking secrets into image layers.
- 2 GB images for a 20 MB app because nothing was cleaned up.

## Success criteria
- `docker build` works on a clean machine with no local state.
- `docker history` tells a readable story of the image.
- Image size and layer count are measured, not guessed.

## Looking ahead
This vision feeds directly into Kubernetes (lab 02), CI/CD (lab 03), and
gitops + advanced packer baking (labs 12, 16).
