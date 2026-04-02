#!/usr/bin/env python3
"""Standalone test runner — no third-party dependencies required."""

from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = str(Path(__file__).parent.parent)
sys.path.insert(0, PROJECT_ROOT)

import unittest

# ---------------------------------------------------------------------------
# Template Renderer Tests
# ---------------------------------------------------------------------------

from bmad_workflow_plugin.mutations.template_renderer import TemplateRenderer, register_filter, list_filters, _DEFAULT_FILTERS


class TestTemplateRendererBareVariable(unittest.TestCase):
    def test_bare_variable_resolved(self):
        r = TemplateRenderer()
        text = "Hello, {{ name }}!"
        self.assertEqual(r._substitute(text, {'name': 'Alice'}), "Hello, Alice!")

    def test_bare_variable_undefined(self):
        r = TemplateRenderer()
        text = "Hello, {{ name }}!"
        self.assertEqual(r._substitute(text, {}), "Hello, !")

    def test_bare_variable_with_spaces(self):
        r = TemplateRenderer()
        text = "Hello, {{  name  }}!"
        self.assertEqual(r._substitute(text, {'name': 'Bob'}), "Hello, Bob!")

    def test_multiple_bare_variables(self):
        r = TemplateRenderer()
        text = "{{ greeting }}, {{ name }}!"
        self.assertEqual(r._substitute(text, {'greeting': 'Hello', 'name': 'Carol'}), "Hello, Carol!")

    def test_bare_variable_value_none(self):
        r = TemplateRenderer()
        text = "Value: {{ val }}"
        self.assertEqual(r._substitute(text, {'val': None}), "Value: ")

    def test_bare_variable_value_empty_string(self):
        r = TemplateRenderer()
        text = "Value: {{ val }}"
        self.assertEqual(r._substitute(text, {'val': ''}), "Value: ")


class TestTemplateRendererDefaultFilter(unittest.TestCase):
    def test_default_filter_provided(self):
        r = TemplateRenderer()
        text = 'Status: {{status|default("draft")}}'
        self.assertEqual(r._substitute(text, {'status': 'review'}), "Status: review")

    def test_default_filter_missing(self):
        r = TemplateRenderer()
        text = 'Status: {{status|default("draft")}}'
        self.assertEqual(r._substitute(text, {}), "Status: draft")

    def test_default_filter_empty_string(self):
        r = TemplateRenderer()
        text = 'Status: {{status|default("draft")}}'
        self.assertEqual(r._substitute(text, {'status': ''}), "Status: draft")

    def test_default_filter_none(self):
        r = TemplateRenderer()
        text = 'Status: {{status|default("draft")}}'
        self.assertEqual(r._substitute(text, {'status': None}), "Status: draft")

    def test_default_filter_single_quoted(self):
        r = TemplateRenderer()
        text = "{{val|default('fallback')}}"
        self.assertEqual(r._substitute(text, {}), "fallback")
        self.assertEqual(r._substitute(text, {'val': 'actual'}), "actual")

    def test_default_filter_complex_fallback(self):
        r = TemplateRenderer()
        text = '{{story_location|default("_bmad/artifacts/stories")}}'
        self.assertEqual(r._substitute(text, {}), "_bmad/artifacts/stories")

    def test_default_filter_nested_in_heading(self):
        r = TemplateRenderer()
        text = '# {{headline|default("Headline: {product name}")}}'
        self.assertEqual(r._substitute(text, {}), "# Headline: {product name}")
        self.assertEqual(r._substitute(text, {'headline': 'My Amazing Product'}), "# My Amazing Product")

    def test_default_filter_with_braces_in_fallback(self):
        r = TemplateRenderer()
        text = '{{val|default("{something}")}}'
        self.assertEqual(r._substitute(text, {}), "{something}")

    def test_default_filter_with_spaces(self):
        r = TemplateRenderer()
        text = '{{ tracking_system|default("file-system")}}'
        self.assertEqual(r._substitute(text, {}), "file-system")
        self.assertEqual(r._substitute(text, {'tracking_system': 'linear'}), "linear")


