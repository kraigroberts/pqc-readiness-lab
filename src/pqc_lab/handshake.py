from __future__ import annotations

import socket
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from . import lib


@dataclass
class HandshakeParams:
    host: str = "127.0.0.1"
    port: int = 5555
    algorithm: str = "mlkem768"


def _derive_aead_key(shared_secret: bytes) -> bytes:
    # ML-KEM shared secret is 32 bytes; ChaCha20-Poly1305 key is 32 bytes
    if len(shared_secret) < 32:
        raise ValueError("shared secret too short for AEAD key")
    return shared_secret[:32]


def run_server(params: HandshakeParams) -> None:
    if not lib.is_available():
        raise RuntimeError("liboqs not available")

    kp = lib.generate_keypair(params.algorithm)
    if not kp:
        raise RuntimeError("keygen failed")
    pk, sk = kp

    with socket.create_server((params.host, params.port)) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn, _addr = srv.accept()
        with conn:
            conn.sendall(len(pk).to_bytes(4, "big") + pk)
            hdr = conn.recv(4)
            if len(hdr) != 4:
                raise RuntimeError("invalid ciphertext header")
            ct_len = int.from_bytes(hdr, "big")
            ct = conn.recv(ct_len)
            if len(ct) != ct_len:
                raise RuntimeError("invalid ciphertext body")
            ss = lib.decapsulate_key(params.algorithm, ct, sk)
            if ss is None:
                raise RuntimeError("decapsulate failed")
            key = _derive_aead_key(ss)
            aead = ChaCha20Poly1305(key)
            hdr = conn.recv(4)
            if len(hdr) != 4:
                raise RuntimeError("invalid aead header")
            m_len = int.from_bytes(hdr, "big")
            nonce = conn.recv(12)
            ct_msg = conn.recv(m_len)
            msg = aead.decrypt(nonce, ct_msg, None)
            reply = msg.upper()
            nonce2 = b"0" * 12
            ct2 = aead.encrypt(nonce2, reply, None)
            conn.sendall(len(ct2).to_bytes(4, "big") + nonce2 + ct2)


def run_client(params: HandshakeParams, message: bytes) -> bytes:
    if not lib.is_available():
        raise RuntimeError("liboqs not available")

    with socket.create_connection((params.host, params.port)) as s:
        hdr = s.recv(4)
        if len(hdr) != 4:
            raise RuntimeError("invalid pk header")
        pk_len = int.from_bytes(hdr, "big")
        pk = s.recv(pk_len)
        if len(pk) != pk_len:
            raise RuntimeError("invalid pk body")
        enc = lib.encapsulate_key(params.algorithm, pk)
        if not enc:
            raise RuntimeError("encapsulate failed")
        ct, ss = enc
        s.sendall(len(ct).to_bytes(4, "big") + ct)
        key = _derive_aead_key(ss)
        aead = ChaCha20Poly1305(key)
        nonce = b"1" * 12
        ct_msg = aead.encrypt(nonce, message, None)
        s.sendall(len(ct_msg).to_bytes(4, "big") + nonce + ct_msg)
        hdr = s.recv(4)
        if len(hdr) != 4:
            raise RuntimeError("invalid reply header")
        m_len = int.from_bytes(hdr, "big")
        nonce2 = s.recv(12)
        ct2 = s.recv(m_len)
        reply = aead.decrypt(nonce2, ct2, None)
        return reply

