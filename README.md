# toml-lint

A linter for TOML files that can detect multiple errors using by tree-sitter parser

## Installation

```
pip install git+https://github.com/yaegassy/toml-lint

# or

pipx install git+https://github.com/yaegassy/toml-lint
```

> TODO: Publishing to PyPI

## Motivation

The `loads` function in `tomllib/tomli` raises an exception and stops when it detects one error. It cannot detect multiple errors.

Therefore, I have created a linter that utilizes the "tree-sitter" parser to detect tree-error-nodes and executes the `loads` function from `tomllib/tomli` for each tree-error-node.

Furthermore, since there are errors that cannot be detected solely by the errors from the "tree-sitter" parser, I also execute the `loads` function from `tomllib/tomli` at the file level and combine the results.

## Usage

### Help

```bash
$ toml-lint --help
usage: toml-lint [-h] [--version] [--stdin-filename STDIN_FILENAME] [filename]

A linter for TOML files that can detect multiple errors using by tree-sitter parser

positional arguments:
  filename              filename to be processed

options:
  -h, --help            show this help message and exit
  --version             print version
  --stdin-filename STDIN_FILENAME
                        name of the file when passing it through stdin

Examples:
  - **FILE**: toml-lint input.toml
  - **STDIN**: cat input.toml | toml-lint --stdin-filename input.toml -
```

### Example of execution

**TOML file with multiple errors**:

```
[tool.ruff]
select = [
  I" # <- There is one missing double quote.
]

[tool.black]
line-length = 79" # <- There are unnecessary double quotes present.

[tool.mypy]
ignore_missing_imports = True # <- The correct form is "true" in lowercase.
```

**Execution result**:

```bash
$ toml-lint input.toml
input.toml:3:2 error: Invalid value
input.toml:7:17 error: Expected newline or end of document after a statement
input.toml:10:26 error: Invalid value
```

## Editor Integration Demo

**Vim/Neovim**:

https://github.com/yaegassy/toml-lint/assets/188642/42c28f5e-e7b4-4f9c-9e92-77331ed32b73

## License

MIT
