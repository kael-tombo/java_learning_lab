# Real-World Project — Packer Image Baking

## Scenario
Your autoscaling groups take 25 minutes to become healthy because
bootstrap installs everything at boot. AMI versions drift between teams,
and a recent incident traced back to an old base image.

## Requirements
- One golden-image pipeline producing versioned AMIs per layer
  (base -> hardened -> app -> config).
- Images scanned for CVEs before publication.
- Boot time target cut by at least 60%.
- Promotion process: dev image -> staging -> prod tags.

## Phase plan
1. **Baseline**: measure current boot-to-healthy and bake time.
2. **Layered templates**: build base, hardened, and app images with
   Packer chains.
3. **Hardening**: apply CIS-style kitchen cleanup, minimal packages.
4. **Pipeline**: build on merge to main; weekly security rebuilds.
5. **Promotion**: tag dev images, smoke-test, promote tags to prod.
6. **Bake-off**: measure new boot time and compare.

## Deliverables
- Packer template repo with CI.
- Image catalog documented (name, layer, git SHA, CVEs).
- Boot time report before/after.

## Risks & mitigations
- Baked drift → weekly rebuilds and tag TTL.
- Test gaps → smoke-test every image before promotion.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Packer docs — building AMIs:
  (link removed)
- Packer docs — provisioners and post-processors:
  https://developer.hashicorp.com/packer/docs

## Definition of done
- Boot-to-healthy reduced ≥ 60%.
- Image promotion drill completed.
- No unversioned AMIs in asg launch templates.