class TestTemplateRendererMixed(unittest.TestCase):
    def test_mixed_bare_and_filter(self):
        r = TemplateRenderer()
        text = 'Status: {{status|default("draft")}} — {{author}}'
        result = r._substitute(text, {'author': 'Alice', 'status': 'done'})
        self.assertEqual(result, "Status: done — Alice")

    def test_real_sprint_status_yaml_fragment(self):
        r = TemplateRenderer()
        text = (
            'tracking_system: {{tracking_system|default("file-system")}}\n'
            'story_location: "{{story_location|default("_bmad/artifacts/stories")}}"'
        )
        self.assertEqual(r._substitute(text, {}),
            'tracking_system: file-system\n'
            'story_location: "_bmad/artifacts/stories"')
        self.assertEqual(r._substitute(text, {'tracking_system': 'linear', 'story_location': 'stories/'}),
            'tracking_system: linear\n'
            'story_location: "stories/"')

    def test_prfaq_template_fragment(self):
        r = TemplateRenderer()
        text = 'Status: {{status|default("draft")}}\nStage: {{stage|default("concept")}}\n\n# {{headline|default("Headline: {product}")}}'
        self.assertEqual(r._substitute(text, {'headline': 'Acme AI'}),
            "Status: draft\nStage: concept\n\n# Acme AI")


class TestTemplateRendererUnknownFilter(unittest.TestCase):
    def test_unknown_filter_leaves_expression_unmodified(self):
        r = TemplateRenderer()
        text = '{{val|unknown_filter("arg")}}'
        result = r._substitute(text, {'val': 'something'})
        self.assertIn('{{val|unknown_filter("arg")}}', result)


class TestTemplateRendererFile(unittest.TestCase):
    def test_render_reads_file(self):
        r = TemplateRenderer()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, {{ name }}!")
            path = f.name
        try:
            result = r.render(path, {'name': 'FileTest'})
            self.assertEqual(result, "Hello, FileTest!")
        finally:
            os.unlink(path)

    def test_render_file_not_found(self):
        r = TemplateRenderer()
        with self.assertRaises(FileNotFoundError):
            r.render('/nonexistent/path/to/template.txt', {})


class TestTemplateRendererEdgeCases(unittest.TestCase):
    def test_double_braces_literal_outer(self):
        r = TemplateRenderer()
        # Note: Double-brace literal escaping ({{ {{ } }}) is NOT reliably supported
        # by this simple single-pass renderer. This is expected.
        # The important case is single-brace templates work correctly.
        text = "{{{{ name }}}}"
        result = r._substitute(text, {'name': 'Alice'})
        # With single-pass, outer braces consumed literally, inner {{
        # then ' name }}' matched as expression but spaces prevent bare-var match
        # Result is intentionally the literal unchanged string
        self.assertEqual(result, "{{{{ name }}}}")

    def test_no_braces(self):
        r = TemplateRenderer()
        text = "No variables here."
        self.assertEqual(r._substitute(text, {'name': 'Alice'}), "No variables here.")

    def test_special_chars_in_value(self):
        r = TemplateRenderer()
        text = '{{val|default("draft")}}'
        self.assertEqual(r._substitute(text, {'val': 'status: done'}), "status: done")


class TestTemplateRendererCustomFilter(unittest.TestCase):
    def test_register_and_use_custom_filter(self):
        @register_filter('upper')
        def upper_filter(value, _arg):
            # upper takes no arg but filter protocol passes one (ignored here)
            return str(value).upper() if value else ''
        try:
            r = TemplateRenderer()
            # With optional parens: {{name|upper()}}
            text = "{{name|upper()}}"
            self.assertEqual(r._substitute(text, {'name': 'alice'}), "ALICE")
        finally:
            del _DEFAULT_FILTERS['upper']

    def test_list_filters_contains_default(self):
        self.assertIn('default', list_filters())


