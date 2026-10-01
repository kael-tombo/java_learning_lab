# Docker Flashcards

Quick-recall cards. Cover the answer, say it aloud, then check.

**Q: What is a Docker container?**
A: A running instance of an image — an isolated process tree with its own filesystem view (namespaces) and resource limits (cgroups), plus a thin writable layer.

**Q: What is a Docker image?**
A: A read-only template of stacked filesystem layers plus JSON config (entrypoint, env, exposed ports). Content-addressed and shareable via registries.

**Q: What is a Dockerfile?**
A: A text recipe of instructions (`FROM`, `RUN`, `COPY`, `CMD`...) that builds an image deterministically.

**Q: `COPY` vs `ADD`?**
A: `COPY` = plain file copy (preferred). `ADD` = copy + tar auto-extract + URL fetch (use only for tar extraction).

**Q: `CMD` vs `ENTRYPOINT`?**
A: ENTRYPOINT = the executable; CMD = default args. `docker run` args replace CMD but append to ENTRYPOINT.

**Q: What is a multi-stage build?**
A: Multiple `FROM` blocks in one Dockerfile: build artifacts in a heavy SDK stage, copy only artifacts into a slim runtime stage.

**Q: How does layer caching work?**
A: Each instruction's output is cached by hash; a changed instruction (or changed context files) invalidates that layer and everything after it.

**Q: What is copy-on-write?**
A: Image layers are read-only; a container's file modification copies that file up into the thin writable layer, leaving the image untouched.

**Q: What is a Docker volume?**
A: Managed persistent storage outside the container lifecycle (`docker volume create`, `-v name:/path`). Survives container removal; shared between containers.

**Q: Bind mount vs volume vs tmpfs?**
A: Volume = Docker-managed persistent disk. Bind mount = host path mapped in (dev loops). tmpfs = RAM-only (secrets, temp, never persisted).

**Q: Default network driver?**
A: `bridge` — single-host private subnet with NAT and port mapping (`-p host:ctr`).

**Q: `bridge` vs `host` vs `overlay`?**
A: bridge = isolated single-host; host = shares host stack (fastest, no isolation); overlay = multi-host Swarm network.

**Q: What is containerd?**
A: OCI-compliant daemon that pulls images and manages container execution; Docker Engine sits on top of it.

**Q: What is the OCI spec?**
A: Open Container Initiative standard for image layout and runtime behavior — what makes images portable across Docker, Podman, CRI-O.

**Q: What does `docker system prune -a --volumes` delete?**
A: Stopped containers, unused networks, all unreferenced images, and unused volumes — frees disk but destroys caches and possibly data.

**Q: What is `.dockerignore` and why does it matter?**
A: Exclusion list for the build context. Keeps secrets out of the image, shrinks context upload, and prevents spurious cache invalidation.

**Q: How do you run multi-container apps?**
A: `docker-compose.yml` (or `docker compose`): declares services, networks, volumes in YAML; one command brings up the whole stack.

**Q: How do you keep images small and secure?**
A: Minimal base (alpine/distroless), combine `RUN`, `--no-cache` installs, multi-stage, non-root `USER`, scan with `docker scout`/Trivy.
