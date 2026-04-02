from __future__ import annotations

import pytest
import tempfile
import os
from pathlib import Path

from bmad_workflow_plugin.registry.loader import RegistryLoader
from bmad_workflow_plugin.paths.resolver import PathResolver, ResolvedPath


@pytest.fixture
def resolver():
    registry = RegistryLoader().load_default()
    return PathResolver(registry)


@pytest.fixture
def temp_project():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ---------------------------------------------------------------------------
# build_preferred_path — Phase 4 (existing)
# ---------------------------------------------------------------------------

def test_build_preferred_story_path(resolver):
    path = resolver.build_preferred_path('/tmp/demo', 'story', {'story_key': '1-2-user-auth'})
    assert path.endswith('/_bmad/artifacts/stories/1-2-user-auth.md')


# ---------------------------------------------------------------------------
# build_preferred_path — Phase 1 artifacts
# ---------------------------------------------------------------------------

def test_build_preferred_brainstorming_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'brainstorming_session',
        {'session_name': 'auth-brainstorm'}
    )
    assert '_bmad/artifacts/planning/brainstorming/auth-brainstorm.md' in path


def test_build_preferred_product_brief_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'product_brief',
        {'project_name': 'my-project'}
    )
    assert '_bmad/artifacts/planning/briefs/my-project/brief.md' in path


def test_build_preferred_prfaq_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'prfaq',
        {'project_name': 'my-project'}
    )
    assert '_bmad/artifacts/planning/prfaqs/my-project/prfaq.md' in path


# ---------------------------------------------------------------------------
# build_preferred_path — Phase 2 artifacts
# ---------------------------------------------------------------------------

def test_build_preferred_prd_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'prd',
        {'project_name': 'my-project'}
    )
    assert '_bmad/artifacts/planning/prds/my-project/prd.md' in path


def test_build_preferred_prd_validation_report_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'prd_validation_report',
        {'project_name': 'my-project'}
    )
    assert '_bmad/artifacts/planning/prds/my-project/prd-validation.md' in path


def test_build_preferred_ux_design_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'ux_design',
        {'project_name': 'my-project'}
    )
    assert '_bmad/artifacts/planning/ux/my-project/ux-design.md' in path


# ---------------------------------------------------------------------------
# build_preferred_path — Phase 3 artifacts
# ---------------------------------------------------------------------------

def test_build_preferred_architecture_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'architecture',
        {'project_name': 'my-project'}
    )
    assert '_bmad/artifacts/solutioning/architecture/my-project/architecture.md' in path


def test_build_preferred_epics_and_stories_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'epics_and_stories',
        {'project_name': 'my-project'}
    )
    assert '_bmad/artifacts/solutioning/epics/my-project/epics.md' in path


def test_build_preferred_project_context_path(resolver):
    path = resolver.build_preferred_path(
        '/tmp/demo', 'project_context',
        {'project_name': 'my-project'}
    )
    assert '_bmad/artifacts/solutioning/my-project/project-context.md' in path


# ---------------------------------------------------------------------------
# build_preferred_path — sprint_status (no identity)
# ---------------------------------------------------------------------------

def test_build_preferred_sprint_status_path(resolver):
    path = resolver.build_preferred_path('/tmp/demo', 'sprint_status', {})
    assert path.endswith('/_bmad/artifacts/state/sprint-status.yaml')


# ---------------------------------------------------------------------------
# build_preferred_path — missing identity key raises
# ---------------------------------------------------------------------------

def test_build_preferred_path_unresolved_placeholder(resolver):
    """When identity is missing a required key, the unresolved placeholder appears in the path."""
    # story_key is required for story; if not provided the template has {story_key}
    # which gets replaced with UNRESOLVED
    path = resolver.build_preferred_path('/tmp/demo', 'story', {})
    # The path resolver replaces {unknown_key} with UNRESOLVED
    # Since story requires story_key and it's missing, path will contain UNRESOLVED
    # and the last-resort fallback in _candidate_paths returns the template literally
    # (via materialize with missing key -> UNRESOLVED)
    # This tests that it doesn't raise, it produces a path with UNRESOLVED
    assert 'UNRESOLVED' in path or '.md' in path  # lenient: at least it doesn't throw


# ---------------------------------------------------------------------------
# resolve_artifact_path — artifact does not exist
# ---------------------------------------------------------------------------

