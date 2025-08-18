from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from pqc_lab import lib
from pqc_lab.cli import main


skip_no_liboqs = pytest.mark.skipif(not lib.is_available(), reason="liboqs not available")


@skip_no_liboqs
def test_cli_sign_verify_roundtrip(tmp_path: Path) -> None:
    runner = CliRunner()
    msg_file = tmp_path / "msg.txt"
    msg_file.write_text("hello pqc")

    pub = tmp_path / "mldsa65.pub"
    priv = tmp_path / "mldsa65.priv"
    sig = tmp_path / "msg.sig"

    r1 = runner.invoke(main, [
        "keygen", "--alg", "mldsa65", "--pub", str(pub), "--priv", str(priv), "--out", str(tmp_path)
    ])
    assert r1.exit_code == 0

    r2 = runner.invoke(main, [
        "sign", "--alg", "mldsa65", "--in", str(msg_file), "--priv", str(priv), "--pub", str(pub), "--sig", str(sig)
    ])
    assert r2.exit_code == 0 and sig.exists()

    r3 = runner.invoke(main, [
        "verify", "--alg", "mldsa65", "--in", str(msg_file), "--pub", str(pub), "--sig", str(sig)
    ])
    assert r3.exit_code == 0
    assert "OK" in r3.output

