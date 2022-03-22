import nox
from shutil import rmtree
from pathlib import Path
from typing import Tuple, List
from os import getenv

nox.options.sessions = ["default"]

ISORT_FILES = ["src", "tests", "setup.py"]
BLACK_FILES = ["src/", "tests/"]
MARKDOWN_OPTIONS = ["--wrap=88", "--end-of-line=lf"]
MARKDOWN_FILES = ["README.md", "docs/", "src/", "tests/"]
SORT_FILE_EXE = ["python3", "scripts/sort_file.py"]
WHITELIST_FILE = ["whitelist.txt"]
CI_ENV_VARS = ["CI"]
FLAKE_PLUGINS = [
    "darglint",
    "flake8-2020",
    "flake8-absolute-import",
    "flake8-annotations",
    "flake8-annotations-complexity",
    "flake8-bandit",
    "flake8-blind-except",
    "flake8-breakpoint",
    "flake8-broken-line",
    "flake8-bugbear",
    "flake8-builtins",
    "flake8-class-attributes-order",
    "flake8-comprehensions",
    "flake8-datetimez",
    "flake8-debugger",
    "flake8-docstrings",
    "flake8-dunder-class-obj",
    "flake8-eradicate",
    "flake8-executable",
    "flake8-expression-complexity",
    "flake8-fixme",
    "flake8-if-expr",
    "flake8-logging-format",
    "flake8-no-implicit-concat",
    "flake8-pep3101",
    "flake8-print",
    "flake8-pytest",
    "flake8-pytest-style",
    "flake8-raise",
    "flake8-requirements",
    "flake8-return",
    "flake8-simplify",
    "flake8-spellcheck",
    "flake8-strftime",
    "flake8-string-format",
    "flake8-super",
    "flake8-use-pathlib",
    "pep8-naming",
    "mdformat-gfm"
]


@nox.session(python=False)
def default(session: nox.Session) -> None:
    if any([getenv(e, False) for e in CI_ENV_VARS]):
        session.notify("check_format")
    else:
        session.notify("format")

    session.notify("test")
    session.notify("lint")
    session.notify("mypy")
    session.notify("docs(build)")
    session.notify("docs(test)")
    session.notify("docs(pdf)")
    session.notify("build")


@nox.session(python=False)
def clean(session: nox.Session) -> None:
    rmtree("build", True)
    rmtree("dist", True)


@nox.session(python=False)
def format(session: nox.Session) -> None:
    session.notify("fmt_isort")
    session.notify("fmt_black")
    session.notify("fmt_markdown")
    session.notify("fmt_whcitelist")


@nox.session
def fmt_isort(session: nox.Session) -> None:
    session.install("isort")
    session.run("isort", *ISORT_FILES)


@nox.session
def fmt_black(session: nox.Session) -> None:
    session.install("black")
    session.run("black", *BLACK_FILES)


@nox.session
def fmt_markdown(session: nox.Session) -> None:
    session.install("mdformat-gfm")
    session.run("mdformat", *MARKDOWN_OPTIONS, *MARKDOWN_FILES)


@nox.session
def fmt_whitelist(session: nox.Session) -> None:
    session.run(*SORT_FILE_EXE, *WHITELIST_FILE)

@nox.session
def check_format(session: nox.Session) -> None:
    session.notify("chk_isort")
    session.notify("chk_black")
    session.notify("chk_markdown")
    session.notify("chk_whitelist")


@nox.session
def chk_isort(session: nox.Session) -> None:
    session.install("isort")
    session.run("isort", *ISORT_FILES, "-c")

@nox.session
def chk_black(session: nox.Session) -> None:
    session.install("black")
    session.run("black", "--check", *BLACK_FILES)

@nox.session
def chk_markdown(session: nox.Session) -> None:
    session.install("mdformat-gfm")
    session.run("mdformat", "--check", *MARKDOWN_OPTIONS, *MARKDOWN_FILES)

@nox.session
def chk_whitelist(session: nox.Session) -> None:
    session.run(*SORT_FILE_EXE, "--check", *WHITELIST_FILE)
    
@nox.session
def test(session: nox.Session) -> None:
    session.install("pytest")
    session.install("-e", ".[testing]")
    session.run("pytest")

@nox.session
def lint(session: nox.Session) -> None:
    session.install("flake8", "flakeheaven", *FLAKE_PLUGINS)
    session.run("flakeheaven", "lint", "src/")
    session.run("flakeheaven", "lint", "tests/")

@nox.session
def mypy(session: nox.Session) -> None:
    session.install("mypy")
    session.run("mypy", "src/")


@nox.session(python=['3.7', '3.8', '3.9', '3.10'])
def test_all_python(session: nox.Session) -> None:
    session.install("pytest")
    session.install("-e", ".[testing]")
    session.run("pytest")

@nox.session
@nox.parametrize("command", [
    nox.param('html', id="build"),
    nox.param('doctest', id="test"),
    nox.param('rinoh', id="pdf")])
def docs(session: nox.Session, command: str) -> None:
    session.install("sphinx")
    session.install("-e", ".[docs]")
    session.run("python3", "-m", "sphinx.cmd.build", "-b", command, "-d", "docs/_build/doctrees", "docs/", f"docs/_build/{command}", env={'AUTODOCDIR': 'api'})

@nox.session
def build(session: nox.Session) -> None:
    session.install("-e", ".")
    session.run("python3", "-m", "build", "--sdist", "--wheel", ".")
