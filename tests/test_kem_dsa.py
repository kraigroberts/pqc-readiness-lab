from __future__ import annotations

import pytest

from pqc_lab import lib


kem_algs = ["mlkem512", "mlkem768", "mlkem1024"]
dsa_algs = ["mldsa44", "mldsa65", "mldsa87"]


skip_no_liboqs = pytest.mark.skipif(not lib.is_available(), reason="liboqs not available")


@skip_no_liboqs
@pytest.mark.parametrize("alg", kem_algs)
def test_kem_roundtrip(alg: str) -> None:
    kp = lib.generate_keypair(alg)
    assert kp is not None
    pk, sk = kp
    enc = lib.encapsulate_key(alg, pk)
    assert enc is not None
    ct, ss1 = enc
    ss2 = lib.decapsulate_key(alg, ct, sk)
    assert ss2 is not None and ss1 == ss2


@skip_no_liboqs
@pytest.mark.parametrize("alg", dsa_algs)
def test_dsa_roundtrip(alg: str) -> None:
    kp = lib.generate_keypair(alg)
    assert kp is not None
    pk, sk = kp
    msg = b"hello pqc"
    sig = lib.sign_message(alg, msg, sk)
    assert sig is not None
    assert lib.verify_signature(alg, msg, sig, pk)

