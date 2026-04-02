import json
from pathlib import Path
from bmad_workflow_plugin.state.state_reader import StateReader


def test_state_reader_reads_existing_state(tmp_path: Path) -> None:
    bmad = tmp_path / '_bmad'
    bmad.mkdir()
    state_path = bmad / 'state.json'
    state_path.write_text(json.dumps({'schema_version': '2.0'}), encoding='utf-8')
    data = StateReader().read(str(tmp_path))
    assert data['schema_version'] == '2.0'
