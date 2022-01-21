"""Test helpers."""
import os
import shlex
import stat
import sys
import traceback
from pathlib import Path
from shutil import rmtree
from subprocess import STDOUT, CalledProcessError, check_output  # noqa: S404
from time import sleep
from uuid import uuid4
from warnings import warn

from pyscaffold.shell import get_executable

IS_POSIX = os.name == "posix"

PYTHON = sys.executable
"""Same python executable executing the tests... Hopefully the one inside the virtualenv
inside tox folder. If we install packages by mistake is not a huge problem.
"""


def uniqstr():
    """Generate a unique random long string."""
    return str(uuid4())


def rmpath(path):
    """Recursively remove path.

    If an error occurs it will just be ignored, so not suitable for every usage.
    The best is to use this function for paths inside pytest tmp directories, and with
    some hope pytest will also do some cleanup itself.
    """
    try:
        rmtree(str(path), onerror=set_writable)
    except FileNotFoundError:
        return
    except Exception:  # noqa: B902
        msg = f"rmpath: Impossible to remove {path}, probably an OS issue...\n\n"
        warn(msg + traceback.format_exc())


def set_writable(func, path, _exc_info):
    sleep(1)  # Sometimes just giving time to the SO, works
    path = Path(path)

    if not path.exists():
        return  # we just want to remove files anyway

    if not os.access(path, os.W_OK):
        path.chmod(stat.S_IWUSR)

    # now it either works or re-raise the exception
    func(path)


def run(*args, **kwargs):
    """Run the external command. See ``subprocess.check_output``."""
    # normalize args
    if len(args) == 1:
        if isinstance(args[0], str):
            args = shlex.split(args[0], posix=IS_POSIX)
        else:
            args = args[0]

    if args[0] in ("python", "putup", "pip", "tox", "pytest", "pre-commit"):
        raise SystemError("Please specify an executable with explicit path")

    opts = {"stderr": STDOUT, "universal_newlines": True}
    opts.update(kwargs)

    try:
        return check_output(args, **opts)  # noqa: S603
    except CalledProcessError as ex:
        print("\n\n" + "!" * 80 + "\nError while running command:")  # noqa: T001
        print(args)  # noqa: T001
        print(opts)  # noqa: T001
        traceback.print_exc()
        msg = "\n******************** Terminal ($? = {0}) ********************\n{1}"
        print(msg.format(ex.returncode, ex.output))  # noqa: T001
        raise


def run_common_tasks(venv=True, tox=True, pre_commit=True, install=True):
    """Run common task."""
    # Requires tox, setuptools_scm and pre-commit in setup.cfg ::
    # opts.extras_require.testing
    if venv:
        run(f"{PYTHON} -m tox -e .venv")

    if tox:
        run(f"{PYTHON} -m tox")

    wheels = list(Path("dist").glob("*.whl"))
    assert wheels

    pdf_path = Path("docs") / "_build" / "rinoh" / "user_guide.pdf"
    assert pdf_path.is_file()

    run(f"{PYTHON} setup.py --version")

    if pre_commit:
        try:
            run(f"{PYTHON} -m pre_commit run --all-files")
        except CalledProcessError:
            print(run(get_executable("git"), "diff"))  # noqa: T001
            raise

    if install:
        assert Path(".venv").exists(), "Please use --venv when generating the project"
        venv_pip = get_executable("pip", prefix=".venv", include_path=False)
        assert venv_pip, "Pip not found, make sure you have used the --venv option"
        run(venv_pip, "install", wheels[0])

    run(get_executable("hg"), "init")
    run(get_executable("hg"), "status")

    run(get_executable("git"), "diff", "--exit-code")
