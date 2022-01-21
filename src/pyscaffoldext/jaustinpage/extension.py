"""Jaustinpage Austins Python Standard library pyscaffold extension."""
from functools import reduce
from typing import List

import toml
from configupdater import ConfigUpdater
from pyscaffold.actions import Action, ActionParams, ScaffoldOpts, Structure
from pyscaffold.extensions import Extension
from pyscaffold.operations import no_overwrite
from pyscaffold.structure import merge, reify_leaf, reject

from pyscaffoldext.jaustinpage import templates
from pyscaffoldext.jaustinpage.templates import template
from pyscaffoldext.markdown.extension import Markdown

JAUSTINPAGE_URL = "https://github.com/jaustinpage"

DEV_PACKAGES = ["tox"]

DOCS_PACKAGES = ["recommonmark", "rinohtype", "sphinx>=3.2.1", "toml"]

TESTING_PACKAGES = [
    "setuptools",
    "setuptools_scm",
    "coverage[toml]",
    "pytest",
    "pytest-cov",
    "pytest-mock",
]

FORMATTING_PACKAGES = [
    "black",
    "isort",
    "mdformat-gfm",
]

LINTING_PACKAGES = [
    "darglint",
    "flake8",
    "flake8-2020",
    "flake8-absolute-import",
    "flake8-annotations",
    "flake8-annotations-complexity",
    "flake8-bandit",
    "flake8-black",
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
    "flake8-isort",
    "flake8-logging-format",
    "flake8-no-implicit-concat",
    "flake8-pep3101",
    "flake8-print",
    "flake8-pytest",
    "flake8-pytest-style",
    "flake8-raise>=0.0.4",
    "flake8-requirements>=1.3.3",
    "flake8-return>=1.1.2",
    "flake8-simplify>=0.14.0",
    "flake8-spellcheck>=0.23.0",
    "flake8-strftime>=0.3.1",
    "flake8-string-format>=0.2.3",
    "flake8-super",
    "flake8-use-pathlib",
    "pep8-naming",
]


class Jaustinpage(Extension):
    """PyScaffold Extension Skeleton.

    This class serves as the skeleton for your new PyScaffold Extension. Refer
    to the official documentation to discover how to implement a PyScaffold
    extension - https://pyscaffold.org/en/latest/extensions.html
    """

    def activate(self, actions: List[Action]) -> List[Action]:
        """Activate extension.

        See :obj:`pyscaffold.extension.Extension.activate`.
        :param actions: actions to activate
        :returns: actions
        """
        actions = Markdown().activate(actions)
        # ^  Wrapping the Markdown extension is more reliable then including it via CLI.
        #    This way we can trust the activation order for registering actions,
        #    and the Python API is guaranteed to work, even if the user does not include
        #    Markdown in the list of extensions.
        actions = self.register(actions, add_files)
        return self.register(actions, replace_files, before="verify_project_dir")


