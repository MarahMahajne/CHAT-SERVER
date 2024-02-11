import socket
import threading

# Define server settings
SERVER_IP = '127.0.0.1'  # Replace with the actual server IP address
SERVER_PORT = 31554  # Replace with the actual server port
MAX_CONNECTIONS = 10

# Dictionary to store user information (token, username)
users = {}


def handle_client(client_socket):
    try:
        while True:
            # Receive the message from the client
            data = client_socket.recv(1024)  # Adjust buffer size as needed
            if not data:
                break

            # Parse the message
            message_number = int.from_bytes(data[0:2], byteorder='big')
            message_length = int.from_bytes(data[2:6], byteorder='big')
            user_token = data[6:16].decode().strip('\x00')

            if message_number == 50:  # Hello message
                username = data[16:].decode().strip('\x00')
                users[user_token] = username
                response = f"Hello, {username}!"
            elif message_number == 51:  # List Users message
                user_type = int.from_bytes(data[16:18], byteorder='big')
                filter_text = data[18:].decode().strip('\x00')
                # Implement logic to list users based on user_type and filter_text
                response = "List Users response"
            elif message_number == 52:  # Message User message
                target_user = data[16:48].decode().strip('\x00')
                message_content = data[48:].decode().strip('\x00')
                # Implement logic to send a message to the target_user
                response = "Message sent"
            elif message_number == 53:  # Authorize message
                # Implement logic to generate an authorization code
                auth_code = "1234567890"  # Replace with a generated code
                response = f"Authorization code: {auth_code}"
            elif message_number == 54:  # Broadcast message
                auth_token = data[16:26].decode().strip('\x00')
                message_content = data[26:].decode().strip('\x00')
                # Implement logic to broadcast the message to all users
                response = "Broadcast sent"
            elif message_number == 99:  # Exit message
                exit_code = data[16:36].decode().strip('\x00')
                # Implement logic to handle client exit
                response = "Exit handled"
            else:
                response = "Invalid message"

            # Send a response back to the client
            client_socket.send(response.encode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the client socket
        client_socket.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(MAX_CONNECTIONS)

    print(f"Listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    main()
