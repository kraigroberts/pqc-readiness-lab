## v0.1.0

- Initial public release
- PQC ops via liboqs (ML-KEM keygen/encap/decap; ML-DSA keygen/sign/verify)
- CLI: bench, keygen, sign, verify, handshake server/client, list, info, show
- Handshake: TCP demo using KEM-derived ChaCha20-Poly1305 for a single message
- Benchmarks write to `artifacts/` by default (JSON/CSV/TXT)
- CI: build liboqs, lint, type-check, tests
- Dockerfile: builds liboqs, installs package

