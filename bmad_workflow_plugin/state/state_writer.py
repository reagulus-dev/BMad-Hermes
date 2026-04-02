from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path


class StateWriter:
    """Atomic, safe write to _bmad/state.json via temp-file rename."""

    def write_patch(self, project_root: str, patch: dict) -> str:
        bmad_dir = Path(project_root) / '_bmad'
        state_path = bmad_dir / 'state.json'

        # Load current state (or start from empty)
        if state_path.exists():
            with state_path.open('r', encoding='utf-8') as f:
                current: dict = json.load(f)
        else:
            current = {}

        # Merge patch — patch keys win; existing keys not in patch are preserved
        merged = {**current, **patch}

        # Always stamp updated_at
        merged['updated_at'] = datetime.now(timezone.utc).isoformat()

        # Ensure _bmad dir exists
        bmad_dir.mkdir(parents=True, exist_ok=True)

        # Atomic write: temp file in same dir, then rename
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=str(bmad_dir), suffix='.tmp', delete=False
            ) as tmp:
                tmp_path = tmp.name
                json.dump(merged, tmp, indent=2, ensure_ascii=False)
                tmp.write('\n')
            Path(tmp_path).replace(state_path)
        finally:
            # Clean up temp file if something went wrong
            if tmp_path is not None and Path(tmp_path).exists():
                Path(tmp_path).unlink(missing_ok=True)

        return str(state_path.resolve())
