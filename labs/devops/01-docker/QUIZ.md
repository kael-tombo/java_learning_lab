# Docker Quiz

Test your Docker fundamentals. Try each question before checking the answers.

## Questions

1. What is the difference between a Docker image and a container?
2. How do Linux namespaces and cgroups each contribute to container isolation?
3. What is the difference between `CMD` and `ENTRYPOINT` in a Dockerfile?
4. When should you use `COPY` instead of `ADD` in a Dockerfile?
5. How do multi-stage builds reduce final image size?
6. What is the default Docker network driver, and when would you pick `bridge` vs `host` vs `overlay`?
7. How do you persist data beyond a container's lifetime?
8. What does `docker system prune` do, and what is the risk of running it with `-a --volumes`?
9. What are the OCI image and runtime specifications, and why do they matter?
10. How does Docker layer caching work, and what invalidates the cache?

## Answers

1. **Image vs container:** An image is a read-only, layered template (filesystem layers + config metadata). A container is a runnable instance of an image: it adds a thin writable layer plus an isolated process tree. Many containers can share one image.
2. **Namespaces vs cgroups:** Namespaces isolate *visibility* (PID, NET, MNT, UTS, IPC, USER — a container sees only its own processes, hostname, network interfaces). Cgroups limit and account *resources* (CPU shares, memory limits, I/O weight, pids). Isolation needs both.
3. **`CMD` vs `ENTRYPOINT`:** `ENTRYPOINT` sets the executable that always runs; `CMD` supplies default arguments (or a default command if no entrypoint). `docker run <img> <args>` overrides `CMD` but appends to `ENTRYPOINT` (unless `--entrypoint` is used). Pattern: `ENTRYPOINT ["python","app.py"]` + `CMD ["--port","5000"]`.
4. **`COPY` vs `ADD`:** Prefer `COPY` for plain file copies — it is transparent. `ADD` adds magic: auto-extracts local tarballs and can fetch remote URLs, which hurts reproducibility and cache clarity. Use `ADD` only when you explicitly want tar auto-extraction.
5. **Multi-stage builds:** Multiple `FROM` statements in one Dockerfile. Early stages contain SDKs/compilers to build artifacts; the final stage copies only the built artifacts into a minimal runtime image. Build tools never ship, so the image is smaller and has a reduced attack surface.
6. **Network drivers:** Default is `bridge` (single-host private network with NAT). Use `host` to remove network isolation for max performance (no port mapping, Linux only, port conflicts possible). Use `overlay` for multi-host Swarm networking. Also `macvlan` (container gets a LAN MAC/IP) and `none`.
7. **Persisting data:** Use volumes (`docker volume create`, `-v vol:/data`) for managed persistent storage, or bind mounts (`-v /host:/ctr`) for dev file sharing. Data in the container's writable layer is lost when the container is removed unless committed. Volumes also enable sharing between containers and backup.
8. **`docker system prune`:** Removes stopped containers, unused networks, dangling images (and with `-a`, all images not used by a container; with `--volumes`, anonymous/named unused volumes). Risk: deletes cached images (slow rebuilds) and volume data (possible data loss). Never run blindly on a build host holding release caches.
9. **OCI specs:** Open Container Initiative defines `image-spec` (layout of layers, manifest, config) and `runtime-spec` (how a bundle is executed). They let images built by Docker run under containerd, CRI-O, Podman, etc. — portability across runtimes and registries.
10. **Layer caching:** Each Dockerfile instruction produces a content-addressed layer. On rebuild, Docker reuses cached layers while the instruction text *and* its build context files are unchanged; the first changed instruction invalidates that layer and all below. Order instructions from least- to most-frequently-changing, and combine `RUN` steps to reduce layers.
