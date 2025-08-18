## v0.1.0
-
## v0.1.1

- Bench: richer outputs (json/csv/text) with env metadata; default artifacts path
- CLI: add `show` quick demo
- Cleanup: ignore/remove egg-info; README fix (ML-DSA-65 references)
- CI: release workflow on tags

- Initial public release
- PQC ops via liboqs (ML-KEM keygen/encap/decap; ML-DSA keygen/sign/verify)
- CLI: bench, keygen, sign, verify, handshake server/client, list, info, show
- Handshake: TCP demo using KEM-derived ChaCha20-Poly1305 for a single message
- Benchmarks write to `artifacts/` by default (JSON/CSV/TXT)
- CI: build liboqs, lint, type-check, tests
- Dockerfile: builds liboqs, installs package

