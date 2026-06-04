#!/usr/bin/env python3
"""
validate_bmad_artifacts.py — run after any story selection or epic handoff edit.

Verifies internal consistency across the four canonical BMad artifact files:

  _bmad/state.json
  _bmad/sprint-status.yaml
  _bmad/artifacts/planning/epics_and_stories.md
  _bmad/artifacts/stories/<current_story>.md  (resolved from state.json)
  CONTINUE-HERE.md

Cross-checks that the agent's narrative (CONTINUE-HERE.md) and the live state
(state.json) and the sprint YAML and the planning doc all agree on:

  - current_epic
  - current_story
  - current_sprint
  - workflow_status
  - next_recommended_workflow

Exits non-zero with a printed report if any drift is found. This is a
deterministic probe — re-run after every story-selection handoff edit, before
any commit, and as the first step of any state-check workflow.

Usage:
  python3 validate_bmad_artifacts.py [project_root]

If project_root is omitted, the current working directory is used.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "PyYAML is required. Install with: pip install pyyaml\n"
    )
    sys.exit(2)


def fail(messages: list[str], prefix: str = "") -> int:
    for m in messages:
        print(f"{prefix}{m}")
    return 1


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).resolve()
    bmad = root / "_bmad"
    if not bmad.is_dir():
        print(f"_bmad/ not found at {bmad}")
        return 1

    state_path = bmad / "state.json"
    sprint_path = bmad / "sprint-status.yaml"
    planning_path = bmad / "artifacts" / "planning" / "epics_and_stories.md"
    cont_path = root / "CONTINUE-HERE.md"

    errors: list[str] = []

    # 1. JSON parses
    try:
        state = json.loads(state_path.read_text())
    except Exception as e:
        print(f"state.json: failed to parse JSON: {e}")
        return 1

    try:
        sprint = yaml.safe_load(sprint_path.read_text())
    except Exception as e:
        print(f"sprint-status.yaml: failed to parse YAML: {e}")
        return 1

    current_epic = state.get("current_epic")
    current_story = state.get("current_story")
    current_sprint = state.get("current_sprint")
    workflow_status = state.get("workflow_status")
    next_workflows = state.get("next_recommended_workflows", [])
    active_artifact = state.get("active_story_artifact")

    # 2. Sprint YAML top-level matches state.json
    if sprint.get("current_epic") != current_epic:
        errors.append(
            f"current_epic drift: state.json={current_epic!r} "
            f"sprint={sprint.get('current_epic')!r}"
        )
    if sprint.get("current_story") != current_story:
        errors.append(
            f"current_story drift: state.json={current_story!r} "
            f"sprint={sprint.get('current_story')!r}"
        )
    if current_sprint and sprint.get("current_sprint") != current_sprint:
        errors.append(
            f"current_sprint drift: state.json={current_sprint!r} "
            f"sprint={sprint.get('current_sprint')!r}"
        )

    # 3. The current_story exists in sprint-status.yaml's epics[] and is not
    #    marked deferred/blocked/completed.
    found = None
    for epic in sprint.get("epics", []) or []:
        for s in epic.get("stories", []) or []:
            if s.get("id") == current_story:
                found = (epic, s)
                break
        if found:
            break
    if not found:
        errors.append(
            f"current_story {current_story!r} not found in sprint-status.yaml "
            f"epics[].stories[]"
        )
    else:
        epic, story = found
        if story.get("status") in {"deferred", "blocked", "completed"}:
            errors.append(
                f"current_story {current_story!r} has status {story.get('status')!r} "
                f"in sprint-status.yaml; that contradicts workflow_status "
                f"{workflow_status!r} in state.json"
            )
        # 4. Epic status consistency
        if epic.get("id") == current_epic:
            if epic.get("status") not in {"in_progress"}:
                errors.append(
                    f"current_epic {current_epic!r} has status "
                    f"{epic.get('status')!r}; expected in_progress while "
                    f"current_story is active"
                )

    # 5. active_story_artifact file exists
    if active_artifact:
        artifact_path = root / active_artifact
        if not artifact_path.is_file():
            errors.append(
                f"active_story_artifact path does not exist on disk: "
                f"{active_artifact}"
            )
        else:
            text = artifact_path.read_text()
            m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
            if not m:
                errors.append(
                    f"active_story_artifact has no YAML frontmatter: "
                    f"{active_artifact}"
                )
            else:
                try:
                    fm = yaml.safe_load(m.group(1))
                except Exception as e:
                    errors.append(
                        f"active_story_artifact frontmatter failed YAML parse: "
                        f"{e}"
                    )
                    fm = {}
                if fm.get("story_id") and fm.get("story_id") != current_story:
                    errors.append(
                        f"active_story_artifact frontmatter story_id "
                        f"{fm.get('story_id')!r} != state.json current_story "
                        f"{current_story!r}"
                    )
                if fm.get("epic") and fm.get("epic") != current_epic:
                    errors.append(
                        f"active_story_artifact frontmatter epic "
                        f"{fm.get('epic')!r} != state.json current_epic "
                        f"{current_epic!r}"
                    )

    # 6. next_recommended_workflows mentions the current story if workflow_status
    #    is story_created / in_progress.
    if workflow_status in {"story_created", "in_progress"}:
        if not any(current_story in (w or "") for w in next_workflows):
            errors.append(
                f"next_recommended_workflows does not mention current_story "
                f"{current_story!r}: {next_workflows}"
            )

    # 7. CONTINUE-HERE.md mentions the current story and epic
    if cont_path.is_file():
        cont = cont_path.read_text()
        if current_story and current_story not in cont:
            errors.append(
                f"CONTINUE-HERE.md does not mention current_story "
                f"{current_story!r}"
            )
        if current_epic and current_epic not in cont:
            errors.append(
                f"CONTINUE-HERE.md does not mention current_epic "
                f"{current_epic!r}"
            )
    else:
        errors.append("CONTINUE-HERE.md missing at repo root")

    # 8. Planning doc has the current story as a heading
    if planning_path.is_file():
        plan = planning_path.read_text()
        if current_story:
            heading_re = re.compile(rf"^###\s+{re.escape(current_story)}\b", re.MULTILINE)
            if not heading_re.search(plan):
                errors.append(
                    f"epics_and_stories.md has no `### {current_story}` heading"
                )

    # Report
    if errors:
        print("FAIL — BMad artifact consistency check found drift:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK — BMad artifacts are consistent.")
    print(f"  current_epic      = {current_epic}")
    print(f"  current_story     = {current_story}")
    print(f"  current_sprint    = {current_sprint}")
    print(f"  workflow_status   = {workflow_status}")
    print(f"  next_workflows    = {next_workflows}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
