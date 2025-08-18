"""Command-line interface for PQC Readiness Lab."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from . import __version__, config, lib
from .handshake import HandshakeParams, run_client, run_server


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@click.group()
@click.version_option(version=__version__, prog_name="pqc-lab")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", type=click.Path(exists=True), help="Configuration file path")
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
        click.echo(
            "Warning: liboqs library not available. PQC operations will not work.",
            err=True,
        )


@main.command()
@click.option(
    "--alg",
    "algorithm",
    type=click.Choice(
        ["mlkem512", "mlkem768", "mlkem1024", "mldsa44", "mldsa65", "mldsa87"]
    ),
    default="mlkem768",
    help="Algorithm to benchmark",
)
@click.option("--count", type=int, default=100, help="Number of iterations")
@click.option("--output", type=click.Path(), help="Output file for results")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["json", "text", "csv"]),
    default="json",
    help="Output format",
)
def bench(algorithm: str, count: int, output: str | None, output_format: str) -> None:
    """Run simple benchmarks for PQC algorithms."""
    import json as _json
    import time as _time

    if not lib.is_available():
        click.echo("liboqs not available; cannot run benchmarks", err=True)
        return

    import platform as _platform
    results: dict[str, object] = {
        "algorithm": algorithm,
        "iterations": int(count),
        "env": {
            "python": _platform.python_version(),
            "platform": _platform.platform(),
            "liboqs_version": lib.get_version() if lib.is_available() else "unknown",
        },
    }

    if algorithm.startswith("mlkem"):
        keypair = lib.generate_keypair(algorithm)
        if not keypair:
            click.echo("failed to generate kem keypair", err=True)
            return
        pk, sk = keypair
        enc_times: list[float] = []
        dec_times: list[float] = []
        for _ in range(count):
            t0 = _time.perf_counter()
            enc = lib.encapsulate_key(algorithm, pk)
            t1 = _time.perf_counter()
            if not enc:
                click.echo("encapsulate failed", err=True)
                return
            ct, _ss = enc
            enc_times.append(t1 - t0)
            t2 = _time.perf_counter()
            ss2 = lib.decapsulate_key(algorithm, ct, sk)
            t3 = _time.perf_counter()
            if ss2 is None:
                click.echo("decapsulate failed", err=True)
                return
            dec_times.append(t3 - t2)
        results.update({
            "avg_encapsulation": sum(enc_times) / len(enc_times),
            "avg_decapsulation": sum(dec_times) / len(dec_times),
        })
    else:
        keypair = lib.generate_keypair(algorithm)
        if not keypair:
            click.echo("failed to generate sig keypair", err=True)
            return
        pk, sk = keypair
        msg = b"benchmark message"
        sign_times: list[float] = []
        verify_times: list[float] = []
        for _ in range(count):
            t0 = _time.perf_counter()
            sig = lib.sign_message(algorithm, msg, sk)
            t1 = _time.perf_counter()
            if not sig:
                click.echo("sign failed", err=True)
                return
            sign_times.append(t1 - t0)
            t2 = _time.perf_counter()
            ok = lib.verify_signature(algorithm, msg, sig, pk)
            t3 = _time.perf_counter()
            if not ok:
                click.echo("verify failed", err=True)
                return
            verify_times.append(t3 - t2)
        results.update({
            "avg_signing": sum(sign_times) / len(sign_times),
            "avg_verification": sum(verify_times) / len(verify_times),
        })

    # Render output
    if output_format == "json":
        rendered = _json.dumps(results)
        default_ext = ".json"
    elif output_format == "csv":
        if algorithm.startswith("mlkem"):
            rendered = (
                "algorithm,iterations,avg_encapsulation,avg_decapsulation\n"
                f"{algorithm},{count},{results['avg_encapsulation']:.6f},{results['avg_decapsulation']:.6f}"
            )
        else:
            rendered = (
                "algorithm,iterations,avg_signing,avg_verification\n"
                f"{algorithm},{count},{results['avg_signing']:.6f},{results['avg_verification']:.6f}"
            )
        default_ext = ".csv"
    else:
        if algorithm.startswith("mlkem"):
            rendered = (
                f"KEM {algorithm}: {count} iters\n"
                f"  avg encaps: {results['avg_encapsulation']:.6f}s\n"
                f"  avg decaps: {results['avg_decapsulation']:.6f}s\n"
            )
        else:
            rendered = (
                f"DSA {algorithm}: {count} iters\n"
                f"  avg sign:   {results['avg_signing']:.6f}s\n"
                f"  avg verify: {results['avg_verification']:.6f}s\n"
            )
        default_ext = ".txt"

    # Save to file
    if output:
        p = Path(output)
    else:
        artifacts = config.get_artifacts_dir()
        artifacts.mkdir(parents=True, exist_ok=True)
        import datetime as _dt

        stamp = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        p = artifacts / f"bench_{algorithm}_{stamp}{default_ext}"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(rendered)
    click.echo(rendered)


@main.command()
@click.option("--kem", default="mlkem768", type=click.Choice(["mlkem512", "mlkem768", "mlkem1024"]))
@click.option("--dsa", default="mldsa65", type=click.Choice(["mldsa44", "mldsa65", "mldsa87"]))
def show(kem: str, dsa: str) -> None:
    """Quick demo: one KEM roundtrip and one DSA sign/verify."""
    import time as _time
    if not lib.is_available():
        click.echo("liboqs not available")
        return
    # KEM
    kp = lib.generate_keypair(kem)
    if not kp:
        click.echo("kem keygen failed")
        return
    pk, sk = kp
    t0 = _time.perf_counter()
    enc = lib.encapsulate_key(kem, pk)
    t1 = _time.perf_counter()
    if not enc:
        click.echo("kem encaps failed")
        return
    ct, ss = enc
    t2 = _time.perf_counter()
    ss2 = lib.decapsulate_key(kem, ct, sk)
    t3 = _time.perf_counter()
    if not ss2:
        click.echo("kem decaps failed")
        return
    # DSA
    kp2 = lib.generate_keypair(dsa)
    if not kp2:
        click.echo("dsa keygen failed")
        return
    pk2, sk2 = kp2
    msg = b"hello pqc"
    t4 = _time.perf_counter()
    sig = lib.sign_message(dsa, msg, sk2)
    t5 = _time.perf_counter()
    if not sig:
        click.echo("sign failed")
        return
    t6 = _time.perf_counter()
    ok = lib.verify_signature(dsa, msg, sig, pk2)
    t7 = _time.perf_counter()
    if not ok:
        click.echo("verify failed")
        return
    click.echo(
        f"KEM {kem}: encaps {t1-t0:.6f}s, decaps {t3-t2:.6f}s\n"
        f"DSA {dsa}: sign {t5-t4:.6f}s, verify {t7-t6:.6f}s"
    )


@main.command()
@click.option(
    "--alg",
    "algorithm",
    type=click.Choice(["mldsa44", "mldsa65", "mldsa87"]),
    default="mldsa65",
    help="Signature algorithm to use",
)
@click.option(
    "--pub", "public_key", type=click.Path(), required=True, help="Public key file"
)
@click.option(
    "--priv", "private_key", type=click.Path(), required=True, help="Private key file"
)
@click.option(
    "--in",
    "input_file",
    type=click.Path(exists=True),
    required=True,
    help="File to sign",
)
@click.option(
    "--sig",
    "signature_file",
    type=click.Path(),
    required=True,
    help="Output signature file",
)
def sign(
    algorithm: str,
    public_key: str,
    private_key: str,
    input_file: str,
    signature_file: str,
) -> None:
    """Sign a file using PQC signature algorithm."""
    if not lib.is_available():
        click.echo("liboqs not available; cannot sign", err=True)
        return
    data = Path(input_file).read_bytes()
    priv = Path(private_key).read_bytes()
    sig = lib.sign_message(algorithm, data, priv)
    if not sig:
        click.echo("sign failed", err=True)
        return
    Path(signature_file).parent.mkdir(parents=True, exist_ok=True)
    Path(signature_file).write_bytes(sig)
    click.echo(f"signature written: {signature_file}")


@main.command()
@click.option(
    "--alg",
    "algorithm",
    type=click.Choice(["mldsa44", "mldsa65", "mldsa87"]),
    default="mldsa65",
    help="Signature algorithm to use",
)
@click.option(
    "--pub",
    "public_key",
    type=click.Path(exists=True),
    required=True,
    help="Public key file",
)
@click.option(
    "--in",
    "input_file",
    type=click.Path(exists=True),
    required=True,
    help="File to verify",
)
@click.option(
    "--sig",
    "signature_file",
    type=click.Path(exists=True),
    required=True,
    help="Signature file",
)
def verify(
    algorithm: str, public_key: str, input_file: str, signature_file: str
) -> None:
    """Verify a file signature using PQC signature algorithm."""
    if not lib.is_available():
        click.echo("liboqs not available; cannot verify", err=True)
        return
    data = Path(input_file).read_bytes()
    pub = Path(public_key).read_bytes()
    sig = Path(signature_file).read_bytes()
    ok = lib.verify_signature(algorithm, data, sig, pub)
    click.echo("OK" if ok else "FAIL")


@main.command()
@click.option(
    "--alg",
    "algorithm",
    type=click.Choice(["mlkem512", "mlkem768", "mlkem1024"]),
    default="mlkem768",
    help="KEM algorithm to use",
)
@click.option("--pub", "public_key", type=click.Path(), help="Public key file")
@click.option("--priv", "private_key", type=click.Path(), help="Private key file")
@click.option(
    "--out",
    "output_dir",
    type=click.Path(),
    default="artifacts",
    help="Output directory",
)
def keygen(
    algorithm: str, public_key: str | None, private_key: str | None, output_dir: str
) -> None:
    """Generate keypair for PQC algorithm."""
    if not lib.is_available():
        click.echo("liboqs not available; cannot keygen", err=True)
        return
    # Set default filenames if not provided
    if not public_key:
        public_key = f"{output_dir}/{algorithm}.pub"
    if not private_key:
        private_key = f"{output_dir}/{algorithm}.priv"

    kp = lib.generate_keypair(algorithm)
    if not kp:
        click.echo("keygen failed", err=True)
        return
    pk, sk = kp
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(public_key).write_bytes(pk)
    Path(private_key).write_bytes(sk)
    click.echo(f"keys written: {public_key}, {private_key}")


@main.group()
def handshake() -> None:
    """Perform PQC-based secure handshake."""
    pass


@handshake.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=5555, help="Port to bind to")
@click.option(
    "--alg",
    "algorithm",
    type=click.Choice(["mlkem512", "mlkem768", "mlkem1024"]),
    default="mlkem768",
    help="KEM algorithm to use",
)
def server(host: str, port: int, algorithm: str) -> None:
    """Start handshake server."""
    params = HandshakeParams(host=host, port=port, algorithm=algorithm)
    run_server(params)


@handshake.command()
@click.option("--host", default="127.0.0.1", help="Server host")
@click.option("--port", default=5555, help="Server port")
@click.option(
    "--alg",
    "algorithm",
    type=click.Choice(["mlkem512", "mlkem768", "mlkem1024"]),
    default="mlkem768",
    help="KEM algorithm to use",
)
@click.option("--message", default="Hello PQC!", help="Message to send")
def client(host: str, port: int, algorithm: str, message: str) -> None:
    """Connect to handshake server."""
    params = HandshakeParams(host=host, port=port, algorithm=algorithm)
    reply = run_client(params, message.encode())
    click.echo(reply.decode())


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


@main.command(name="list")
def list_cmd() -> None:
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


if __name__ == "__main__":
    main()
