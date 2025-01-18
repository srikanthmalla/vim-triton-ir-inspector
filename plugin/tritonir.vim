" TritonIRInspector Plugin for Vim
if !has('python3')
  echoerr "TritonIRInspector requires Python 3 support in Vim"
  finish
endif

" Avoid loading the plugin multiple times
if exists('g:vim_triton_ir_plugin_loaded')
    finish
endif
let g:vim_triton_ir_plugin_loaded = 1

" Set up Python path
let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

python3 << EOF
import sys
from os.path import normpath, join

# Set up the Python path
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
import tritonir
EOF

function! TritonIRInspector_toggle()
  " Check if the current file appears to be a Triton IR file
  let l:is_tritonir = 0
  let l:content = getline(1, '$')
  for l:line in l:content
    if l:line =~ '#loc' || l:line =~ 'module {'
      let l:is_tritonir = 1
      break
    endif
  endfor

  if !l:is_tritonir
    echo "This does not appear to be a Triton IR file."
    return
  endif

  " Execute Python logic
  python3 << EOF
if vim.current.buffer.name:
    tritonir.parse_tritonir(vim.current.buffer.name)
    tritonir.open_source_file()
EOF

" Ensure global autocommand is set up once
if !exists('g:tritonir_autocommand_set')
  augroup TritonIRInspector
    autocmd!
    autocmd CursorMoved * python3 tritonir.sync_lines()
  augroup END
  let g:tritonir_autocommand_set = 1
endif
endfunction

command! TritonIRToggle call TritonIRInspector_toggle()

nnoremap <leader>tt :TritonIRToggle<CR>
