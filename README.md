# tui-blog

proof of concept of running tui app via ssh

## build ocaml
1. `opam switch create . 5.2.0 -y --deps-only` 
2. `eval $(opam env)`
3. `opam exec -- dune build`

1. `pipenv shell`
2. `python server.py`


