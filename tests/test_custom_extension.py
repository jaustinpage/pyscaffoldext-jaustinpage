"""Test extension."""

from pathlib import Path

import pytest
from pyscaffold import cli
from pyscaffold.file_system import chdir

from pyscaffoldext.jaustinpage import templates
from pyscaffoldext.jaustinpage.extension import Jaustinpage

from .helpers import run_common_tasks

EXT_FLAGS = [Jaustinpage().flag]

# If you need to check logs with caplog, have a look on
# pyscaffoldext-custom-extension's tests/conftest.py file and the
# `isolated_logger` fixture.


def test_add_custom_extension(tmpfolder):
    args = ["my_project", "--no-config", "-p", "my_package", *EXT_FLAGS]
    # --no-config: avoid extra config from dev's machine interference
    cli.main(args)
    assert Path("my_project/src/my_package/__init__.py").exists()


@pytest.mark.parametrize(
    "add_file",
    ["Makefile", "LICENSE.txt", ".hgignore", ".gitignore"],
)
def test_file_is_added(add_file, tmpfolder):
    args = ["my_project", "--no-config", "-p", "my_package", *EXT_FLAGS]
    # --no-config: avoid extra config from dev's machine interference
    cli.main(args)
    filepath = Path(f"my_project/{add_file}")
    original_filepath = (
        Path(templates.__file__).resolve().parent / f"{add_file.strip('.')}.template"
    )
    assert filepath.exists()
    assert filepath.read_text() == original_filepath.read_text()


def test_setup_cfg_modified(tmpfolder):
    args = ["my_project", "--no-config", "-p", "my_package", *EXT_FLAGS]
    # --no-config: avoid extra config from dev's machine interference
    cli.main(args)
    filepath = Path("my_project/setup.cfg")
    setup_cfg_text = filepath.read_text()
    assert "url = https://github.com/jaustinpage" in setup_cfg_text
    assert "Source = https://github.com/jaustinpage" in setup_cfg_text
    assert "license = MIT" in setup_cfg_text
    assert "pytest-mock" in setup_cfg_text


def test_add_custom_extension_and_pretend(tmpfolder):
    args = ["my_project", "--no-config", "--pretend", "-p", "my_package", *EXT_FLAGS]
    # --no-config: avoid extra config from dev's machine interference
    cli.main(args)

    assert not Path("my_project").exists()


def test_add_custom_extension_with_namespace(tmpfolder):
    args = [
        "my_project",
        "--no-config",  # avoid extra config from dev's machine interference
        "--package",
        "my_package",
        "--namespace",
        "my.ns",
        *EXT_FLAGS,
    ]
    cli.main(args)

    assert Path("my_project/src/my/ns/my_package/__init__.py").exists()


# To use marks make sure to uncomment them in setup.cfg
# @pytest.mark.slow
def test_generated_extension(tmpfolder):
    args = [
        "myproject",
        "--no-config",  # avoid extra config from dev's machine interference
        "--venv",  # generate a venv so we can install the resulting project
        "--pre-commit",  # ensure generated files respect repository conventions
        "--namespace",  # it is very easy to forget users might want to use namespaces
        "my.ns",  # ... so we automatically test the worst case scenario
        *EXT_FLAGS,
    ]
    cli.main(args)

    with chdir("myproject"):
        # Testing a project generated by the custom extension
        run_common_tasks()