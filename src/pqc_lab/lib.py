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

    lib = None
    for path in lib_paths:
        try:
            if Path(path).exists():
                lib = ctypes.CDLL(path)
                logger.info(f"Loaded liboqs from: {path}")
                break
            else:
                # Try to find library in system paths
                lib = ctypes.util.find_library("oqs")
                if lib:
                    lib = ctypes.CDLL(lib)
                    logger.info(f"Loaded liboqs from system: {lib}")
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
            return version_func().decode("utf-8")
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
