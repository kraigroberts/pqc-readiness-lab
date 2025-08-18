from __future__ import annotations

import json

from click.testing import CliRunner

from pqc_lab import __version__
from pqc_lab.cli import main


def test_import_and_version() -> None:
    assert isinstance(__version__, str) and len(__version__) > 0


def test_cli_info() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["info"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["version"] == __version__

