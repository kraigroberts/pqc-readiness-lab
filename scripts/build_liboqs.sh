#!/bin/bash

# Build script for Open Quantum Safe (liboqs) library
# This script clones and builds liboqs from source
# OPTIMIZED: Only builds ML-KEM-768 (Kyber) and ML-DSA-65 (Dilithium) for faster CI builds

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LIBOQS_VERSION="main"
BUILD_TYPE="Release"
BUILD_DIR="build"
INSTALL_PREFIX="/usr/local"
PARALLEL_JOBS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking build dependencies..."
    
    local missing_deps=()
    
    # Check for required commands
    for cmd in git cmake make; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    # Check for required packages (Ubuntu/Debian)
    if command -v dpkg &> /dev/null; then
        for pkg in build-essential libssl-dev pkg-config; do
            if ! dpkg -l | grep -q "^ii.*$pkg"; then
                missing_deps+=("$pkg")
            fi
        done
    fi
    
    # Check for required packages (macOS)
    if command -v brew &> /dev/null; then
        for pkg in openssl pkg-config; do
            if ! brew list | grep -q "^$pkg$"; then
                missing_deps+=("$pkg")
            fi
        done
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install missing dependencies and try again:"
        log_info "Ubuntu/Debian: sudo apt-get install build-essential cmake git libssl-dev pkg-config"
        log_info "macOS: brew install cmake git openssl pkg-config"
        exit 1
    fi
    
    log_success "All dependencies satisfied"
}

cleanup() {
    log_info "Cleaning up..."
    if [ -d "liboqs" ]; then
        rm -rf liboqs
    fi
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
    fi
}

clone_liboqs() {
    log_info "Cloning liboqs repository..."
    
    if [ -d "liboqs" ]; then
        log_warning "liboqs directory already exists, removing..."
        rm -rf liboqs
    fi
    
    git clone --depth 1 --branch "$LIBOQS_VERSION" https://github.com/open-quantum-safe/liboqs.git
    log_success "liboqs repository cloned successfully"
}

build_liboqs() {
    log_info "Building liboqs with only required algorithms (ML-KEM-768, ML-DSA-65)..."
    
    cd liboqs
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    cd "$BUILD_DIR"
    
    # Configure with CMake - only build the specific algorithms we need
    log_info "Configuring with CMake (optimized for ML-KEM-768 and ML-DSA-65)..."
    cmake .. \
        -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
        -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" \
        -DOQS_USE_OPENSSL=ON \
        -DOQS_BUILD_ONLY_LIB=ON \
        -DOQS_DIST_BUILD=ON \
        -DOQS_OPT_TARGET=generic \
        -DBUILD_SHARED_LIBS=ON \
        -DOQS_ENABLE_KEM_KYBER=ON \
        -DOQS_ENABLE_SIG_DILITHIUM=ON \
        -DOQS_ENABLE_KEM_KYBER_512=OFF \
        -DOQS_ENABLE_KEM_KYBER_768=ON \
        -DOQS_ENABLE_KEM_KYBER_1024=OFF \
        -DOQS_ENABLE_SIG_DILITHIUM_2=OFF \
        -DOQS_ENABLE_SIG_DILITHIUM_3=ON \
        -DOQS_ENABLE_SIG_DILITHIUM_5=OFF \
        -DOQS_ENABLE_KEM_CLASSIC_MCELIECE=OFF \
        -DOQS_ENABLE_KEM_HQC=OFF \
        -DOQS_ENABLE_KEM_BIKE=OFF \
        -DOQS_ENABLE_KEM_FRODO=OFF \
        -DOQS_ENABLE_KEM_SABER=OFF \
        -DOQS_ENABLE_KEM_NTRU=OFF \
        -DOQS_ENABLE_KEM_SIKE=OFF \
        -DOQS_ENABLE_SIG_FALCON=OFF \
        -DOQS_ENABLE_SIG_SPHINCS=OFF \
        -DOQS_ENABLE_SIG_RAINBOW=OFF \
        -DOQS_ENABLE_SIG_PICNIC=OFF \
        -DOQS_ENABLE_SIG_QTESLA=OFF \
        -DOQS_ENABLE_SIG_GEMMS=OFF \
        -DOQS_ENABLE_SIG_LEDACRYPT=OFF \
        -DOQS_ENABLE_SIG_ED25519=OFF \
        -DOQS_ENABLE_SIG_ECDSA=OFF \
        -DOQS_ENABLE_SIG_RSA=OFF
    
    # Build
    log_info "Building with $PARALLEL_JOBS parallel jobs..."
    make -j"$PARALLEL_JOBS"
    
    # Install
    log_info "Installing liboqs..."
    sudo make install
    
    # Update library cache
    if command -v ldconfig &> /dev/null; then
        log_info "Updating library cache..."
        sudo ldconfig
    fi
    
    cd ../..
    log_success "liboqs built and installed successfully (optimized build)"
}

verify_installation() {
    log_info "Verifying installation..."
    
    # Check if library files exist
    local lib_paths=(
        "$INSTALL_PREFIX/lib/liboqs.so"
        "$INSTALL_PREFIX/lib/liboqs.dylib"
        "$INSTALL_PREFIX/lib64/liboqs.so"
    )
    
    local lib_found=false
    for lib_path in "${lib_paths[@]}"; do
        if [ -f "$lib_path" ]; then
            log_success "Found liboqs library at: $lib_path"
            lib_found=true
            break
        fi
    done
    
    if [ "$lib_found" = false ]; then
        log_error "liboqs library not found in expected locations"
        exit 1
    fi
    
    # Check if headers exist
    if [ -d "$INSTALL_PREFIX/include/oqs" ]; then
        log_success "Found liboqs headers at: $INSTALL_PREFIX/include/oqs"
    else
        log_error "liboqs headers not found at: $INSTALL_PREFIX/include/oqs"
        exit 1
    fi
    
    # Test library loading
    log_info "Testing library loading..."
    if python3 -c "import ctypes; ctypes.CDLL('$INSTALL_PREFIX/lib/liboqs.so')" 2>/dev/null; then
        log_success "Library can be loaded successfully"
    else
        log_warning "Library loading test failed (this may be normal on some systems)"
    fi
}

main() {
    log_info "Starting liboqs build process..."
    log_info "Build type: $BUILD_TYPE"
    log_info "Install prefix: $INSTALL_PREFIX"
    log_info "Parallel jobs: $PARALLEL_JOBS"
    
    # Set up error handling
    trap cleanup EXIT
    
    # Check dependencies
    check_dependencies
    
    # Clone repository
    clone_liboqs
    
    # Build and install
    build_liboqs
    
    # Verify installation
    verify_installation
    
    log_success "liboqs build completed successfully!"
    log_info "Library installed to: $INSTALL_PREFIX"
    log_info "Headers installed to: $INSTALL_PREFIX/include/oqs"
    
    # Remove trap
    trap - EXIT
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            LIBOQS_VERSION="$2"
            shift 2
            ;;
        --build-type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        --prefix)
            INSTALL_PREFIX="$2"
            shift 2
            ;;
        --jobs)
            PARALLEL_JOBS="$2"
            shift 2
            ;;
        --clean)
            cleanup
            exit 0
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --version VERSION    liboqs version to build (default: main)"
            echo "  --build-type TYPE    CMake build type (default: Release)"
            echo "  --prefix PATH        Installation prefix (default: /usr/local)"
            echo "  --jobs N             Number of parallel jobs (default: auto)"
            echo "  --clean              Clean build artifacts and exit"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
