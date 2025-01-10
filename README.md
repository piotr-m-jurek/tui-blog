# tui-blog

proof of concept of running tui app via ssh

## build ocaml
1. `opam switch create . 5.2.0 -y --deps-only` 
2. `eval $(opam env)`
3. `opam exec -- dune build`

## run server

1. get python shell and install dependencies
```python
pipenv shell
```
2. run server. This step assumes that you've build the tui before that
```python
python server.py
```

## connect to via ssh

```sh
ssh -p 2222 localhost
```

