### Architecture Overview

Minimal milestone skeleton:
- `pqc_lab` Python package with CLI
- CI that builds liboqs, lints, type-checks, and tests
- Docker image that builds liboqs and runs the CLI

Planned additions:
- KEM/DSA bindings via liboqs
- TCP handshake deriving a shared secret using ML-KEM
- File signing and verification using ML-DSA

Handshake sketch:
```
Client                         Server
  |------ send KEM pk --------->|
  |<--- ct = Encaps(pk), ss ----|
  |--- Decaps(sk, ct) => ss --->|
  |   AEAD(ss, "hello pqc")     |
```

