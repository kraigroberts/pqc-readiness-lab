from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click

from . import __version__
from .config import Config, default_config


@click.group()
@click.version_option(__version__, prog_name="pqc-lab")
@click.option("--config", type=click.Path(path_type=Path), default=None, help="Config file")
@click.pass_context
def main(ctx: click.Context, config: Optional[Path]) -> None:
    cfg = default_config()
    if config is not None and config.exists():
        # For milestone 1 keep it simple: no file parsing yet
        cfg = cfg.model_copy(update={"config_file": config})
    ctx.obj = cfg


@main.command()
@click.pass_obj
def info(cfg: Config) -> None:
    data = {
        "version": __version__,
        "algorithms": cfg.algorithms.model_dump(),
        "network": cfg.network.model_dump(),
        "paths": {"artifacts_dir": str(cfg.paths.artifacts_dir)},
    }
    click.echo(json.dumps(data))


if __name__ == "__main__":
    main()
