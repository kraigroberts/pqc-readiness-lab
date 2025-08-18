"""liboqs integration module for PQC Readiness Lab.

This module provides a thin wrapper around the Open Quantum Safe library
for Post-Quantum Cryptography operations.
"""

import ctypes
import ctypes.util
import logging
from pathlib import Path

from . import config

logger = logging.getLogger(__name__)

# liboqs library handle
_liboqs_lib: ctypes.CDLL | None = None


class LibOQSError(Exception):
    """Exception raised for liboqs errors."""

    pass


def _load_liboqs() -> ctypes.CDLL | None:
    """Load the liboqs library."""
    global _liboqs_lib

    if _liboqs_lib is not None:
        return _liboqs_lib

    # Try to find liboqs in common locations
    lib_paths = [
        "liboqs",
        "/usr/local/lib/liboqs.so",
        "/usr/local/lib/liboqs.dylib",
        "/usr/lib/liboqs.so",
        "/usr/lib/liboqs.dylib",
    ]

    # Add custom path if specified
    if config.config.liboqs_path:
        custom_path = config.config.liboqs_path / "lib" / "liboqs.so"
        if custom_path.exists():
            lib_paths.insert(0, str(custom_path))

    lib: ctypes.CDLL | None = None
    for path in lib_paths:
        try:
            if Path(path).exists():
                lib = ctypes.CDLL(path)
                logger.info(f"Loaded liboqs from: {path}")
                break
            else:
                # Try to find library in system paths
                found_lib = ctypes.util.find_library("oqs")
                if found_lib:
                    lib = ctypes.CDLL(found_lib)
                    logger.info(f"Loaded liboqs from system: {found_lib}")
                    break
        except (OSError, ImportError) as e:
            logger.debug(f"Failed to load liboqs from {path}: {e}")
            continue

    if lib is None:
        logger.warning(
            "Could not load liboqs library. PQC operations will not be available."
        )
        return None

    # Set function signatures for common liboqs functions
    try:
        # KEM functions
        lib.OQS_KEM_new.argtypes = [ctypes.c_char_p]
        lib.OQS_KEM_new.restype = ctypes.c_void_p

        lib.OQS_KEM_free.argtypes = [ctypes.c_void_p]
        lib.OQS_KEM_free.restype = None

        lib.OQS_KEM_keypair.argtypes = [
            ctypes.c_void_p,  # kem
            ctypes.POINTER(ctypes.c_uint8),  # public_key
            ctypes.POINTER(ctypes.c_uint8),  # secret_key
        ]
        lib.OQS_KEM_keypair.restype = ctypes.c_int

        lib.OQS_KEM_encaps.argtypes = [
            ctypes.c_void_p,  # kem
            ctypes.POINTER(ctypes.c_uint8),  # ciphertext
            ctypes.POINTER(ctypes.c_uint8),  # shared_secret
            ctypes.POINTER(ctypes.c_uint8),  # public_key
        ]
        lib.OQS_KEM_encaps.restype = ctypes.c_int

        lib.OQS_KEM_decaps.argtypes = [
            ctypes.c_void_p,  # kem
            ctypes.POINTER(ctypes.c_uint8),  # shared_secret
            ctypes.POINTER(ctypes.c_uint8),  # ciphertext
            ctypes.POINTER(ctypes.c_uint8),  # secret_key
        ]
        lib.OQS_KEM_decaps.restype = ctypes.c_int

        # DSA functions
        lib.OQS_SIG_new.argtypes = [ctypes.c_char_p]
        lib.OQS_SIG_new.restype = ctypes.c_void_p

        lib.OQS_SIG_free.argtypes = [ctypes.c_void_p]
        lib.OQS_SIG_free.restype = None

        lib.OQS_SIG_keypair.argtypes = [
            ctypes.c_void_p,  # sig
            ctypes.POINTER(ctypes.c_uint8),  # public_key
            ctypes.POINTER(ctypes.c_uint8),  # secret_key
        ]
        lib.OQS_SIG_keypair.restype = ctypes.c_int

        lib.OQS_SIG_sign.argtypes = [
            ctypes.c_void_p,  # sig
            ctypes.POINTER(ctypes.c_uint8),  # signature
            ctypes.POINTER(ctypes.c_size_t),  # signature_len
            ctypes.POINTER(ctypes.c_uint8),  # message
            ctypes.c_size_t,  # message_len
            ctypes.POINTER(ctypes.c_uint8),  # secret_key
        ]
        lib.OQS_SIG_sign.restype = ctypes.c_int

        lib.OQS_SIG_verify.argtypes = [
            ctypes.c_void_p,  # sig
            ctypes.POINTER(ctypes.c_uint8),  # message
            ctypes.c_size_t,  # message_len
            ctypes.POINTER(ctypes.c_uint8),  # signature
            ctypes.c_size_t,  # signature_len
            ctypes.POINTER(ctypes.c_uint8),  # public_key
        ]
        lib.OQS_SIG_verify.restype = ctypes.c_int

        logger.info("Successfully configured liboqs function signatures")

    except AttributeError as e:
        logger.warning(f"Could not configure all liboqs functions: {e}")

    _liboqs_lib = lib
    return lib


