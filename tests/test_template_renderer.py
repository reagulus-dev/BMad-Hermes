from __future__ import annotations

import pytest
import tempfile
import os
from pathlib import Path

from bmad_workflow_plugin.mutations.template_renderer import (
    TemplateRenderer,
    register_filter,
    list_filters,
)


class TestTemplateRendererBareVariable:
    def test_bare_variable_resolved(self):
        r = TemplateRenderer()
        text = "Hello, {{ name }}!"
        assert r._substitute(text, {'name': 'Alice'}) == "Hello, Alice!"

    def test_bare_variable_undefined(self):
        r = TemplateRenderer()
        text = "Hello, {{ name }}!"
        assert r._substitute(text, {}) == "Hello, !"

    def test_bare_variable_with_spaces(self):
        r = TemplateRenderer()
        text = "Hello, {{  name  }}!"
        assert r._substitute(text, {'name': 'Bob'}) == "Hello, Bob!"

    def test_multiple_bare_variables(self):
        r = TemplateRenderer()
        text = "{{ greeting }}, {{ name }}!"
        assert r._substitute(text, {'greeting': 'Hello', 'name': 'Carol'}) == "Hello, Carol!"

    def test_bare_variable_value_none(self):
        r = TemplateRenderer()
        text = "Value: {{ val }}"
        assert r._substitute(text, {'val': None}) == "Value: "

    def test_bare_variable_value_empty_string(self):
        r = TemplateRenderer()
        text = "Value: {{ val }}"
        assert r._substitute(text, {'val': ''}) == "Value: "


class TestTemplateRendererDefaultFilter:
    def test_default_filter_provided(self):
        r = TemplateRenderer()
        text = "Status: {{status|default(\"draft\")}}"
        assert r._substitute(text, {'status': 'review'}) == "Status: review"

    def test_default_filter_missing(self):
        r = TemplateRenderer()
        text = "Status: {{status|default(\"draft\")}}"
        assert r._substitute(text, {}) == "Status: draft"

    def test_default_filter_empty_string(self):
        r = TemplateRenderer()
        text = "Status: {{status|default(\"draft\")}}"
        assert r._substitute(text, {'status': ''}) == "Status: draft"

    def test_default_filter_none(self):
        r = TemplateRenderer()
        text = "Status: {{status|default(\"draft\")}}"
        assert r._substitute(text, {'status': None}) == "Status: draft"

    def test_default_filter_with_spaces(self):
        r = TemplateRenderer()
        text = "{{ tracking_system|default(\"file-system\")}}"
        assert r._substitute(text, {}) == "file-system"
        assert r._substitute(text, {'tracking_system': 'linear'}) == "linear"

    def test_default_filter_single_quoted(self):
        r = TemplateRenderer()
        text = "{{val|default('fallback')}}"
        assert r._substitute(text, {}) == "fallback"
        assert r._substitute(text, {'val': 'actual'}) == "actual"

    def test_default_filter_complex_fallback(self):
        r = TemplateRenderer()
        text = '{{story_location|default("_bmad/artifacts/stories")}}'
        assert r._substitute(text, {}) == "_bmad/artifacts/stories"

    def test_default_filter_nested_in_heading(self):
        r = TemplateRenderer()
        text = "# {{headline|default(\"Headline: {product name}\")}}"
        assert r._substitute(text, {}) == "# Headline: {product name}"
        assert r._substitute(text, {'headline': 'My Amazing Product'}) == "# My Amazing Product"

    def test_default_filter_with_braces_in_fallback(self):
        r = TemplateRenderer()
        text = "{{val|default(\"{something}\")}}"
        assert r._substitute(text, {}) == "{something}"


class TestTemplateRendererMixed:
    def test_mixed_bare_and_filter(self):
        r = TemplateRenderer()
        text = "Status: {{status|default(\"draft\")}} — {{author}}"
        result = r._substitute(text, {'author': 'Alice', 'status': 'done'})
        assert result == "Status: done — Alice"

    def test_prfaq_template_fragment(self):
        r = TemplateRenderer()
        text = "Status: {{status|default(\"draft\")}}\nStage: {{stage|default(\"concept\")}}\n\n# {{headline|default(\"Headline: {product}\")}}"
        vars = {'headline': 'Acme AI'}
        assert r._substitute(text, vars) == (
            "Status: draft\nStage: concept\n\n# Acme AI"
        )

    def test_real_sprint_status_yaml_fragment(self):
        r = TemplateRenderer()
        text = (
            'tracking_system: {{tracking_system|default("file-system")}}\n'
            'story_location: "{{story_location|default("_bmad/artifacts/stories")}}"'
        )
        # With no vars, defaults kick in
        assert r._substitute(text, {}) == (
            'tracking_system: file-system\n'
            'story_location: "_bmad/artifacts/stories"'
        )
        # With vars, values override
        assert r._substitute(text, {'tracking_system': 'linear', 'story_location': 'stories/'}) == (
            'tracking_system: linear\n'
            'story_location: "stories/"'
        )


class TestTemplateRendererUnknownFilter:
    def test_unknown_filter_leaves_expression_unmodified(self):
        r = TemplateRenderer()
        text = "{{val|unknown_filter(\"arg\")}}"
        result = r._substitute(text, {'val': 'something'})
        # Unknown filters are left as-is
        assert '{{val|unknown_filter("arg")}}' in result


class TestTemplateRendererFile:
    def test_render_reads_file(self):
        r = TemplateRenderer()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, {{ name }}!")
            path = f.name
        try:
            result = r.render(path, {'name': 'FileTest'})
            assert result == "Hello, FileTest!"
        finally:
            os.unlink(path)

    def test_render_file_not_found(self):
        r = TemplateRenderer()
        with pytest.raises(FileNotFoundError):
            r.render('/nonexistent/path/to/template.txt', {})


class TestTemplateRendererEdgeCases:
    def test_double_braces_not_substituted(self):
        r = TemplateRenderer()
        text = "{{{{ name }}}}"
        # Outer braces are substituted; inner are literal
        result = r._substitute(text, {'name': 'Alice'})
        assert result == "{{ name }}"

    def test_no_braces(self):
        r = TemplateRenderer()
        text = "No variables here."
        assert r._substitute(text, {'name': 'Alice'}) == "No variables here."

    def test_special_chars_in_value(self):
        r = TemplateRenderer()
        text = "{{val|default(\"draft\")}}"
        assert r._substitute(text, {'val': 'status: done'}) == "status: done"


class TestTemplateRendererCustomFilter:
    def test_register_and_use_custom_filter(self):
        @register_filter('upper')
        def upper_filter(value, _arg):
            return str(value).upper() if value else ''

        r = TemplateRenderer()
        text = "{{name|upper}}"
        assert r._substitute(text, {'name': 'alice'}) == "ALICE"
        # Clean up
        from bmad_workflow_plugin.mutations.template_renderer import _DEFAULT_FILTERS
        del _DEFAULT_FILTERS['upper']

    def test_list_filters_contains_default(self):
        assert 'default' in list_filters()
