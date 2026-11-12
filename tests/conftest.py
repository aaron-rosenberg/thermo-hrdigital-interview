"""Shared synthetic database and isolated source copies."""

from contextlib import closing
from pathlib import Path
import shutil

import sqlite3
import pytest

from workforce.runner import build

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def database(tmp_path_factory):
    output = tmp_path_factory.mktemp("warehouse") / "workforce.sqlite"
    build(ROOT / "fixtures", output)
    return output


@pytest.fixture
def db(database):
    with closing(sqlite3.connect(f"file:{database}?mode=ro", uri=True)) as connection:
        yield connection


@pytest.fixture
def extracts(tmp_path):
    return Path(shutil.copytree(ROOT / "fixtures", tmp_path / "fixtures"))
