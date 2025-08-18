from __future__ import annotations

import threading
import time

import pytest

from pqc_lab import lib
from pqc_lab.handshake import HandshakeParams, run_client, run_server


skip_no_liboqs = pytest.mark.skipif(not lib.is_available(), reason="liboqs not available")


@skip_no_liboqs
def test_handshake_roundtrip() -> None:
    params = HandshakeParams(host="127.0.0.1", port=5566, algorithm="mlkem768")
    server_thread = threading.Thread(target=run_server, args=(params,), daemon=True)
    server_thread.start()
    time.sleep(0.1)
    msg = b"hello pqc"
    reply = run_client(params, msg)
    assert reply == msg.upper()

