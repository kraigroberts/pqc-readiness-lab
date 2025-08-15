"""Command-line interface for PQC Readiness Lab."""

import logging
import sys
from pathlib import Path

import click

from . import __version__, config, lib


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


@click.group()
@click.version_option(version=__version__, prog_name="pqc-lab")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', type=click.Path(exists=True), help='Configuration file path')
def main(verbose: bool, config: str | None = None) -> None:
    """Post-Quantum Cryptography Readiness Lab CLI.

    A practical demonstration of PQC readiness using NIST PQC algorithms.
    """
    setup_logging(verbose)

    if config:
        # TODO: Load configuration from file
        pass

    # Check liboqs availability
    if not lib.is_available():
        click.echo("Warning: liboqs library not available. PQC operations will not work.", err=True)


@main.command()
@click.option('--alg', 'algorithm',
              type=click.Choice(['mlkem512', 'mlkem768', 'mlkem1024', 'mldsa44', 'mldsa65', 'mldsa87']),
              default='mlkem768', help='Algorithm to benchmark')
@click.option('--count', type=int, default=100, help='Number of iterations')
@click.option('--output', type=click.Path(), help='Output file for results')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text', 'csv']),
              default='json', help='Output format')
def bench(algorithm: str, count: int, output: str | None, output_format: str) -> None:
    """Run benchmarks for PQC algorithms."""
    click.echo(f"Benchmarking {algorithm} with {count} iterations...")

    # TODO: Implement benchmarking logic
    click.echo("Benchmarking not yet implemented in milestone 1")

    # Placeholder result (not yet implemented)
    _ = {
        "algorithm": algorithm,
        "iterations": count,
        "format": output_format,
        "status": "not_implemented"
    }

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # TODO: Save results to file
        click.echo(f"Results would be saved to {output}")
    else:
        click.echo("Results would be displayed here")


@main.command()
@click.option('--alg', 'algorithm',
              type=click.Choice(['mldsa44', 'mldsa65', 'mldsa87']),
              default='mldsa65', help='Signature algorithm to use')
@click.option('--pub', 'public_key', type=click.Path(), required=True, help='Public key file')
@click.option('--priv', 'private_key', type=click.Path(), required=True, help='Private key file')
@click.option('--in', 'input_file', type=click.Path(exists=True), required=True, help='File to sign')
@click.option('--sig', 'signature_file', type=click.Path(), required=True, help='Output signature file')
def sign(algorithm: str, public_key: str, private_key: str, input_file: str, signature_file: str) -> None:
    """Sign a file using PQC signature algorithm."""
    click.echo(f"Signing {input_file} with {algorithm}...")

    # TODO: Implement signing logic
    click.echo("File signing not yet implemented in milestone 1")

    # Create signature file directory if needed
    sig_path = Path(signature_file)
    sig_path.parent.mkdir(parents=True, exist_ok=True)

    # Placeholder signature file
    sig_path.write_text(f"PLACEHOLDER_SIGNATURE_{algorithm}")
    click.echo(f"Placeholder signature saved to {signature_file}")


@main.command()
@click.option('--alg', 'algorithm',
              type=click.Choice(['mldsa44', 'mldsa65', 'mldsa87']),
              default='mldsa65', help='Signature algorithm to use')
@click.option('--pub', 'public_key', type=click.Path(exists=True), required=True, help='Public key file')
@click.option('--in', 'input_file', type=click.Path(exists=True), required=True, help='File to verify')
@click.option('--sig', 'signature_file', type=click.Path(exists=True), required=True, help='Signature file')
def verify(algorithm: str, public_key: str, input_file: str, signature_file: str) -> None:
    """Verify a file signature using PQC signature algorithm."""
    click.echo(f"Verifying {input_file} with {algorithm}...")

    # TODO: Implement verification logic
    click.echo("Signature verification not yet implemented in milestone 1")

    # Placeholder verification
    click.echo("Placeholder verification completed")


@main.command()
@click.option('--alg', 'algorithm',
              type=click.Choice(['mlkem512', 'mlkem768', 'mlkem1024']),
              default='mlkem768', help='KEM algorithm to use')
