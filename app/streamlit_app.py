from __future__ import annotations

import time
from typing import Optional

import streamlit as st
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from pqc_lab import lib


st.set_page_config(page_title="PQC Readiness Lab", layout="centered")
st.title("PQC Readiness Lab – Visual Demo")


def render_status() -> None:
    st.subheader("Library status")
    available = lib.is_available()
    st.write(f"liboqs available: {'✅' if available else '❌'}")
    st.write(f"liboqs version: {lib.get_version()}")


def demo_sign_verify() -> None:
    st.subheader("Sign / Verify (ML-DSA-65)")
    message = st.text_area("Message", value="Hello PQC!", height=100)
    if st.button("Generate keys and sign"):
        if not lib.is_available():
            st.error("liboqs not available")
            return
        kp = lib.generate_keypair("mldsa65")
        if not kp:
            st.error("Key generation failed")
            return
        pk, sk = kp
        sig = lib.sign_message("mldsa65", message.encode(), sk)
        if not sig:
            st.error("Sign failed")
            return
        st.success(f"Signature length: {len(sig)} bytes")
        ok = lib.verify_signature("mldsa65", message.encode(), sig, pk)
        st.write(f"Verification: {'✅ OK' if ok else '❌ FAIL'}")


def demo_kem_encrypt() -> None:
    st.subheader("KEM-derived encryption (ML-KEM-768 → ChaCha20-Poly1305)")
    plaintext = st.text_area("Message to encrypt", value="quantum-safe", height=80)
    if st.button("Run KEM + AEAD demo"):
        if not lib.is_available():
            st.error("liboqs not available")
            return
        # Keygen
        kp = lib.generate_keypair("mlkem768")
        if not kp:
            st.error("KEM keygen failed")
            return
        pk, sk = kp
        # Encapsulate / decapsulate
        enc = lib.encapsulate_key("mlkem768", pk)
        if not enc:
            st.error("Encapsulate failed")
            return
        ct, ss1 = enc
        ss2 = lib.decapsulate_key("mlkem768", ct, sk)
        if ss2 is None:
            st.error("Decapsulate failed")
            return
        st.write(f"Shared secret length: {len(ss1)} bytes; match: {'✅' if ss1 == ss2 else '❌'}")
        # AEAD encrypt with shared secret
        key = ss1[:32]
        aead = ChaCha20Poly1305(key)
        nonce = b"demo-nonce-01"  # 12 bytes
        ct_msg = aead.encrypt(nonce, plaintext.encode(), None)
        pt = aead.decrypt(nonce, ct_msg, None)
        st.code(ct_msg.hex()[:96] + ("…" if len(ct_msg) > 48 else ""), language="text")
        st.write(f"Decrypted == original: {'✅' if pt.decode()==plaintext else '❌'}")


def demo_bench() -> None:
    st.subheader("Quick Benchmarks")
    alg = st.selectbox("Algorithm", ["mlkem768", "mldsa65"], index=0)
    iters = st.slider("Iterations", min_value=5, max_value=200, value=50, step=5)
    if st.button("Run benchmark"):
        if not lib.is_available():
            st.error("liboqs not available")
            return
        t0 = time.perf_counter()
        if alg.startswith("mlkem"):
            kp = lib.generate_keypair(alg)
            if not kp:
                st.error("Keygen failed")
                return
            pk, sk = kp
            enc_times = []
            dec_times = []
            for _ in range(iters):
                s = time.perf_counter()
                enc = lib.encapsulate_key(alg, pk)
                m = time.perf_counter()
                if not enc:
                    st.error("Encapsulate failed")
                    return
                ct, _ = enc
                e = time.perf_counter()
                ss = lib.decapsulate_key(alg, ct, sk)
                f = time.perf_counter()
                if ss is None:
                    st.error("Decapsulate failed")
                    return
                enc_times.append(m - s)
                dec_times.append(f - e)
            st.write(f"avg encaps: {sum(enc_times)/len(enc_times):.6f}s; avg decaps: {sum(dec_times)/len(dec_times):.6f}s")
        else:
            kp = lib.generate_keypair(alg)
            if not kp:
                st.error("Keygen failed")
                return
            pk, sk = kp
            msg = b"benchmark"
            sign_times = []
            verify_times = []
            for _ in range(iters):
                s = time.perf_counter()
                sig = lib.sign_message(alg, msg, sk)
                m = time.perf_counter()
                if not sig:
                    st.error("Sign failed")
                    return
                ok = lib.verify_signature(alg, msg, sig, pk)
                e = time.perf_counter()
                if not ok:
                    st.error("Verify failed")
                    return
                sign_times.append(m - s)
                verify_times.append(e - m)
            st.write(f"avg sign: {sum(sign_times)/len(sign_times):.6f}s; avg verify: {sum(verify_times)/len(verify_times):.6f}s")
        st.caption(f"Elapsed: {time.perf_counter()-t0:.3f}s")


render_status()
st.divider()
demo_sign_verify()
st.divider()
demo_kem_encrypt()
st.divider()
demo_bench()


