from __future__ import annotations

import re


CHECKBOX_RE = re.compile(r'^(\s*-\s*\[)( |x|X)(\]\s+)(.*)$')


class CheckboxOps:
    """Safe checkbox line operations on markdown task lists."""

    def set_checkbox(self, section_text: str, match_text: str, checked: bool) -> str:
        """
        Toggle or set a checkbox by matching the label text.
        match_text is substring-matched against the checkbox label.
        Returns updated section_text; raises ValueError if no match found.
        """
        marker = 'x' if checked else ' '
        lines = section_text.splitlines()
        updated_lines: list[str] = []
        found = False
        for line in lines:
            m = CHECKBOX_RE.match(line)
            if m and match_text in m.group(4):
                updated_lines.append(f'{m.group(1)}{marker}{m.group(3)}{m.group(4)}')
                found = True
            else:
                updated_lines.append(line)
        if not found:
            raise ValueError(f'No checkbox line found containing: {match_text!r}')
        return '\n'.join(updated_lines)
