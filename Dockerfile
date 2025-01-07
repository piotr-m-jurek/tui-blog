# Build stage
FROM ocaml/opam:debian-ocaml-5.1 AS builder

RUN sudo apt-get update && sudo apt-get install -y m4 pkg-config openssh-server neovim

COPY . /app/
WORKDIR /app
RUN sudo chown -R opam:opam /app

RUN sudo ssh-keygen -A

RUN sudo mkdir /run/sshd
RUN sudo chmod 0755 /run/sshd

# replace prepared config
RUN sudo mv -f /app/sshd_config /etc/ssh/sshd_config

# add user for testing login
RUN sudo useradd -ms /bin/bash tester && \
    sudo echo "tester:password" | sudo chpasswd



# Install OCaml dependencies and build
RUN opam install . --deps-only 
RUN opam exec -- dune build


# Make the executable runnable
RUN sudo chmod +x /app/_build/default/bin/main.exe
# Run the executable
# CMD ["sudo", "/usr/sbin/sshd", "-d"]
