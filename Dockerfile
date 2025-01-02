# Build stage
FROM ocaml/opam:debian-ocaml-5.1 AS builder

# Install system dependencies
RUN sudo apt-get update && sudo apt-get install -y m4 pkg-config

# Copy your project files and set permissions
COPY . /app/
WORKDIR /app
RUN sudo chown -R opam:opam /app

# Install OCaml dependencies and build
RUN opam install . --deps-only 
RUN opam exec -- dune build


# Make the executable runnable
RUN sudo chmod +x /app/_build/default/bin/main.exe


# Run the executable
CMD ["/app/_build/default/bin/main.exe"]