def add_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Add extension files.

    See :obj:`pyscaffold.actions.Action`
    :param opts: scaffold options
    :param struct: structure
    :returns: action params
    """
    file_list = [
        ".gitignore",
        ".hgignore",
        ".run/all.run.xml",
        ".run/make.run.xml",
        ".run/pytest debug.run.xml",
        ".run/tox.run.xml",
        "Makefile",
        "tox.ini",
        "whitelist.txt",
    ]

    files: Structure = {}

    for file_path in file_list:
        *dirs, file_name = file_path.split("/")

        files_descender = files
        for dir_ in dirs:
            files_descender = files_descender.setdefault(dir_, {})
        files_descender[file_name] = (template(file_name.strip(".")), no_overwrite())

    return merge(struct, files), opts


def configure_pyproject_toml(content: str, opts: ScaffoldOpts) -> str:
    """Set customizations to pyproject.toml.

    :param content: The content of the pyproject.toml
    :param opts: scaffold options
    :returns: the modified content of the pyproject.toml
    """
    pyproject_toml = toml.loads(content)

    pyproject_toml["tool.black"] = {"line-length": 88}

    pyproject_toml["tool.isort"] = {"profile": "black"}

    pyproject_toml["tool.pytest.ini_options"] = {
        "testpaths": ["tests"],
        "addopts": [
            "--cov-report=term-missing",
            "--cov-fail-under=100",
            "--verbose",
        ],
        "norecursedirs": [
            "dist",
            "build",
            ".tox",
        ],
    }

    pyproject_toml["tool.coverage.run"] = {"branch": True, "source": [opts["package"]]}

    pyproject_toml["tool.coverage.paths"] = {"source": ["src/", "*/site-packages/"]}

    pyproject_toml["tool.coverage.report"] = {
        "skip_covered": True,
        "show_missing": True,
        "exclude_lines": [
            "pragma: no cover",
            "def __repr__",
            "if self\\.debug",
            "raise AssertionError",
            "raise NotImplementedError",
            "if 0:",
            "if __name__ == .__main__.:",
        ],
    }

    return toml.dumps(pyproject_toml)


def configure_setup_cfg(content: str, opts: ScaffoldOpts) -> str:
    """Set customizations to setup.cfg.

    :param content: The content of the setup.cfg
    :param opts: scaffold options
    :returns: the modified content of the setup.cfg
    """
    updater = ConfigUpdater()
    updater.read_string(content)
    # metadata
    updater["metadata"]["url"] = JAUSTINPAGE_URL
    updater["metadata"]["license"] = "MIT"
    updater["metadata"]["project_urls"] = [f"Source = {JAUSTINPAGE_URL}"]

    # options.extras_require
    testing_packages = updater["options.extras_require"]["testing"]
    testing_packages.set_values(TESTING_PACKAGES)
    updater.set("options.extras_require", "dev")
    updater["options.extras_require"]["dev"].set_values(DEV_PACKAGES)
    updater.set("options.extras_require", "docs")
    updater["options.extras_require"]["docs"].set_values(DOCS_PACKAGES)

    # flake8
    updater["flake8"]["extend_ignore"] = "E203, W503, ANN101"
    updater["flake8"]["docstring_style"] = "sphinx"
    updater["flake8"]["max-complexity"] = "8"
    updater["flake8"]["max-annotations-complexity"] = "4"
    updater["flake8"]["max-expression-complexity"] = "7"
    if opts.get("namespace", False):
        ns_list = ",".join([f"{ns}.{opts['package']}" for ns in opts["ns_list"]])
        updater["flake8"]["known-modules"] = f"{opts['name']}:[{ns_list}]"

    # coverage.run
    updater["flake8"].add_after.space(1).section("coverage.run")
    updater.set("coverage.run", "branch", "true")

    # coverage.paths
    updater["coverage.run"].add_after.space(1).section("coverage.paths")
    updater.set("coverage.paths", "source")
    updater["coverage.paths"]["source"].set_values(["src/", "*/site-packages/"])

    # coverage.report
    updater["coverage.paths"].add_after.space(1).section("coverage.report")
    updater["coverage.report"]["skip_covered"] = "False"
    updater["coverage.report"]["show_missing"] = "True"
    updater.set("coverage.report", "exclude_lines")
    updater["coverage.report"]["exclude_lines"].set_values(
        [
            "pragma: no cover",
            "def __repr__",
            R"if self\.debug",
            "raise AssertionError",
            "raise NotImplementedError",
            "if 0:",
            "if __name__ == .__main__.:",
        ]
    )
    updater["coverage.report"].add_after.space(1)

    return str(updater)


def replace_files(struct: Structure, opts: ScaffoldOpts) -> ActionParams:
    """Replace existing files.

    See :obj:`pyscaffold.actions.Action`
    :param opts: scaffold options
    :param struct: structure
    :returns: action params
    """
    # do setup.cfg modifications
    setup_content, setup_file_op = reify_leaf(struct["setup.cfg"], opts)
    struct["setup.cfg"] = (configure_setup_cfg(setup_content, opts), setup_file_op)
    pyproject_content, pyproject_file_op = reify_leaf(struct["pyproject.toml"], opts)
    struct["pyproject.toml"] = (
        configure_pyproject_toml(pyproject_content, opts),
        pyproject_file_op,
    )

    # remove files for replacement
    replacement_files = [
        "LICENSE.txt",
        f"src/{opts['package']}/__init__.py",
        f"src/{opts['package']}/skeleton.py",
        "tests/test_skeleton.py",
        "tests/conftest.py",
    ]

    struct = reduce(reject, replacement_files, struct)

    # define new files
    files: Structure = {
        "AUTHORS.md": (template("AUTHORS.md"), no_overwrite()),
        "LICENSE.txt": (template("LICENSE.txt"), no_overwrite()),
        "README.md": (template("README.md"), no_overwrite()),
        "src": {
            opts["package"]: {
                "__init__.py": templates.init,
                "skeleton.py": (template("skeleton.py"), no_overwrite()),
            }
        },
        "tests": {
            "test_skeleton.py": (template("test_skeleton.py"), no_overwrite()),
            "conftest.py": (template("conftest.py"), no_overwrite()),
        },
        "docs": {
            "index.md": (template("index.md"), no_overwrite()),
        },
    }

    # merge new files and return
    return merge(struct, files), opts
