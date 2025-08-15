# PQC Readiness Lab Architecture

## Overview

The PQC Readiness Lab is designed as a modular system that demonstrates practical Post-Quantum Cryptography readiness through several key components:

1. **C Language Demos** - Low-level examples using liboqs directly
2. **Python Harness** - High-level orchestration and CLI tools
3. **Test Suite** - Validation and benchmarking tools
4. **CI/CD Pipeline** - Automated build and testing

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Python CLI    │    │   Python Core   │    │   C Demos       │
│   (pqc-lab)    │◄──►│   (lib.py)      │◄──►│   (kem_demo)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Suite    │    │   Configuration │    │   liboqs        │
│   (pytest)      │    │   (config.py)   │    │   (C Library)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Details

### Python Package (`src/pqc_lab/`)

- **`cli.py`** - Command-line interface using Click
- **`lib.py`** - Thin wrapper around liboqs using ctypes
- **`config.py`** - Configuration management using Pydantic
- **`handshake.py`** - Network handshake implementation (Milestone 4)
- **`signing.py`** - File signing/verification (Milestone 3)
- **`bench.py`** - Benchmarking tools (Milestone 3)

### C Demos (`c/`)

- **`kem_demo/`** - KEM key generation, encapsulation, decapsulation
- **`dsa_demo/`** - DSA key generation, signing, verification
- **`CMakeLists.txt`** - Build configuration

### Test Suite (`tests/`)

- **`test_smoke.py`** - Basic package import and configuration tests
- **`test_kem_dsa.py`** - KEM and DSA functionality tests (Milestone 2)
- **`test_handshake.py`** - Network handshake tests (Milestone 4)
- **`test_bench.py`** - Benchmark validation tests (Milestone 3)

## Key Workflows

### 1. KEM-Based Key Exchange

```
Client                                    Server
  │                                         │
  │ 1. Generate KEM keypair                 │
  │    (public_key, private_key)            │
  │                                         │
  │ 2. Send public_key ────────────────────►│
  │                                         │
  │ 3. Server generates shared secret       │
  │    using KEM encapsulation              │
  │                                         │
  │ 4. Server sends ciphertext ◄────────────│
  │                                         │
  │ 5. Client derives same shared secret    │
  │    using KEM decapsulation              │
  │                                         │
  │ 6. Both parties now have shared secret  │
  │    for symmetric encryption             │
```

### 2. File Signing & Verification

```
Signing Process:
1. Generate DSA keypair (public_key, private_key)
2. Hash the file content
3. Sign the hash with private_key
4. Save signature to file

Verification Process:
1. Load public_key and signature
2. Hash the file content
3. Verify signature against hash using public_key
4. Return verification result
```

### 3. Benchmarking

```
1. Load algorithm configuration
2. Perform warmup iterations
3. Time key generation operations
4. Time encryption/decryption operations
5. Measure memory usage and key sizes
6. Generate structured output (JSON/CSV)
7. Save results to artifacts directory
```

## Security Considerations

### Algorithm Selection

- **KEM**: ML-KEM-768 (recommended) provides 192-bit security
- **DSA**: ML-DSA-65 (recommended) provides 192-bit security
- All algorithms are NIST PQC standardization candidates

### Key Management

- **Key Generation**: Uses cryptographically secure random number generation
- **Key Storage**: Keys are stored in plaintext for demo purposes
- **Production Note**: Real systems require secure key storage and PKI

### Network Security

- **Handshake**: Demonstrates KEM-based key exchange
- **Transport**: Uses AEAD encryption (ChaCha20-Poly1305) for messages
- **Authentication**: Server authentication through public key verification

## Migration Path

### Phase 1: Algorithm Integration
- Integrate PQC algorithms alongside existing classical algorithms
- Implement hybrid approach (PQC + classical) for backward compatibility

### Phase 2: Key Management
- Implement proper PKI for PQC keys
- Establish key rotation and lifecycle management
- Add hybrid certificate support

### Phase 3: Protocol Integration
- Integrate with TLS 1.3 for PQC support
- Implement PQC-aware certificate validation
- Add PQC algorithm negotiation

### Phase 4: Production Deployment
- Performance optimization and tuning
- Security audit and validation
- Compliance and certification

## Performance Characteristics

### Expected Performance (ML-KEM-768)
- **Key Generation**: ~100-500 μs
- **Encapsulation**: ~50-200 μs  
- **Decapsulation**: ~100-300 μs
- **Public Key Size**: ~1,184 bytes
- **Ciphertext Size**: ~1,088 bytes

### Expected Performance (ML-DSA-65)
- **Key Generation**: ~200-800 μs
- **Signing**: ~100-400 μs
- **Verification**: ~200-600 μs
- **Public Key Size**: ~1,952 bytes
- **Signature Size**: ~3,366 bytes

## Dependencies

### System Dependencies
- **Build Tools**: CMake 3.16+, Make, GCC/Clang
- **Libraries**: OpenSSL 1.1.1+ or 3.0+
- **Python**: 3.10+

### Python Dependencies
- **Core**: cryptography, pydantic, click, rich
- **Development**: pytest, mypy, ruff, black
- **Optional**: cffi for enhanced liboqs integration

## Build Process

### Native Build
1. Install system dependencies
2. Run `./scripts/build_liboqs.sh` to build liboqs
3. Install Python package with `pip install -e .`
4. Build C demos with CMake

### Docker Build
1. Build multi-stage Docker image
2. Stage 1: Build liboqs from source
3. Stage 2: Create Python runtime with liboqs
4. Run container with `docker run pqc-lab`

## Testing Strategy

### Unit Tests
- Package import and configuration
- Algorithm parameter validation
- Error handling and edge cases

### Integration Tests
- End-to-end KEM operations
- File signing and verification
- Network handshake scenarios

### Performance Tests
- Algorithm benchmarking
- Memory usage profiling
- Scalability testing

### Security Tests
- Cryptographic validation
- Key generation quality
- Random number generation

## Future Enhancements

### Algorithm Support
- Additional NIST PQC candidates
- Custom algorithm implementations
- Performance optimizations

### Protocol Support
- TLS 1.3 PQC integration
- SSH PQC key support
- Certificate transparency

### Tooling
- Key management utilities
- Performance analysis tools
- Security validation suite

---

*This architecture document will be updated as the project evolves through its milestones.*
