from __future__ import annotations

import re
from pathlib import Path


# Registry of built-in filters. Each receives (value, arg) and returns the filtered result.
_DEFAULT_FILTERS = {}


def _register_filter(name: str):
    """Decorator to register a filter function."""
    def decorator(fn):
        _DEFAULT_FILTERS[name] = fn
        return fn
    return decorator


@_register_filter('default')
def _default_filter(value, fallback):
    """Return fallback if value is None or empty string, else return value."""
    if value is None or value == '':
        return fallback
    return value


class TemplateRenderer:
    """Renders a template file with Jinja2-style {{ variable }} substitution
    and pipe filters (e.g. {{ name|default("Anonymous") }}).
    """

    # Matches {{ expr }} where expr may contain pipe filters.
    # Captures the full expression inside the braces.
    _BLOCK_RE = re.compile(r'\{\{\s*(.+?)\s*\}\}')

    # Matches a bare variable name (no filters) — used for the non-filter fast path.
    _BARE_VAR_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    # Matches:
    #   var|filter("arg")   — quoted string arg
    #   var|filter('arg')   — single-quoted string arg
    #   var|filter()        — no arg (empty parens, e.g. {{ name|upper() }})
    _FILTER_RE = re.compile(
        r'^(?P<var>[a-zA-Z_][a-zA-Z0-9_]*)\s*\|\s*(?P<filter>\w+)\s*(?:\(\s*(?:(["\'])(?P<arg>[^"\']*)\3|\s*)\s*\))?$'
    )

    def render(self, template_path: str, template_vars: dict) -> str:
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f'Template not found: {template_path}')
        template_text = path.read_text(encoding='utf-8')
        return self._substitute(template_text, template_vars)

    def _substitute(self, text: str, vars: dict) -> str:
        """Single-pass substitution. Handles bare {{ var }} and {{ var|filter("arg") }}.
        Quadruple-brace sequences ({{{{ and }}}}) are escape sequences for literal {{ and }}.
        """
        # Pre-process escape sequences: {{{{ → sentinel, }}}} → sentinel
        OB = '\x00OB\x00'
        CB = '\x00CB\x00'
        text = text.replace('{{{{', OB).replace('}}}}', CB)

        result = text

        def replacer(block_match: re.Match) -> str:
            expr = block_match.group(1).strip()

            # Fast path: bare variable with no filters
            if self._BARE_VAR_RE.match(expr):
                value = vars.get(expr, None)
                return '' if value is None else str(value)

            # Filter path: var|filter("arg")
            filter_match = self._FILTER_RE.match(expr)
            if filter_match:
                var_name = filter_match.group('var')
                filter_name = filter_match.group('filter')
                filter_arg = filter_match.group('arg')

                filter_fn = _DEFAULT_FILTERS.get(filter_name)
                if filter_fn is None:
                    return block_match.group(0)  # leave unresolved if filter unknown

                value = vars.get(var_name, None)
                return str(filter_fn(value, filter_arg))

            # Unknown expression shape — leave as-is
            return block_match.group(0)

        result = self._BLOCK_RE.sub(replacer, result)
        # Restore escape sentinels to literal {{ and }}
        result = result.replace(OB, '{{').replace(CB, '}}')
        return result


# ---------------------------------------------------------------------------
# Public filter registration (for users who want to add custom filters)
# ---------------------------------------------------------------------------
def register_filter(name_or_fn, fn=None):
    """Register a custom filter.

    Supports two call styles:
      @register_filter('upper')          # decorator style — returns a decorator
      register_filter('upper', my_fn)     # direct call style
    """
    if fn is not None:
        # Direct call: register_filter('upper', my_fn)
        _DEFAULT_FILTERS[name_or_fn] = fn
        return fn
    # Decorator style: @register_filter('upper')
    def decorator(f):
        _DEFAULT_FILTERS[name_or_fn] = f
        return f
    return decorator


def list_filters() -> list[str]:
    """Return names of all registered filters."""
    return list(_DEFAULT_FILTERS.keys())
