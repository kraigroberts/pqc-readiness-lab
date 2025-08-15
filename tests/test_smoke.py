"""Smoke tests for PQC Readiness Lab package."""

from pqc_lab import __version__, config, lib


def test_package_import() -> None:
    """Test that the package can be imported successfully."""
    assert __version__ == "0.1.0"


def test_config_import() -> None:
    """Test that configuration module can be imported."""
    assert config is not None
    assert hasattr(config, "config")


def test_lib_import() -> None:
    """Test that liboqs wrapper module can be imported."""
    assert lib is not None
    assert hasattr(lib, "is_available")


def test_basic_configuration() -> None:
    """Test basic configuration values."""
    assert config.get_default_kem() == "ML-KEM-768"
    assert config.get_default_dsa() == "ML-DSA-65"
    assert len(config.get_kem_algorithms()) > 0
    assert len(config.get_dsa_algorithms()) > 0


def test_lib_capabilities() -> None:
    """Test liboqs wrapper capabilities."""
    # These may return empty lists if liboqs is not available
    # but should not crash
    kems = lib.get_supported_kems()
    sigs = lib.get_supported_sigs()

    assert isinstance(kems, list)
    assert isinstance(sigs, list)


def test_version_info() -> None:
    """Test version information."""
    version = lib.get_version()
    assert isinstance(version, str)

    # Version should be either "unknown" or a valid version string
    assert version == "unknown" or len(version) > 0


def test_artifacts_directory() -> None:
    """Test artifacts directory configuration."""
    artifacts_dir = config.get_artifacts_dir()
    assert artifacts_dir.name == "artifacts"


def test_network_config() -> None:
    """Test network configuration."""
    net_config = config.get_network_config()
    assert net_config.default_host == "127.0.0.1"
    assert net_config.default_port == 5555
    assert net_config.timeout > 0


def test_benchmark_config() -> None:
    """Test benchmark configuration."""
    bench_config = config.get_benchmark_config()
    assert bench_config.default_iterations > 0
    assert bench_config.warmup_iterations >= 0
    assert bench_config.output_format in ["json", "text", "csv"]


if __name__ == "__main__":
    # Basic smoke test runner
    print("Running PQC Lab smoke tests...")

    test_package_import()
    test_config_import()
    test_lib_import()
    test_basic_configuration()
    test_lib_capabilities()
    test_version_info()
    test_artifacts_directory()
    test_network_config()
    test_benchmark_config()

    print("All smoke tests passed!")
