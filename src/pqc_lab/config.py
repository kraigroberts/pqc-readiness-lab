from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class AlgorithmConfig(BaseModel):
    kem: str = Field(default="ML-KEM-768", description="NIST KEM algorithm choice")
    signature: str = Field(default="ML-DSA-65", description="NIST signature algorithm choice")


class PathsConfig(BaseModel):
    artifacts_dir: Path = Field(default=Path("artifacts"))


class NetworkConfig(BaseModel):
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=5555)


class Config(BaseModel):
    algorithms: AlgorithmConfig = Field(default_factory=AlgorithmConfig)
    paths: PathsConfig = Field(default_factory=PathsConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)
    config_file: Optional[Path] = Field(default=None)


def default_config() -> Config:
    return Config()
