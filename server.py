import os
import pty
import select
import paramiko
import socket
from threading import Event

HOST_KEY = paramiko.RSAKey.from_private_key_file('./host.key')  # Read host key from file


class SSHHandler(paramiko.ServerInterface):
    def __init__(self):
        self.event = Event()  # Use threading.Event for synchronization

    # Always allow authentication
    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password,publickey"

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        self.event.set()  # Signal that a shell request has been made
        return True

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        return True


def handle_ssh_connection(client_socket):
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(HOST_KEY)
    server = SSHHandler()

    try:
        transport.start_server(server=server)
    except paramiko.SSHException:
        print("SSH negotiation failed.")
        return

    channel = transport.accept()
    if channel is None:
        print("Client did not open a channel.")
        return

    # Wait for the event to be set (shell request)
    if not server.event.wait(10):  # Use threading.Event's wait method
        print("No shell request from client.")
        return

    # Create a pseudo-terminal for the OCaml application
    pid, fd = pty.fork()
    if pid == 0:
        # Child process: Run the OCaml TUI app
        os.execlp("./_build/default/bin/main.exe", "./_build/default/bin/main.exe")
    else:
        # Parent process: Relay data between SSH and PTY
        try:
            while True:
                read_list, _, _ = select.select([channel, fd], [], [])
                if channel in read_list:
                    data = channel.recv(1024)
                    if not data:
                        break
                    os.write(fd, data)
                if fd in read_list:
                    data = os.read(fd, 1024)
                    if not data:
                        break
                    channel.send(data)
        except Exception as e:
            print(f"Error relaying data: {e}")
        finally:
            channel.close()


def start_ssh_server(host="0.0.0.0", port=2222):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"SSH server listening on {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()  # Added addr to get connection info
        try:
            print(f"New connection from {addr}")
            handle_ssh_connection(client_socket)
        except Exception as e:
            print(f"Error handling connection from {addr}: {e}")
        finally:
            client_socket.close()
            print(f"Connection from {addr} closed")


if __name__ == "__main__":
    start_ssh_server()