def get_liboqs() -> ctypes.CDLL | None:
    """Get the loaded liboqs library instance."""
    return _load_liboqs()


def is_available() -> bool:
    """Check if liboqs is available."""
    return get_liboqs() is not None


def get_supported_kems() -> list[str]:
    """Get list of supported KEM algorithms."""
    lib = get_liboqs()
    if lib is None:
        return []

    # For now, return the configured algorithms
    # In a full implementation, this would query liboqs
    return config.get_kem_algorithms()


def get_supported_sigs() -> list[str]:
    """Get list of supported signature algorithms."""
    lib = get_liboqs()
    if lib is None:
        return []

    # For now, return the configured algorithms
    # In a full implementation, this would query liboqs
    return config.get_dsa_algorithms()


def get_kem_details(alg_name: str) -> dict | None:
    """Get details about a KEM algorithm."""
    lib = get_liboqs()
    if lib is None:
        return None

    # For now, return basic information
    # In a full implementation, this would query liboqs
    if alg_name in get_supported_kems():
        return {
            "name": alg_name,
            "type": "KEM",
            "claimed_nist_level": (
                1 if "512" in alg_name else (2 if "768" in alg_name else 3)
            ),
            "is_ind_cca": True,
        }

    return None


def get_sig_details(alg_name: str) -> dict | None:
    """Get details about a signature algorithm."""
    lib = get_liboqs()
    if lib is None:
        return None

    # For now, return basic information
    # In a full implementation, this would query liboqs
    if alg_name in get_supported_sigs():
        return {
            "name": alg_name,
            "type": "DSA",
            "claimed_nist_level": (
                1 if "44" in alg_name else (2 if "65" in alg_name else 3)
            ),
            "is_euf_cma": True,
        }

    return None


# Version information
def get_version() -> str:
    """Get liboqs version."""
    lib = get_liboqs()
    if lib is None:
        return "unknown"

    try:
        # Try to get version from liboqs
        version_func = getattr(lib, "OQS_get_library_version", None)
        if version_func:
            version_func.restype = ctypes.c_char_p
            result = version_func()
            if result is not None:
                decoded = result.decode("utf-8")
                if isinstance(decoded, str):
                    return decoded
    except Exception:
        pass

    return "unknown"


def get_enabled_features() -> list[str]:
    """Get list of enabled liboqs features."""
    lib = get_liboqs()
    if lib is None:
        return []

    features = []

    # Check for OpenSSL integration
    if config.config.enable_openssl:
        try:
            # Try to detect OpenSSL integration
            if hasattr(lib, "OQS_OPENSSL_1_1_1_loaded"):
                features.append("OpenSSL-1.1.1")
            elif hasattr(lib, "OQS_OPENSSL_3_0_loaded"):
                features.append("OpenSSL-3.0")
        except Exception:
            pass

    # Check for specific algorithm families
    if get_supported_kems():
        features.append("KEM")
    if get_supported_sigs():
        features.append("DSA")

    return features


# ---- Algorithm mapping and sizes ----

_KEM_NAME_MAP: dict[str, bytes] = {
    "mlkem512": b"ML-KEM-512",
    "mlkem768": b"ML-KEM-768",
    "mlkem1024": b"ML-KEM-1024",
}

_DSA_NAME_MAP: dict[str, bytes] = {
    "mldsa44": b"ML-DSA-44",
    "mldsa65": b"ML-DSA-65",
    "mldsa87": b"ML-DSA-87",
}

_KEM_SIZES: dict[str, dict[str, int]] = {
    "mlkem512": {"public_key": 800, "secret_key": 1632, "ciphertext": 768, "shared_secret": 32},
    "mlkem768": {"public_key": 1184, "secret_key": 2400, "ciphertext": 1088, "shared_secret": 32},
    "mlkem1024": {"public_key": 1568, "secret_key": 3168, "ciphertext": 1568, "shared_secret": 32},
}

_DSA_SIZES: dict[str, dict[str, int]] = {
    "mldsa44": {"public_key": 1312, "secret_key": 2528, "signature": 2420},
    "mldsa65": {"public_key": 1952, "secret_key": 4000, "signature": 3293},
    "mldsa87": {"public_key": 2592, "secret_key": 4864, "signature": 4595},
}


def _map_kem_name(alg_name: str) -> bytes | None:
    return _KEM_NAME_MAP.get(alg_name)


def _map_sig_name(alg_name: str) -> bytes | None:
    return _DSA_NAME_MAP.get(alg_name)


def _kem_sizes(alg_name: str) -> dict[str, int] | None:
    return _KEM_SIZES.get(alg_name)


def _dsa_sizes(alg_name: str) -> dict[str, int] | None:
    return _DSA_SIZES.get(alg_name)


# ---- PQC operations ----

