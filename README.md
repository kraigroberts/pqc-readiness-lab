# PQC Readiness Lab

A practical demonstration of Post-Quantum Cryptography readiness using NIST PQC algorithms (ML-KEM/Kyber and ML-DSA/Dilithium) via the Open Quantum Safe library.

## 🎯 Mission

Demonstrate hands-on ability to transition products/systems to NIST PQC by implementing:
- **Key Encapsulation Mechanisms (KEM)**: ML-KEM-768 for secure key exchange
- **Digital Signature Algorithms (DSA)**: ML-DSA-3 for artifact integrity
- **Practical Applications**: Client/server handshake, file signing/verification
- **Performance Analysis**: Benchmarks and validation tools

## 🚀 Quickstart

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/pqc-readiness-lab.git
cd pqc-readiness-lab

# Build and run with Docker
docker build -t pqc-lab .
docker run --rm pqc-lab pqc-lab --help
```

### Option 2: Native Build

#### Prerequisites
- **Ubuntu/Debian**: `sudo apt-get install build-essential cmake git python3.10 python3.10-dev python3.10-venv`
- **macOS**: `brew install cmake git python@3.10`
- **Python**: 3.10+ with pip

#### Build Steps
```bash
# Clone and setup
git clone https://github.com/yourusername/pqc-readiness-lab.git
cd pqc-readiness-lab

# Create virtual environment
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build liboqs (this may take 5-10 minutes)
./scripts/build_liboqs.sh

# Install the package
pip install -e .

# Verify installation
pqc-lab --help
```

## 📚 Usage Examples

### Benchmarks
```bash
# Run KEM benchmarks
pqc-lab bench --alg mlkem768 --count 100

# Run signature benchmarks  
pqc-lab bench --alg mldsa3 --count 100
```

### File Signing & Verification
```bash
# Generate keypair
pqc-lab keygen --alg mldsa3 --pub artifacts/dsa.pub --priv artifacts/dsa.priv

# Sign a file
pqc-lab sign --in README.md --sig artifacts/README.md.sig --pub artifacts/dsa.pub --priv artifacts/dsa.priv

# Verify signature
pqc-lab verify --in README.md --sig artifacts/README.md.sig --pub artifacts/dsa.pub
```

### Secure Handshake
```bash
# Terminal 1: Start server
pqc-lab handshake server --host 127.0.0.1 --port 5555

# Terminal 2: Connect client
pqc-lab handshake client --host 127.0.0.1 --port 5555 --message "Hello PQC!"
```

## 🏗️ Architecture

The lab consists of several components:

- **C Demos**: Low-level examples using liboqs directly
- **Python Harness**: High-level orchestration and CLI tools
- **Test Suite**: Validation and benchmarking tools
- **CI/CD**: Automated build and testing pipeline

See [docs/arch.md](docs/arch.md) for detailed architecture diagrams and migration guidance.

## 🔧 Development

### Project Structure
```
pqc-readiness-lab/
├── c/                    # C language demos
├── src/pqc_lab/         # Python package
├── tests/               # Test suite
├── scripts/             # Build scripts
├── docs/                # Documentation
└── .github/workflows/   # CI/CD
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/pqc_lab

# Linting and type checking
ruff check src/ tests/
mypy src/ tests/
```

### Building C Components
```bash
# Build C demos
mkdir build && cd build
cmake ..
make

# Run C demos
./kem_demo
./dsa_demo
```

## 📊 Supported Algorithms

| Type | Algorithm | Security Level | Use Case |
|------|-----------|----------------|----------|
| KEM | ML-KEM-512 | 128-bit | Key exchange (lightweight) |
| KEM | ML-KEM-768 | 192-bit | Key exchange (recommended) |
| KEM | ML-KEM-1024 | 256-bit | Key exchange (high security) |
| DSA | ML-DSA-44 | 128-bit | Signatures (lightweight) |
| DSA | ML-DSA-65 | 192-bit | Signatures (recommended) |
| DSA | ML-DSA-87 | 256-bit | Signatures (high security) |

## 🚨 Security Notes

- **Research Use**: This is a demonstration project, not production-ready
- **Algorithm Selection**: Uses NIST PQC standardization candidates
- **Key Management**: Demonstrates basic concepts; production systems require proper PKI
- **Hybrid Approach**: Consider combining PQC with classical algorithms during transition

## 📈 Performance

Benchmark results are saved to `artifacts/bench_<date>.json` and include:
- Operations per second
- Median latency
- Key and ciphertext sizes
- Memory usage patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Open Quantum Safe](https://openquantumsafe.org/) for the liboqs library
- NIST for PQC standardization efforts
- The quantum-resistant cryptography community

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Check the [documentation](docs/)
- Review the [architecture guide](docs/arch.md)

---

**Ready to explore the quantum-resistant future? Start with `pqc-lab --help`!**
