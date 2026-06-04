# Scaffold / Monorepo Foundation Review Notes

Use this reference when reviewing a foundation story that creates a new repo, package workspace, app shell scaffold, or local-service module layout before meaningful runtime behavior exists.

## Review Trigger

A story is scaffold/foundation-shaped when it primarily creates or normalizes:
- root package manager config (`package.json`, `pnpm-workspace.yaml`, lockfile)
- TypeScript base config and child `tsconfig.json` files
- app/package directory structure
- placeholder exports and smoke tests
- ignore rules and README setup commands
- BMad state/sprint/story artifacts for the new project

## Review Checks

1. Workspace config hygiene
   - Ensure package-manager config is valid and minimal.
   - For pnpm/Corepack projects, run `corepack pnpm --version` (or the project’s declared pnpm invocation) before relying on local `node_modules/.bin/*` fallbacks. If `package.json` pins `pnpm@<version>+sha512.<hash>` and Corepack reports a hash mismatch, treat it as a scaffold blocker: the committed package-manager contract is broken for fresh clones even if locally installed binaries can lint/typecheck/test/build.
   - For pnpm, remove stale interactive approval placeholders such as `allowBuilds: esbuild: set this to true or false`.
   - If build-script approvals are intentionally recorded, prefer a clean explicit form such as `onlyBuiltDependencies: ['esbuild']`.

2. Root scripts vs child scripts
   - If root scripts call recursive commands such as `pnpm -r run build`, every intended child workspace must define that script.
   - Run install, typecheck, test, and build from the root after any manifest correction.

3. Manifest/package-boundary audit
   - Count expected app and package workspaces.
   - Verify each child has `package.json`, `tsconfig.json`, `src/index.ts`, and `src/index.test.ts` or the project’s equivalent minimum.
   - Verify package names are unique and follow the namespace convention.

4. Ignore-file future compatibility
   - Do not ignore future source/config files that later stories are expected to commit.
   - Example: if a later local Postgres/Redis story will add `docker-compose.yml` or `docker/`, the scaffold story should not globally ignore those paths.
   - Keep generated/runtime material ignored instead, such as `node_modules/`, `dist/`, profiles, screenshots, traces, and local secrets.

5. Scope containment
   - Verify the scaffold did not sneak in runtime/product behavior outside the story.
   - For automation products, explicitly check that no live vendor adapter, checkout/final-submit flow, account/payment capture, OTP/3DS/SCA handling, or browser-worker runtime claim was added unless that is the story.

6. No-secrets sweep
   - Grep source/config/docs for secret-like terms.
   - Classify hygiene/docs mentions separately from real secrets; do not fail solely on `.gitignore` secret patterns or README prose, but call it `PASS WITH NOTES` if matches exist.

7. Runtime claim discipline
   - For scaffold-only work, runtime/UI verification can be `not applicable`.
   - Say exactly what was validated instead: installability, typecheck, tests, build, package boundaries, lockfile presence, and secret hygiene.
   - Do not call it QA/founder-review ready just because static gates passed.

## Example Validation Bundle

```bash
pnpm install --ignore-scripts
pnpm -r run typecheck
pnpm -r run test
pnpm -r run build
python3 scripts-or-inline-workspace-audit.py

grep -R -I -n -i -E '(password|secret|api[_-]?key|token|credential|cookie|bearer|private[ _-]?key|webhook)' . \
  --include='*.ts' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.md' --include='*.gitignore' \
  --exclude='pnpm-lock.yaml' --exclude-dir=node_modules --exclude-dir=.pnpm --exclude-dir=_bmad --exclude-dir=docs --exclude='CONTINUE-HERE.md'
```

## Reporting Pattern

- Verdict: usually `PASS WITH NOTES` when static evidence is complete but no runtime exists yet.
- Findings should distinguish review-time corrections from remaining risks.
- State should advance to the next story only after the review artifact and sprint/current state agree.
- Required next action should be a concrete next story, often `bmad-create-story` then `bmad-dev-story` for the next foundation contract.