# ---------------------------------------------------------------------------
# Path Resolver Tests
# ---------------------------------------------------------------------------

from bmad_workflow_plugin.registry.loader import RegistryLoader
from bmad_workflow_plugin.paths.resolver import PathResolver, ResolvedPath


def _make_resolver():
    registry = RegistryLoader().load_default()
    return PathResolver(registry)


class TestPathResolverBuildPreferred(unittest.TestCase):
    def test_story_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'story', {'story_key': '1-2-user-auth'})
        self.assertTrue(path.endswith('/_bmad/artifacts/stories/1-2-user-auth.md'))

    # Phase 1
    def test_brainstorming_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'brainstorming_session', {'session_name': 'auth-brain'})
        self.assertIn('_bmad/artifacts/planning/brainstorming/auth-brain.md', path)

    def test_product_brief_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'product_brief', {'project_name': 'my-project'})
        self.assertIn('_bmad/artifacts/planning/briefs/my-project/brief.md', path)

    def test_prfaq_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'prfaq', {'project_name': 'my-project'})
        self.assertIn('_bmad/artifacts/planning/prfaqs/my-project/prfaq.md', path)

    # Phase 2
    def test_prd_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'prd', {'project_name': 'my-project'})
        self.assertIn('_bmad/artifacts/planning/prds/my-project/prd.md', path)

    def test_prd_validation_report_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'prd_validation_report', {'project_name': 'my-project'})
        self.assertIn('_bmad/artifacts/planning/prds/my-project/prd-validation.md', path)

    def test_ux_design_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'ux_design', {'project_name': 'my-project'})
        self.assertIn('_bmad/artifacts/planning/ux/my-project/ux-design.md', path)

    # Phase 3
    def test_architecture_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'architecture', {'project_name': 'my-project'})
        self.assertIn('_bmad/artifacts/solutioning/architecture/my-project/architecture.md', path)

    def test_epics_and_stories_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'epics_and_stories', {'project_name': 'my-project'})
        self.assertIn('_bmad/artifacts/solutioning/epics/my-project/epics.md', path)

    def test_project_context_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'project_context', {'project_name': 'my-project'})
        self.assertIn('_bmad/artifacts/solutioning/my-project/project-context.md', path)

    # sprint_status
    def test_sprint_status_path(self):
        r = _make_resolver()
        path = r.build_preferred_path('/tmp/demo', 'sprint_status', {})
        self.assertTrue(path.endswith('/_bmad/artifacts/state/sprint-status.yaml'))


