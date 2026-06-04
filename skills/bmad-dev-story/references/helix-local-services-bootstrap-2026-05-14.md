# Helix Local Services Bootstrap — 2026-05-14

Context: Helix HLX-1.4 implemented local PostgreSQL/Redis bootstrap after HLX-INFRA-1 installed host prerequisites.

Reusable lessons for BMad dev-story validation:

- Keep host prerequisite installation separate from repo bootstrap when Docker/psql/redis-cli may be missing or require sudo.
- After a user is added to the `docker` group, the long-running controller process may still have stale groups. Verify with both `getent group docker` / `id <user>` and a real Docker command.
- If `groups` in the parent process is stale but `id <user>` shows membership, run Docker validation through a refreshed group shell, e.g. `sg docker -c 'docker info --format {{.ServerVersion}}'` and `sg docker -c 'docker compose ... up -d'`.
- For local PostgreSQL/Redis bootstrap stories, validate more than static files:
  - dependency install after manifest edits
  - recursive typecheck/test/build
  - Docker Compose up using the repo `.env.example`
  - structured PostgreSQL health (`SELECT 1`)
  - structured Redis health (`PING`)
  - migration runner against the live local database
  - direct table existence/schema verification for expected tables
- If the repo is not a git repository, state explicitly that git diff/status evidence is unavailable; do not invent diff evidence.
- Do not claim UI/runtime behavior unrelated to the local-services slice. For HLX-1.4, Electron UI, worker orchestration, live retailer adapter behavior, checkout/final-submit, 3DS, SCA, and OTP behavior stayed unclaimed.

Example evidence commands:

```bash
getent group docker
id "$USER"
sg docker -c 'docker info --format {{.ServerVersion}}'
sg docker -c 'docker run --rm hello-world'
sg docker -c 'docker compose --env-file config/.env.example -f config/docker-compose.yml up -d'
pnpm services:health
pnpm db:migrate
```