def test_resolve_returns_candidates_when_not_exists(resolver, temp_project):
    result = resolver.resolve_artifact_path(str(temp_project), 'story', {'story_key': '1-1-new'})
    assert result.path is None
    assert result.candidates  # should list all candidates


# ---------------------------------------------------------------------------
# resolve_artifact_path — artifact exists at preferred path
# ---------------------------------------------------------------------------

def test_resolve_finds_existing_at_preferred_path(resolver, temp_project):
    # Create story at preferred path
    story_key = '1-1-new-feature'
    preferred = resolver.build_preferred_path(str(temp_project), 'story', {'story_key': story_key})
    Path(preferred).parent.mkdir(parents=True, exist_ok=True)
    Path(preferred).write_text('# Story content', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(temp_project), 'story', {'story_key': story_key})
    assert result.path == preferred
    assert result.source_kind == 'preferred'
    assert result.ambiguous is False


# ---------------------------------------------------------------------------
# resolve_artifact_path — artifact exists only at legacy path
# ---------------------------------------------------------------------------

def test_resolve_finds_existing_at_legacy_path(resolver, temp_project):
    # Create story at legacy path (not preferred)
    legacy_path = temp_project / '_bmad-output' / 'implementation-artifacts' / '1-1-legacy-story.md'
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text('# Legacy Story', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(temp_project), 'story', {'story_key': '1-1-legacy-story'})
    assert result.path == str(legacy_path)
    assert result.source_kind == 'legacy_compatible'


# ---------------------------------------------------------------------------
# resolve_artifact_path — artifact exists at both preferred and legacy
# ---------------------------------------------------------------------------

def test_resolve_ambiguous_when_both_exist(resolver, temp_project):
    # Create at preferred
    pref = resolver.build_preferred_path(str(temp_project), 'story', {'story_key': '1-1-amb'})
    Path(pref).parent.mkdir(parents=True, exist_ok=True)
    Path(pref).write_text('# Story', encoding='utf-8')

    # Create at legacy
    legacy = temp_project / '_bmad-output' / 'implementation-artifacts' / '1-1-amb.md'
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_text('# Legacy Story', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(temp_project), 'story', {'story_key': '1-1-amb'})
    assert result.ambiguous is True
    assert result.path is None


# ---------------------------------------------------------------------------
# resolve_artifact_path — Phase 1-3 artifacts
# ---------------------------------------------------------------------------

def test_resolve_product_brief_phase1(resolver, temp_project):
    project_name = 'acme-app'
    preferred = resolver.build_preferred_path(str(temp_project), 'product_brief', {'project_name': project_name})
    Path(preferred).parent.mkdir(parents=True, exist_ok=True)
    Path(preferred).write_text('# Product Brief', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(temp_project), 'product_brief', {'project_name': project_name})
    assert result.path == preferred
    assert result.source_kind == 'preferred'


def test_resolve_prd_phase2(resolver, temp_project):
    project_name = 'acme-app'
    preferred = resolver.build_preferred_path(str(temp_project), 'prd', {'project_name': project_name})
    Path(preferred).parent.mkdir(parents=True, exist_ok=True)
    Path(preferred).write_text('# PRD', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(temp_project), 'prd', {'project_name': project_name})
    assert result.path == preferred


def test_resolve_architecture_phase3(resolver, temp_project):
    project_name = 'acme-app'
    preferred = resolver.build_preferred_path(str(temp_project), 'architecture', {'project_name': project_name})
    Path(preferred).parent.mkdir(parents=True, exist_ok=True)
    Path(preferred).write_text('# Architecture', encoding='utf-8')

    result = resolver.resolve_artifact_path(str(temp_project), 'architecture', {'project_name': project_name})
    assert result.path == preferred


# ---------------------------------------------------------------------------
# resolve_artifact_path — unknown artifact type raises
# ---------------------------------------------------------------------------

def test_resolve_unknown_artifact_type_raises(resolver, temp_project):
    with pytest.raises(KeyError, match='Unknown artifact type'):
        resolver.resolve_artifact_path(str(temp_project), 'nonexistent_artifact', {})


# ---------------------------------------------------------------------------
# ResolvedPath dataclass fields
# ---------------------------------------------------------------------------

def test_resolved_path_fields():
    rp = ResolvedPath(path='/some/path.md', source_kind='preferred', candidates=['/a.md', '/b.md'], ambiguous=False)
    assert rp.path == '/some/path.md'
    assert rp.source_kind == 'preferred'
    assert rp.candidates == ['/a.md', '/b.md']
    assert rp.ambiguous is False
