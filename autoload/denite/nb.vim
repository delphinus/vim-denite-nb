let g:denite_nb_executable = get(g:, 'denite_nb_executable', 'nb')

function! denite#nb#executable() abort
  if executable(g:denite_nb_executable)
    return g:denite_nb_executable
  endif
  call denite#util#print_error('cannot find `nb` executable')
  return v:null
endfunction
