# vim-triton-ir-inspector

A Vim plugin to inspect Triton IR files and map them to their corresponding source files.

## Installation

Choose one of the following options:

### Using [vim-plug](https://github.com/junegunn/vim-plug): 

`Plug 'srikanthmalla/vim-triton-ir-inspector'`

### Clone the repo and manually add the path to runtime:

Copy this repo under `.vim` and add this line to `.vimrc`:

set runtimepath+=~/.vim/vim-triton-ir-inspector

## Dependencies:

- Vim compiled with `+python3`.
- Python 3 environment to execute the plugin logic.

---

## Commands

### `:TritonIRToggle`
- Toggles inspection of a Triton IR file.
- Opens the corresponding source file in a split if mappings exist.

---

## Keybindings

| Keybinding    | Command            |
|---------------|--------------------|
| `<Leader>tt`  | `:TritonIRToggle`  |

---

## Example Usage

1. **Inspect Triton IR file**:
    Open a Triton IR file in Vim and run:

    ```vim
    :TritonIRToggle
    ```

    The plugin parses the file for mappings and opens the associated source file in a split.

2. **Mapping Sync**:
    - Moving the cursor in the Triton IR file will highlight the corresponding line in the source file.
    - Similarly, moving the cursor in the source file will highlight the related line(s) in the Triton IR file.

---

## Features

- Parses Triton IR files for `#loc` directives.
- Highlights corresponding lines in the source file and IR file based on cursor movements.
- Automatically syncs mappings in real-time as you navigate files.

---

## Requirements

- Vim with Python 3 support.
- Triton IR files with `#loc` directives.
