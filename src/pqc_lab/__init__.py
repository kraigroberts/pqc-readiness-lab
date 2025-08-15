"""Post-Quantum Cryptography Readiness Lab.

A practical demonstration of PQC readiness using NIST PQC algorithms
(ML-KEM/Kyber and ML-DSA/Dilithium) via the Open Quantum Safe library.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from . import config
from . import lib

__all__ = ["__version__", "__author__", "__email__", "config", "lib"]
