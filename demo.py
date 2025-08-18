#!/usr/bin/env python3
"""
from __future__ import annotations
PQC Readiness Lab Demo Script

This script demonstrates the Post-Quantum Cryptography capabilities
in an impressive, show-ready format.
"""

import time
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pqc_lab import lib, config
from pqc_lab import __version__


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str) -> None:
    """Print a formatted section."""
    print(f"\n{title}")
    print("-" * len(title))


def demo_system_info() -> None:
    """Demonstrate system information."""
    print_header("PQC Readiness Lab - System Information")
    
    print(f"Version: {__version__}")
    print(f"liboqs Available: {'✅ Yes' if lib.is_available() else '❌ No'}")
    
    if lib.is_available():
        print(f"liboqs Version: {lib.get_version()}")
        print(f"Enabled Features: {', '.join(lib.get_enabled_features())}")
        
        kems = lib.get_supported_kems()
        dsas = lib.get_supported_sigs()
        
        print(f"\nSupported KEMs: {len(kems)} algorithms")
        for kem in kems:
            details = lib.get_kem_details(kem)
            if details:
                print(f"  • {kem}: NIST Level {details['claimed_nist_level']}")
        
        print(f"\nSupported DSAs: {len(dsas)} algorithms")
        for dsa in dsas:
            details = lib.get_sig_details(dsa)
            if details:
                print(f"  • {dsa}: NIST Level {details['claimed_nist_level']}")
    else:
        print("⚠️  liboqs not available - PQC operations will not work")


def demo_key_generation() -> None:
    """Demonstrate key generation."""
    if not lib.is_available():
        print("⚠️  Skipping key generation demo - liboqs not available")
        return
    
    print_header("Key Generation Demo")
    
    # Test KEM key generation
    print_section("ML-KEM-768 Key Generation")
    start_time = time.time()
    keypair = lib.generate_keypair("mlkem768")
    if keypair:
        public_key, secret_key = keypair
        keygen_time = time.time() - start_time
        
        print(f"✅ Keypair generated in {keygen_time:.6f} seconds")
        print(f"Public Key: {len(public_key)} bytes")
        print(f"Secret Key: {len(secret_key)} bytes")
        
        # Test encapsulation/decapsulation
        print_section("Key Encapsulation Test")
        start = time.time()
        result = lib.encapsulate_key("mlkem768", public_key)
        if result:
            ciphertext, shared_secret = result
            encaps_time = time.time() - start
            
            print(f"✅ Key encapsulated in {encaps_time:.6f} seconds")
            print(f"Ciphertext: {len(ciphertext)} bytes")
            print(f"Shared Secret: {len(shared_secret)} bytes")
            
            # Test decapsulation
            start = time.time()
            decaps_secret = lib.decapsulate_key("mlkem768", ciphertext, secret_key)
            if decaps_secret:
                decaps_time = time.time() - start
                print(f"✅ Key decapsulated in {decaps_time:.6f} seconds")
                
                # Verify shared secrets match
                if shared_secret == decaps_secret:
                    print("✅ Shared secrets match perfectly!")
                else:
                    print("❌ Shared secrets do not match!")
            else:
                print("❌ Key decapsulation failed")
        else:
            print("❌ Key encapsulation failed")
    else:
        print("❌ Keypair generation failed")
    
    # Test DSA key generation
    print_section("ML-DSA-65 Key Generation")
    start_time = time.time()
    keypair = lib.generate_keypair("mldsa65")
    if keypair:
        public_key, secret_key = keypair
        keygen_time = time.time() - start_time
        
        print(f"✅ Keypair generated in {keygen_time:.6f} seconds")
        print(f"Public Key: {len(public_key)} bytes")
        print(f"Secret Key: {len(secret_key)} bytes")
        
        # Test signing/verification
        print_section("Digital Signature Test")
        message = b"Hello, Post-Quantum World! This is a test message for signing."
        
        start = time.time()
        signature = lib.sign_message("mldsa65", message, secret_key)
        if signature:
            sign_time = time.time() - start
            print(f"✅ Message signed in {sign_time:.6f} seconds")
            print(f"Message: {len(message)} bytes")
            print(f"Signature: {len(signature)} bytes")
            
            # Test verification
            start = time.time()
            if lib.verify_signature("mldsa65", message, signature, public_key):
                verify_time = time.time() - start
                print(f"✅ Signature verified in {verify_time:.6f} seconds")
                print("✅ Digital signature is valid!")
            else:
                print("❌ Signature verification failed")
        else:
            print("❌ Message signing failed")
    else:
        print("❌ DSA keypair generation failed")


