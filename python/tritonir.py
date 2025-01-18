import vim
import re

# Global variables
ttir_to_source = {}
source_to_ttir = {}
source_buffer_name = None
ttir_buffer_name = None
source_file_path = None  # Store the source file path from the first #loc

def parse_tritonir(file_path):
    """Parse the Triton IR file for loc mappings."""
    global ttir_to_source, source_to_ttir, ttir_buffer_name, source_file_path

    ttir_to_source.clear()
    source_to_ttir.clear()
    source_file_path = None

    loc_mapping = {}  # Map #loc IDs to source file lines

    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            # Match the first #loc to determine the source file
            if not source_file_path:
                first_loc_match = re.search(r'#loc = loc\("(.*?)":\d+:\d+\)', line)
                if first_loc_match:
                    source_file_path = first_loc_match.group(1)
                    vim.command(f'echom "Source file path: {source_file_path}"')

            # Match and store #loc definitions
            # Match other #loc directives for line mappings
            match = re.search(r'#loc(\d+) = loc\("(.*?)":(\d+):\d+\)', line)
            if match:
                loc_id, src_file, src_line = match.groups()
                src_line = int(src_line)
                loc_mapping[f'#loc{loc_id}'] = (src_file, src_line)
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            # Match operations with #loc references
            op_match = re.search(r'loc\s*\(\s*(#loc\d+)\s*\)', line)
            if op_match:
                loc_id = op_match.group(1)
                if loc_id in loc_mapping:
                    src_file, src_line = loc_mapping[loc_id]
                    # Map IR line to source line
                    if line_number not in ttir_to_source:
                        ttir_to_source[line_number] = []
                    ttir_to_source[line_number].append(src_line)

                    # Map source line back to IR line
                    if src_line not in source_to_ttir:
                        source_to_ttir[src_line] = []
                    source_to_ttir[src_line].append(line_number)

    # Store the buffer name for synchronization
    ttir_buffer_name = vim.current.buffer.name

    # Debugging: Output the mappings
    # vim.command(f'echom "Source file path: {source_file_path}"')
    # vim.command(f'echom "Triton IR to Source Mapping: {ttir_to_source}"')
    # vim.command(f'echom "Source to Triton IR Mapping: {source_to_ttir}"')

def open_source_file():
    """Open the corresponding source file in a split."""
    global source_buffer_name, source_file_path

    if not source_file_path:
        print("No source file found in the Triton IR file.")
        return

    # Check if the source file is already open in any active buffer
    for buf in vim.buffers:
        if buf.name == source_file_path:
            print("Source file is already open in another buffer.")
            return
    try:
        vim.command(f'vsplit {source_file_path}')
        source_buffer_name = source_file_path
    except vim.error as e:
        print(f"Error opening source file: {e}")

def sync_cursor_to_source():
    """Sync cursor movement from Triton IR to the source file."""
    global ttir_buffer_name, source_buffer_name
    curr_line = vim.current.window.cursor[0]
    vim.command('call clearmatches()')
    if curr_line in ttir_to_source:
        vim.command(f'echom "{ttir_buffer_name} Triton IR Cursor Line: {curr_line}, mapping {ttir_to_source[curr_line]}"')  # Debug print
        src_line = ttir_to_source[curr_line]
        # Highlight line without moving cursor
        highlight_line(source_buffer_name, src_line)
    else:
        vim.command('echom "No mapping found for this line in Triton IR"')  # Debug print
        highlight_line(source_buffer_name, [])

def sync_cursor_to_ttir():
    """Sync cursor movement from the source file to the Triton IR file."""
    global source_buffer_name, ttir_buffer_name
    curr_line = vim.current.window.cursor[0]
    vim.command('call clearmatches()')
    if curr_line in source_to_ttir:
        vim.command(f'echom "{source_buffer_name} Source Cursor Line: {curr_line}, mapping {source_to_ttir[curr_line]}"')  # Debug print
        ttir_line = source_to_ttir[curr_line]
        # Highlight line without moving cursor
        highlight_line(ttir_buffer_name, ttir_line)
    else:
        vim.command('echom "No mapping found for this line in the source file"')  # Debug print
        highlight_line(ttir_buffer_name, [])

def highlight_line(buffer_name, line_numbers):
    """Highlight a list of specific lines in the given buffer."""
    try:
        # Save the current window and buffer
        current_window = vim.current.window
        current_buffer = vim.current.buffer.name

        # Find the window containing the target buffer
        target_window = None
        for window in vim.windows:
            if window.buffer.name == buffer_name:
                target_window = window
                break

        if not target_window:
            vim.command(f'echom "Target buffer {buffer_name} not found in any window."')
            return

        # Switch to the target window
        vim.current.window = target_window

        # Clear existing highlights in the target buffer
        vim.command('call clearmatches()')

        # Apply highlights to the specified lines
        for line_number in line_numbers:
            vim.command(f'call matchaddpos("Search", [{line_number}])')

        # Move the first highlighted line into view
        if line_numbers:
            vim.command(f'call cursor({line_numbers[0]}, 1)')
            vim.command('normal! zz')  # Center the cursor in the window

        # Switch back to the original window
        vim.current.window = current_window
    except Exception as e:
        vim.command(f'echom "Error in highlight_line: {e}"')

def sync_lines():
    """Sync cursor movements between Triton IR and source file."""
    curr_buf = vim.current.buffer.name
    try:
        if curr_buf == ttir_buffer_name:
            sync_cursor_to_source()
        elif curr_buf == source_buffer_name:
            sync_cursor_to_ttir()
    except Exception as e:
        vim.command(f'echom "Error in sync_lines: {e}"')  # Debugging exception
