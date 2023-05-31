import argparse
import sys
from typing import List, Optional

from .core import lint

__all__ = ["cli"]


STD_STREAM = "-"
ENCODING = "UTF-8"


def get_version() -> str:
    """Get the program version."""
    try:
        from importlib.metadata import version  # type: ignore
    except ImportError:
        try:
            from importlib_metadata import version  # type: ignore
        except ImportError:
            print(
                "Error: unable to get version. "
                "If using Python < 3.8, you must install "
                "`importlib_metadata` to get the version.",
                file=sys.stderr,
            )
            sys.exit(1)
    return version("toml-lint")


def read_file(path: str) -> str:
    """Read contents from a file."""
    if path == STD_STREAM:
        return sys.stdin.read()
    with open(path, "r", encoding=ENCODING) as fileobj:
        return fileobj.read()


def get_parser() -> argparse.ArgumentParser:
    """Get the argument parser."""
    parser = argparse.ArgumentParser(
        prog="toml-lint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A linter for TOML files that can detect multiple errors using by tree-sitter parser",
        epilog="""\
Examples:
  - **FILE**: toml-lint input.toml
  - **STDIN**: cat input.toml | toml-lint --stdin-filename input.toml -
""",
    )
    parser.add_argument(
        "--version",
        help="print version",
        action="store_true",
    )
    parser.add_argument(
        "--stdin-filename",
        dest="stdin_filename",
        help="name of the file when passing it through stdin",
        type=str,
    )
    parser.add_argument(
        "filename",
        help=("filename to be processed"),
        type=str,
        nargs="?",
    )
    return parser


def cli(
    arguments: Optional[List[str]] = None,
) -> None:
    parser = get_parser()
    args = parser.parse_args(args=arguments)

    if args.version:
        print(get_version())
        sys.exit(0)

    if args.filename is None:
        parser.print_help()
        sys.exit(0)

    toml_text = read_file(args.filename)
    display_filename = args.stdin_filename if args.stdin_filename else args.filename

    lint(toml_text, display_filename)