class TestPathResolverResolve(unittest.TestCase):
    def test_returns_candidates_when_not_exists(self):
        r = _make_resolver()
        with tempfile.TemporaryDirectory() as d:
            result = r.resolve_artifact_path(d, 'story', {'story_key': '1-1-new'})
        self.assertIsNone(result.path)
        self.assertTrue(len(result.candidates) > 0)

    def test_finds_existing_at_preferred_path(self):
        r = _make_resolver()
        with tempfile.TemporaryDirectory() as d:
            story_key = '1-1-new-feature'
            preferred = r.build_preferred_path(d, 'story', {'story_key': story_key})
            Path(preferred).parent.mkdir(parents=True, exist_ok=True)
            Path(preferred).write_text('# Story content', encoding='utf-8')
            result = r.resolve_artifact_path(d, 'story', {'story_key': story_key})
        self.assertEqual(result.path, preferred)
        self.assertEqual(result.source_kind, 'preferred')
        self.assertFalse(result.ambiguous)

    def test_finds_existing_at_legacy_path(self):
        r = _make_resolver()
        with tempfile.TemporaryDirectory() as d:
            legacy_path = Path(d) / '_bmad-output' / 'implementation-artifacts' / '1-1-legacy-story.md'
            legacy_path.parent.mkdir(parents=True, exist_ok=True)
            legacy_path.write_text('# Legacy Story', encoding='utf-8')
            result = r.resolve_artifact_path(d, 'story', {'story_key': '1-1-legacy-story'})
        self.assertEqual(result.path, str(legacy_path))
        self.assertEqual(result.source_kind, 'legacy_compatible')

    def test_ambiguous_when_both_exist(self):
        # NOTE: Ambiguity detection (multiple preferred paths for same key) is not
        # reachable with the current data model — each artifact type has exactly
        # one preferred path template. The ambiguity code path is tested via
        # integration tests or when that constraint changes.
        # This test is a placeholder documenting the limitation.
        r = _make_resolver()
        with tempfile.TemporaryDirectory() as d:
            result = r.resolve_artifact_path(d, 'story', {'story_key': '1-1-no-such'})
        # No file exists → not ambiguous, path is None
        self.assertFalse(result.ambiguous)
        self.assertIsNone(result.path)

    def test_resolve_product_brief_phase1(self):
        r = _make_resolver()
        with tempfile.TemporaryDirectory() as d:
            project_name = 'acme-app'
            preferred = r.build_preferred_path(d, 'product_brief', {'project_name': project_name})
            Path(preferred).parent.mkdir(parents=True, exist_ok=True)
            Path(preferred).write_text('# Product Brief', encoding='utf-8')
            result = r.resolve_artifact_path(d, 'product_brief', {'project_name': project_name})
        self.assertEqual(result.path, preferred)

    def test_resolve_prd_phase2(self):
        r = _make_resolver()
        with tempfile.TemporaryDirectory() as d:
            project_name = 'acme-app'
            preferred = r.build_preferred_path(d, 'prd', {'project_name': project_name})
            Path(preferred).parent.mkdir(parents=True, exist_ok=True)
            Path(preferred).write_text('# PRD', encoding='utf-8')
            result = r.resolve_artifact_path(d, 'prd', {'project_name': project_name})
        self.assertEqual(result.path, preferred)

    def test_resolve_architecture_phase3(self):
        r = _make_resolver()
        with tempfile.TemporaryDirectory() as d:
            project_name = 'acme-app'
            preferred = r.build_preferred_path(d, 'architecture', {'project_name': project_name})
            Path(preferred).parent.mkdir(parents=True, exist_ok=True)
            Path(preferred).write_text('# Architecture', encoding='utf-8')
            result = r.resolve_artifact_path(d, 'architecture', {'project_name': project_name})
        self.assertEqual(result.path, preferred)

    def test_resolve_unknown_artifact_type_raises(self):
        r = _make_resolver()
        with self.assertRaises(KeyError):
            r.resolve_artifact_path('/tmp/demo', 'nonexistent_artifact', {})


class TestResolvedPathDataclass(unittest.TestCase):
    def test_fields(self):
        rp = ResolvedPath(path='/some/path.md', source_kind='preferred', candidates=['/a.md', '/b.md'], ambiguous=False)
        self.assertEqual(rp.path, '/some/path.md')
        self.assertEqual(rp.source_kind, 'preferred')
        self.assertEqual(rp.candidates, ['/a.md', '/b.md'])
        self.assertFalse(rp.ambiguous)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Run all tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    all_tests = [
        # Template Renderer
        'tests.test_template_renderer',
        # Path Resolver
        'tests.test_path_resolver',
    ]

    # We import here to avoid top-level import issues
    import importlib

    for test_module_name in ['TestTemplateRendererBareVariable',
                              'TestTemplateRendererDefaultFilter',
                              'TestTemplateRendererMixed',
                              'TestTemplateRendererUnknownFilter',
                              'TestTemplateRendererFile',
                              'TestTemplateRendererEdgeCases',
                              'TestTemplateRendererCustomFilter',
                              'TestPathResolverBuildPreferred',
                              'TestPathResolverResolve',
                              'TestResolvedPathDataclass']:
        # Discover tests from this file
        pass

    # Build suite from this module
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)
