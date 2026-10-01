# Docker Exercises

Hands-on infra tasks. Each has a goal, steps, and a done-check. You need only Docker Engine + Compose.

## Exercise 1: Hello Docker + Inspection

**Goal:** Run your first container and distinguish image vs container.
**Steps:**
1. `docker run hello-world` — read the output.
2. `docker images` and `docker ps -a` — identify the image vs the stopped container.
3. `docker inspect hello-world | head -50`.
**Done when:** You can explain which line in `ps -a` is the container and which line in `images` is the image.

## Exercise 2: Interactive Container + Filesystem Deltas

**Goal:** Feel the writable layer.
**Steps:**
1. `docker run -it ubuntu:22.04 bash`; inside: `apt-get update && apt-get install -y curl && curl -sI https://example.com | head -3`.
2. In another terminal: `docker diff <container>` while the first shell is still open.
3. Exit, then `docker commit <container> my-ubuntu:curl && docker images`.
**Done when:** `docker diff` shows added files and `my-ubuntu:curl` appears in `images`.

## Exercise 3: Build and Run a Flask App

**Goal:** Author a real Dockerfile.
**Steps:**
1. Create `app.py` (Flask "hello from docker" on port 5000), `requirements.txt`, and this Dockerfile:
   `FROM python:3.12-slim / WORKDIR /app / COPY requirements.txt . / RUN pip install --no-cache-dir -r requirements.txt / COPY . . / EXPOSE 5000 / CMD ["python","app.py"]`.
2. `docker build -t flask-demo:1.0 . && docker run -d -p 5000:5000 --name web flask-demo:1.0`.
3. `curl localhost:5000`; `docker logs web`.
**Done when:** HTTP 200 from the container and `logs` shows the Flask startup line.

## Exercise 4: Compose a Postgres + Adminer + App Stack

**Goal:** Run a multi-container pipeline dependency.
**Steps:**
1. Write `docker-compose.yml` with services: `db` (postgres:15, env POSTGRES_PASSWORD, volume `pgdata:/var/lib/postgresql/data`, port 5432), `adminer` (port 8080), `app` (build from Ex 3, `depends_on: [db]`, env `DATABASE_URL`).
2. `docker compose up -d && docker compose ps`.
3. Open Adminer at localhost:8080, log into Postgres; insert one row from the app container.
**Done when:** `compose ps` shows 3 healthy services and you can query the inserted row via Adminer.

## Exercise 5: Multi-Stage Build (Slim the Image)

**Goal:** Cut image size and attack surface.
**Steps:**
1. Rewrite the Flask Dockerfile with two stages: `FROM python:3.12 AS build` (install deps to `/install` with `pip install --prefix=/install`), then `FROM python:3.12-slim` (`COPY --from=build /install /usr/local`, `COPY app.py .`, non-root `USER app`).
2. Build both variants; compare `docker images flask-demo flask-slim`.
3. `docker run --rm flask-slim` smoke test.
**Done when:** Slim variant is ≥40% smaller and still serves HTTP 200.

## Exercise 6: Optimize a Bloated Dockerfile

**Goal:** Practice layer-cache discipline.
**Given (bloated):** `FROM ubuntu` + separate `RUN apt-get update`, `RUN apt-get install -y python3`, `ADD . /app` first, no `.dockerignore`, runs as root.
**Steps:**
1. Switch to `python:3.12-slim`, combine `RUN apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*`.
2. Add `.dockerignore` (`.git`, `__pycache__`, `*.pyc`, `.env`), move `COPY` after dependency install, add `USER app`.
3. Time two consecutive builds to prove caching: `time docker build -t opt .` twice with no changes.
**Done when:** Second build finishes in seconds (cache hits) and `docker history opt` shows fewer, slimmer layers.

## Exercise 7: Break It, Then Debug It

**Goal:** Build debugging muscle.
**Steps:**
1. Deliberately break the build: wrong base tag, bad `COPY` path, port mismatch (`EXPOSE 5000` but app listens on 8000).
2. Diagnose with: build log output, `docker run --rm -it <img> sh`, `docker logs <ctr>`, `docker inspect <ctr>`.
3. Fix all three and document each root cause in one sentence.
**Done when:** Container serves traffic again and you have three one-line postmortems.

## Exercise 8 (Stretch): Scan and Harden

**Goal:** Ship a production-minded image.
**Steps:**
1. Scan with `docker scout cves flask-slim` (or Trivy).
2. Fix: pin base digest, drop to non-root, remove shell if distroless is viable.
3. Re-scan and record remaining CVEs with a one-line justification each.
**Done when:** Re-scan shows fewer HIGH/CRITICAL findings and the app still passes the Ex 3 smoke test.
