# Start with an OCaml image
FROM ocaml/opam:debian-12-ocaml-5.1

# Install system dependencies
RUN sudo apt-get update && sudo apt-get install -y \
    libev-dev \
    pkg-config \
    m4 \
    && sudo rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install project dependencies and build
RUN opam install . --deps-only --with-test
RUN opam exec -- dune build

# Set the entrypoint
ENTRYPOINT ["opam", "exec", "--", "dune", "exec", "tui_blog"]
