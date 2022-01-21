#!/usr/bin/env python3
"""Format markdown templates taking into consideration substitution lengths."""
import logging
from contextlib import suppress
from pathlib import Path
from string import Template
from typing import Tuple, Union

import black  # noqa: I900
import isort  # noqa: I900
import mdformat  # noqa: I900
from diff_match_patch import diff_match_patch  # noqa: I900

dmp = diff_match_patch()

PYSCAFFOLD_OPTS = {
    "distribution": None,
    "name": "myproject",
    "package": "myproject",
    "author": "Austin Page",
    "email": "jaustinpage@gmail.com",
    "license": "MIT",
    "description": "A description",
    "version": "0.0.1",
    "qual_pkg": "my.ns.myproject",
}


class BadPatchError(Exception):
    """Error when patch did not apply cleanly."""

    pass


def patch_original(
    original_text: str, substituted_text: str, formatted_text: str
) -> str:
    """Patch original text with formatting fixes.

    :param original_text: the original text in the file
    :param substituted_text: the substituted text to check the formatting of
    :param formatted_text: the substituted text after it has been formatted
    """
    patches = dmp.patch_make(substituted_text, formatted_text)
    patched_original_text, applied = dmp.patch_apply(patches, original_text)
    for p in applied:
        if not p:
            raise BadPatchError("Patches did not apply successfully")

    return patched_original_text


Diffs = Union[list[tuple[int, str]], list]


def diff_text(text1: str, text2: str) -> Diffs:
    diff = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diff)
    return diff


def pretty_print_diff(diffs: Diffs) -> str:
    patches = dmp.patch_make(diffs)
    return dmp.patch_toText(patches)


def black_formatter(contents: str) -> str:
    mode = black.Mode(
        target_versions={black.TargetVersion.PY36},
        line_length=88,
        string_normalization=True,
        is_pyi=False,
    )
    with suppress(black.NothingChanged):
        return black.format_str(contents, mode=mode)
    return contents


def isort_formatter(contents: str) -> str:
    iconfig = isort.Config(
        profile="black",
        known_first_party={
            f"{PYSCAFFOLD_OPTS['qual_pkg']}.skeleton",
            f"{PYSCAFFOLD_OPTS['qual_pkg']}",
        },
    )
    return isort.code(contents, config=iconfig)


def pyfile_formatter(contents: str) -> str:
    return black_formatter(isort_formatter(contents))


def mdfile_formatter(contents: str) -> str:
    """Format .md files.

    :param contents: the contents of the mdfile
    :returns: the formatted file
    """
    return mdformat.text(contents, options={"wrap": 88})


def get_template(path: Path) -> Tuple[str, str]:
    """Get original and substituted text.

    :param path: the path to the template
    :returns: original text, substituted text
    """
    original_text = path.read_text()
    substituted_text = Template(original_text).safe_substitute(PYSCAFFOLD_OPTS)
    return original_text, substituted_text


def sort_formatter(contents: str) -> str:
    return "\n".join(sorted(contents.splitlines(), key=str.casefold)) + "\n"


FILETYPE_FORMATTERS = {
    ".md": mdfile_formatter,
    ".py": pyfile_formatter,
    "whitelist.txt": sort_formatter,
}


class FormatterNotFoundError(Exception):
    """Raised when formatter cannot be found."""

    pass


def format_text(path: Path, contents: str) -> str:
    """Format text of file.

    :param path: path to file
    :param contents: contents of file
    :returns: formatted contents of file
    """
    filename = Path(path.stem)
    extension = filename.suffix
    formatter = FILETYPE_FORMATTERS.get(
        extension, FILETYPE_FORMATTERS.get(str(filename), None)
    )
    if not formatter:
        raise FormatterNotFoundError
    return formatter(contents)


def process_file(path: Path) -> None:
    original_text, substituted_text = get_template(path)
    try:
        formatted_substitute_text = format_text(path, substituted_text)
        formatted_original_text = patch_original(
            original_text, substituted_text, formatted_substitute_text
        )
        proposed_changes = diff_text(original_text, formatted_original_text)
        if 1 < len(proposed_changes):
            logging.warning(
                "Changing %s:\n %s", path, pretty_print_diff(proposed_changes)
            )
            path.write_text(formatted_original_text)
        else:
            logging.info("No changes needed for %s", path)
    except FormatterNotFoundError:
        logging.info("Could not find formatter for %s", path)
    except BadPatchError:
        logging.warning("Patches did not apply correctly for %s", path)


def main() -> None:
    """Fix file formats."""
    for path in Path("src").rglob("*.template"):
        process_file(path)


if __name__ == "__main__":
    main()