def demo_performance() -> None:
    """Demonstrate performance benchmarks."""
    if not lib.is_available():
        print("⚠️  Skipping performance demo - liboqs not available")
        return
    
    print_header("Performance Benchmark Demo")
    
    # KEM performance
    print_section("ML-KEM-768 Performance (100 iterations)")
    
    # Generate keypair once
    keypair = lib.generate_keypair("mlkem768")
    if not keypair:
        print("❌ Cannot run KEM benchmark - key generation failed")
        return
    
    public_key, secret_key = keypair
    
    # Benchmark encapsulation
    encaps_times = []
    for i in range(100):
        start = time.time()
        result = lib.encapsulate_key("mlkem768", public_key)
        if result:
            encaps_times.append(time.time() - start)
    
    if encaps_times:
        avg_encaps = sum(encaps_times) / len(encaps_times)
        min_encaps = min(encaps_times)
        max_encaps = max(encaps_times)
        
        print(f"Encapsulation (100 iterations):")
        print(f"  Average: {avg_encaps:.6f} seconds")
        print(f"  Minimum: {min_encaps:.6f} seconds")
        print(f"  Maximum: {max_encaps:.6f} seconds")
        print(f"  Throughput: {1/avg_encaps:.1f} ops/second")
    
    # Benchmark decapsulation
    decaps_times = []
    result = lib.encapsulate_key("mlkem768", public_key)
    if result:
        ciphertext, _ = result
        for i in range(100):
            start = time.time()
            lib.decapsulate_key("mlkem768", ciphertext, secret_key)
            decaps_times.append(time.time() - start)
        
        if decaps_times:
            avg_decaps = sum(decaps_times) / len(decaps_times)
            min_decaps = min(decaps_times)
            max_decaps = max(decaps_times)
            
            print(f"\nDecapsulation (100 iterations):")
            print(f"  Average: {avg_decaps:.6f} seconds")
            print(f"  Minimum: {min_decaps:.6f} seconds")
            print(f"  Maximum: {max_decaps:.6f} seconds")
            print(f"  Throughput: {1/avg_decaps:.1f} ops/second")
    
    # DSA performance
    print_section("ML-DSA-65 Performance (100 iterations)")
    
    # Generate keypair once
    keypair = lib.generate_keypair("mldsa65")
    if not keypair:
        print("❌ Cannot run DSA benchmark - key generation failed")
        return
    
    public_key, secret_key = keypair
    message = b"Benchmark message for PQC signature testing"
    
    # Benchmark signing
    sign_times = []
    for i in range(100):
        start = time.time()
        signature = lib.sign_message("mldsa65", message, secret_key)
        if signature:
            sign_times.append(time.time() - start)
    
    if sign_times:
        avg_sign = sum(sign_times) / len(sign_times)
        min_sign = min(sign_times)
        max_sign = max(sign_times)
        
        print(f"Signing (100 iterations):")
        print(f"  Average: {avg_sign:.6f} seconds")
        print(f"  Minimum: {min_sign:.6f} seconds")
        print(f"  Maximum: {max_sign:.6f} seconds")
        print(f"  Throughput: {1/avg_sign:.1f} ops/second")
    
    # Benchmark verification
    verify_times = []
    signature = lib.sign_message("mldsa65", message, secret_key)
    if signature:
        for i in range(100):
            start = time.time()
            lib.verify_signature("mldsa65", message, signature, public_key)
            verify_times.append(time.time() - start)
        
        if verify_times:
            avg_verify = sum(verify_times) / len(verify_times)
            min_verify = min(verify_times)
            max_verify = max(verify_times)
            
            print(f"\nVerification (100 iterations):")
            print(f"  Average: {avg_verify:.6f} seconds")
            print(f"  Minimum: {min_verify:.6f} seconds")
            print(f"  Maximum: {max_verify:.6f} seconds")
            print(f"  Throughput: {1/avg_verify:.1f} ops/second")


def main() -> None:
    """Run the PQC demo."""
    print("🚀 PQC Readiness Lab - Interactive Demo")
    print("Demonstrating Post-Quantum Cryptography capabilities")
    
    try:
        demo_system_info()
        demo_key_generation()
        demo_performance()
        
        print_header("Demo Complete!")
        print("✅ All demonstrations completed successfully!")
        print("\nNext steps:")
        print("  • Run 'pqc-lab --help' to see available commands")
        print("  • Try 'pqc-lab bench --alg mlkem768 --count 100' for benchmarks")
        print("  • Use 'pqc-lab keygen --alg mldsa65' to generate keys")
        print("  • Sign files with 'pqc-lab sign --in file.txt --pub key.pub --priv key.priv --sig file.sig'")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
