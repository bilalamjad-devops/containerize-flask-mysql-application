# Stage 1: Manual Deployment → Docker Migration

> This is Stage 1 of a 5-stage migration series:
> **Stage 1 (this repo): Dockerfile** → Stage 2: docker-compose → Stage 3: Kubernetes → Stage 4: CI/CD → Stage 5: GitOps (ArgoCD)

## Problem

The Flask + MySQL app ran directly on a developer's machine or a manually
configured server. Every new environment (a teammate's laptop, a staging
server) required repeating the same manual setup: install Python, install
MySQL, install exact package versions, hope nothing drifted from what
originally worked.

## Solution

Package the Flask application itself into a Docker image, so "it works on my
machine" becomes "it works in this container," anywhere Docker runs.

**Scope of this stage on purpose:** only the app is containerized here.
MySQL still runs separately (locally installed, or in its own container you
start manually). Multi-container orchestration is Stage 2's job, not this
one — keeping each stage to a single new concept.

## Run it locally

1. Have a MySQL server available (local install, or run one manually):
   ```bash
   docker run -d --name mysql-dev -e MYSQL_ROOT_PASSWORD=changeme -e MYSQL_DATABASE=web_db -p 3306:3306 mysql:8.4
   ```

2. Copy the env template:
   ```bash
   cp .env.example .env
   ```
   Edit `DB_HOST` if MySQL isn't on `127.0.0.1` from the app container's
   point of view (see note below).

3. Build the image:
   ```bash
   docker build -t flask-mysql-demo .
   ```

4. Run the app container:
   ```bash
   docker run -p 5000:5000 --env-file .env flask-mysql-demo
   ```

5. Visit `http://localhost:5000`.

### Note on networking

A container's `127.0.0.1` refers to itself, not your host machine or other
containers. If MySQL is running as a separate container (as in step 1
above), set `DB_HOST` to that container's name (`mysql-dev`) and run both
containers on the same Docker network:

```bash
docker network create demo-net
docker run -d --name mysql-dev --network demo-net -e MYSQL_ROOT_PASSWORD=changeme -e MYSQL_DATABASE=web_db mysql:8.4
docker run -p 5000:5000 --network demo-net --env-file .env flask-mysql-demo
```

This exact "two containers need to find each other" friction is precisely
the problem Stage 2 (docker-compose) solves properly.

## What's deliberately NOT here yet

- No docker-compose (Stage 2)
- No Kubernetes (Stage 3)
- No CI/CD (Stage 4)
- No GitOps (Stage 5)

## Lessons Learned

- Flask's built-in dev server (`app.run(...)`) is fine here since this stage
  is about proving containerization works, not production-hardening yet —
  that's addressed in a later stage.
- `DB_NAME` is validated as a safe identifier before being interpolated into
  SQL, since MySQL doesn't support parameterized table/database names.
