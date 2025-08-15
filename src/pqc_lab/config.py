"""Configuration settings for PQC Readiness Lab."""

from pathlib import Path

from pydantic import BaseModel, Field


class AlgorithmConfig(BaseModel):
    """Configuration for PQC algorithms."""

    # KEM algorithms
    kem_algorithms: list[str] = Field(
        default=["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
        description="Supported KEM algorithms",
    )

    # DSA algorithms
    dsa_algorithms: list[str] = Field(
        default=["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"],
        description="Supported DSA algorithms",
    )

    # Default algorithms
    default_kem: str = Field(default="ML-KEM-768", description="Default KEM algorithm")
    default_dsa: str = Field(default="ML-DSA-65", description="Default DSA algorithm")


class NetworkConfig(BaseModel):
    """Configuration for network operations."""

    default_host: str = Field(
        default="127.0.0.1", description="Default host for network operations"
    )
    default_port: int = Field(
        default=5555, description="Default port for network operations"
    )
    timeout: float = Field(default=30.0, description="Network timeout in seconds")
    buffer_size: int = Field(default=4096, description="Network buffer size")


class BenchmarkConfig(BaseModel):
    """Configuration for benchmarking operations."""

    default_iterations: int = Field(
        default=100, description="Default benchmark iterations"
    )
    warmup_iterations: int = Field(
        default=10, description="Warmup iterations before timing"
    )
    output_format: str = Field(default="json", description="Benchmark output format")
    save_results: bool = Field(
        default=True, description="Save benchmark results to file"
    )


class FileConfig(BaseModel):
    """Configuration for file operations."""

    artifacts_dir: Path = Field(
        default=Path("artifacts"), description="Directory for artifacts"
    )
    key_prefix: str = Field(default="pqc", description="Prefix for generated keys")
    signature_extension: str = Field(
        default=".sig", description="Extension for signature files"
    )
    public_key_extension: str = Field(
        default=".pub", description="Extension for public key files"
    )
    private_key_extension: str = Field(
        default=".priv", description="Extension for private key files"
    )


class Config(BaseModel):
    """Main configuration for PQC Readiness Lab."""

    algorithm: AlgorithmConfig = Field(default_factory=AlgorithmConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    benchmark: BenchmarkConfig = Field(default_factory=BenchmarkConfig)
    file: FileConfig = Field(default_factory=FileConfig)

    # liboqs configuration
    liboqs_path: Path | None = Field(
        default=None, description="Path to liboqs installation"
    )
    enable_openssl: bool = Field(default=True, description="Enable OpenSSL integration")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    verbose: bool = Field(default=False, description="Verbose output")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        extra = "forbid"


# Global configuration instance
config = Config()


# Convenience accessors
def get_kem_algorithms() -> list[str]:
    """Get list of supported KEM algorithms."""
    return config.algorithm.kem_algorithms


def get_dsa_algorithms() -> list[str]:
    """Get list of supported DSA algorithms."""
    return config.algorithm.dsa_algorithms


def get_default_kem() -> str:
    """Get default KEM algorithm."""
    return config.algorithm.default_kem


def get_default_dsa() -> str:
    """Get default DSA algorithm."""
    return config.algorithm.default_dsa


def get_artifacts_dir() -> Path:
    """Get artifacts directory path."""
    return config.file.artifacts_dir


def get_network_config() -> NetworkConfig:
    """Get network configuration."""
    return config.network


def get_benchmark_config() -> BenchmarkConfig:
    """Get benchmark configuration."""
    return config.benchmark
