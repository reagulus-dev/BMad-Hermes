# Helix Host Infra Prerequisite Pattern — 2026-05-14

## Context
During Helix foundation work, `HLX-1.4` needed local PostgreSQL/Redis runtime verification. The repo story originally treated missing Docker/`psql`/`redis-cli` as environment-blocked. The user chose a cleaner sequence: create a prerequisite infrastructure story before implementing the repo-level bootstrap story.

## Reusable Pattern
When a repo-level story needs host tools installed:
1. Keep the repo story scoped to repo artifacts and runtime validation.
2. Create a prerequisite infra story for host package installation.
3. Update sprint/status so the repo story is `blocked_by_prerequisite` until host tools verify.
4. In the infra story, record host facts and tool availability before install.
5. Require non-interactive sudo preflight before package mutation:
   ```bash
   sudo -n true
   ```
6. If sudo requires a password, stop immediately and mark the infra story `blocked_on_sudo`; do not start interactive prompts or run partial install commands.
7. Record exact evidence and manual unblock commands in the story and continuation doc.

## Example Preflight Evidence
```bash
os=Ubuntu 24.04.4 LTS
user=reagulus
sudo_noninteractive=no
docker=not_found
psql=not_found
redis-cli=not_found
apt=present
```

## Blocked Evidence Example
```bash
sudo_preflight=failed
sudo: a password is required
docker=not_found
docker_compose=not_found
psql=not_found
redis-cli=not_found
BLOCKED: passwordless sudo unavailable; not attempting apt-get install.
```

## Status Semantics
- Infra story: `blocked_on_sudo` when passwordless sudo is unavailable.
- Dependent repo story: `blocked_by_prerequisite` with `blocked_by: <infra_story_id>`.
- Global BMad state: `workflow_status: blocked` until host tools are installed or the user provides an interactive sudo/unblock path.

## Pitfall
Do not fold host-level OS package installs into a normal repo implementation story. It changes the risk class, requires explicit authority, and needs separate evidence from TypeScript/build validation.
