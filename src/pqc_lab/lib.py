"""Minimal liboqs availability probe for milestone 1."""

from __future__ import annotations

import ctypes
import ctypes.util
from typing import Optional

_liboqs: Optional[ctypes.CDLL] = None


def get_liboqs() -> Optional[ctypes.CDLL]:
    global _liboqs
    if _liboqs is not None:
        return _liboqs
    path = ctypes.util.find_library("oqs")
    if not path:
        return None
    try:
        _liboqs = ctypes.CDLL(path)
    except OSError:
        _liboqs = None
    return _liboqs


def is_available() -> bool:
    return get_liboqs() is not None