@click.option('--pub', 'public_key', type=click.Path(), help='Public key file')
@click.option('--priv', 'private_key', type=click.Path(), help='Private key file')
@click.option('--out', 'output_dir', type=click.Path(), default='artifacts', help='Output directory')
def keygen(algorithm: str, public_key: str | None, private_key: str | None, output_dir: str) -> None:
    """Generate keypair for PQC algorithm."""
    click.echo(f"Generating {algorithm} keypair...")

    # TODO: Implement key generation logic
    click.echo("Key generation not yet implemented in milestone 1")

    # Set default filenames if not provided
    if not public_key:
        public_key = f"{output_dir}/{algorithm}.pub"
    if not private_key:
        private_key = f"{output_dir}/{algorithm}.priv"

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Placeholder key files
    Path(public_key).write_text(f"PLACEHOLDER_PUBLIC_KEY_{algorithm}")
    Path(private_key).write_text(f"PLACEHOLDER_PRIVATE_KEY_{algorithm}")

    click.echo(f"Placeholder keys saved to {public_key} and {private_key}")


@main.group()
def handshake() -> None:
    """Perform PQC-based secure handshake."""
    pass


@handshake.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5555, help='Port to bind to')
@click.option('--alg', 'algorithm',
              type=click.Choice(['mlkem512', 'mlkem768', 'mlkem1024']),
              default='mlkem768', help='KEM algorithm to use')
def server(host: str, port: int, algorithm: str) -> None:
    """Start handshake server."""
    click.echo(f"Starting {algorithm} handshake server on {host}:{port}...")

    # TODO: Implement handshake server
    click.echo("Handshake server not yet implemented in milestone 1")
    click.echo("Server would listen for connections here")


@handshake.command()
@click.option('--host', default='127.0.0.1', help='Server host')
@click.option('--port', default=5555, help='Server port')
@click.option('--alg', 'algorithm',
              type=click.Choice(['mlkem512', 'mlkem768', 'mlkem1024']),
              default='mlkem768', help='KEM algorithm to use')
@click.option('--message', default='Hello PQC!', help='Message to send')
def client(host: str, port: int, algorithm: str, message: str) -> None:
    """Connect to handshake server."""
    click.echo(f"Connecting to {algorithm} handshake server at {host}:{port}...")

    # TODO: Implement handshake client
    click.echo("Handshake client not yet implemented in milestone 1")
    click.echo(f"Would send message: {message}")


@main.command()
def info() -> None:
    """Show system information and capabilities."""
    click.echo("PQC Readiness Lab System Information")
    click.echo("=" * 40)

    click.echo(f"Version: {__version__}")
    click.echo(f"liboqs available: {lib.is_available()}")

    if lib.is_available():
        click.echo(f"liboqs version: {lib.get_version()}")
        click.echo(f"Enabled features: {', '.join(lib.get_enabled_features())}")
        click.echo(f"Supported KEMs: {', '.join(lib.get_supported_kems())}")
        click.echo(f"Supported DSAs: {', '.join(lib.get_supported_sigs())}")
    else:
        click.echo("liboqs not available - PQC operations will not work")

    click.echo(f"Artifacts directory: {config.get_artifacts_dir()}")
    click.echo(f"Default KEM: {config.get_default_kem()}")
    click.echo(f"Default DSA: {config.get_default_dsa()}")


@main.command()
def list() -> None:
    """List supported algorithms and their details."""
    click.echo("Supported PQC Algorithms")
    click.echo("=" * 30)

    click.echo("\nKey Encapsulation Mechanisms (KEM):")
    for kem in lib.get_supported_kems():
        details = lib.get_kem_details(kem)
        if details:
            click.echo(f"  {kem}: NIST Level {details['claimed_nist_level']}")

    click.echo("\nDigital Signature Algorithms (DSA):")
    for dsa in lib.get_supported_sigs():
        details = lib.get_sig_details(dsa)
        if details:
            click.echo(f"  {dsa}: NIST Level {details['claimed_nist_level']}")


if __name__ == '__main__':
    main()
