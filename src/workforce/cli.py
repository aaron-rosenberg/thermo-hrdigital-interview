"""Command-line entry point; no network or cloud credentials required."""

import argparse
import logging
from pathlib import Path

from workforce.runner import build


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("build", help="Rebuild a local database from CSV extracts")
    command.add_argument("--fixtures", type=Path, default=Path("fixtures"))
    command.add_argument("--output", type=Path, default=Path(".local/workforce.sqlite"))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        build(args.fixtures, args.output)
    except (ValueError, OSError) as exc:
        logging.error("Build failed: %s", exc)
        return 1
    return 0
