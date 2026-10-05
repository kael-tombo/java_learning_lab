# Mini Project — Packer Image Baking

## Goal
Build a golden image with Packer: install nginx + an app agent, run a
smoke test in a provisioner, and publish a tagged artifact.

## Steps
1. Install Packer; validate version.
2. Write `image.pkr.hcl`: source ubuntu AMI, builders, provisioners.
3. Provisioner: install nginx, write a version file, install app agent.
4. Post-processor: name `golden-app-<git-sha>`, tag with environment.
5. `packer validate` then `packer build`.
6. Launch an instance from the image; verify nginx serves and version
   file matches the build.
7. Rebuild with one added package; confirm new image only.

## Acceptance criteria
- Template validates and builds end-to-end.
- Image launches a working instance.
- Version metadata baked and visible.

## Stretch goals
- Add a pre-bake smoke test with `packer build` failing on error.
- Scan the image with a CIS benchmark tool.

## Estimated time
60–75 minutes (build time dominates).