def generate_keypair(alg_name: str) -> tuple[bytes, bytes] | None:
    """Generate a keypair for KEM (mlkem*) or DSA (mldsa*)."""
    lib = get_liboqs()
    if lib is None:
        return None

    if alg_name.startswith("mlkem"):
        kem_name = _map_kem_name(alg_name)
        sizes = _kem_sizes(alg_name)
        if kem_name is None or sizes is None:
            return None
        kem = lib.OQS_KEM_new(kem_name)
        if not kem:
            return None
        try:
            pk = (ctypes.c_uint8 * sizes["public_key"])()
            sk = (ctypes.c_uint8 * sizes["secret_key"])()
            rc = lib.OQS_KEM_keypair(kem, pk, sk)
            if rc != 0:
                return None
            return bytes(pk), bytes(sk)
        finally:
            lib.OQS_KEM_free(kem)
    else:
        sig_name = _map_sig_name(alg_name)
        sizes = _dsa_sizes(alg_name)
        if sig_name is None or sizes is None:
            return None
        sig = lib.OQS_SIG_new(sig_name)
        if not sig:
            return None
        try:
            pk = (ctypes.c_uint8 * sizes["public_key"])()
            sk = (ctypes.c_uint8 * sizes["secret_key"])()
            rc = lib.OQS_SIG_keypair(sig, pk, sk)
            if rc != 0:
                return None
            return bytes(pk), bytes(sk)
        finally:
            lib.OQS_SIG_free(sig)


def encapsulate_key(alg_name: str, public_key: bytes) -> tuple[bytes, bytes] | None:
    """Encapsulate a shared secret using a KEM public key."""
    lib = get_liboqs()
    if lib is None:
        return None
    kem_name = _map_kem_name(alg_name)
    sizes = _kem_sizes(alg_name)
    if kem_name is None or sizes is None:
        return None
    kem = lib.OQS_KEM_new(kem_name)
    if not kem:
        return None
    try:
        ct = (ctypes.c_uint8 * sizes["ciphertext"])()
        ss = (ctypes.c_uint8 * sizes["shared_secret"])()
        pk_arr = (ctypes.c_uint8 * len(public_key)).from_buffer_copy(public_key)
        rc = lib.OQS_KEM_encaps(kem, ct, ss, pk_arr)
        if rc != 0:
            return None
        return bytes(ct), bytes(ss)
    finally:
        lib.OQS_KEM_free(kem)


def decapsulate_key(alg_name: str, ciphertext: bytes, secret_key: bytes) -> bytes | None:
    """Decapsulate a shared secret using a KEM secret key."""
    lib = get_liboqs()
    if lib is None:
        return None
    kem_name = _map_kem_name(alg_name)
    sizes = _kem_sizes(alg_name)
    if kem_name is None or sizes is None:
        return None
    kem = lib.OQS_KEM_new(kem_name)
    if not kem:
        return None
    try:
        ss = (ctypes.c_uint8 * sizes["shared_secret"])()
        ct_arr = (ctypes.c_uint8 * len(ciphertext)).from_buffer_copy(ciphertext)
        sk_arr = (ctypes.c_uint8 * len(secret_key)).from_buffer_copy(secret_key)
        rc = lib.OQS_KEM_decaps(kem, ss, ct_arr, sk_arr)
        if rc != 0:
            return None
        return bytes(ss)
    finally:
        lib.OQS_KEM_free(kem)


def sign_message(alg_name: str, message: bytes, secret_key: bytes) -> bytes | None:
    """Sign a message using the specified signature algorithm."""
    lib = get_liboqs()
    if lib is None:
        return None
    sig_name = _map_sig_name(alg_name)
    sizes = _dsa_sizes(alg_name)
    if sig_name is None or sizes is None:
        return None
    sig = lib.OQS_SIG_new(sig_name)
    if not sig:
        return None
    try:
        sig_buf = (ctypes.c_uint8 * sizes["signature"])()
        sig_len = ctypes.c_size_t(0)
        msg_arr = (ctypes.c_uint8 * len(message)).from_buffer_copy(message)
        sk_arr = (ctypes.c_uint8 * len(secret_key)).from_buffer_copy(secret_key)
        rc = lib.OQS_SIG_sign(sig, sig_buf, ctypes.byref(sig_len), msg_arr, len(message), sk_arr)
        if rc != 0:
            return None
        return bytes(bytearray(sig_buf)[: sig_len.value])
    finally:
        lib.OQS_SIG_free(sig)


def verify_signature(alg_name: str, message: bytes, signature: bytes, public_key: bytes) -> bool:
    """Verify a message signature."""
    lib = get_liboqs()
    if lib is None:
        return False
    sig_name = _map_sig_name(alg_name)
    if sig_name is None:
        return False
    sig = lib.OQS_SIG_new(sig_name)
    if not sig:
        return False
    try:
        msg_arr = (ctypes.c_uint8 * len(message)).from_buffer_copy(message)
        sig_arr = (ctypes.c_uint8 * len(signature)).from_buffer_copy(signature)
        pk_arr = (ctypes.c_uint8 * len(public_key)).from_buffer_copy(public_key)
        rc = lib.OQS_SIG_verify(sig, msg_arr, len(message), sig_arr, len(signature), pk_arr)
        return rc == 0
    finally:
        lib.OQS_SIG_free(sig)
