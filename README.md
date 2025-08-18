### PQC Readiness Lab

Production-quality skeleton to demonstrate NIST PQC readiness using `liboqs` with a Python CLI.

### Quickstart (native)
```bash
python3.10 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
sudo apt-get update && sudo apt-get install -y build-essential cmake git libssl-dev
bash scripts/build_liboqs.sh
pqc-lab info
```

### Quickstart (Docker)
```bash
docker build -t pqc-lab .
docker run --rm pqc-lab
```

### What works now
- CLI `pqc-lab info` prints JSON with version and defaults
- CI builds `liboqs`, installs deps, runs lint, type-check, and tests

Next milestones will add KEM/DSA operations, handshake, and signing flows.
