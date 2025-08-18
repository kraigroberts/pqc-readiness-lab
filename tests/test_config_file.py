from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from pqc_lab.cli import main


def test_config_file_overrides(tmp_path: Path) -> None:
    cfg = {
        "algorithm": {
            "default_kem": "ML-KEM-512",
            "default_dsa": "ML-DSA-44",
        },
        "network": {"default_host": "0.0.0.0", "default_port": 6000},
    }
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps(cfg))

    runner = CliRunner()
    res = runner.invoke(main, ["--config", str(cfg_path), "info"])  # reuse info output
    assert res.exit_code == 0

