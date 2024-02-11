import socket
import struct

SERVER_IP = '127.0.0.1'
SERVER_PORT = 31554
AUTHORIZATION_PORT = 31555
NOTIFICATION_PORT = 31556


def send_message(socket, message, response=True):
    socket.sendall(message)
    if response:
        response = socket.recv(1024)
        return response
    return


def send_hello(socket, username):
    message_number = 50
    user_name = username.ljust(32)
    message_length = len(user_name) + 6
    hello_message = struct.pack("!h i 32s", message_number, message_length, user_name)
    hello_response = send_message(socket, hello_message)
    return hello_response


def send_list_users(socket, token):
    message_number = 71
    user_type = 3
    filter = "".ljust(32).encode('utf-8')
    maseege_length = len(filter) + len(token) + 6 + 2
    list_users_message = struct.pack("! h i h 10s 32s", message_number, maseege_length, user_type, token, filter)
    response = send_message(socket, list_users_message)
    return response


def send_message_user(socket, token, target_user, message):
    message_number = 84
    message_length = len(target_user) + len(message) + 14
    target_user_bytes = target_user.encode('utf-8').ljust(32)
    message_bytes = message.encode('utf-8')
    massage_user_massage = struct.pack("! h i 10s 32s 20s", message_number, message_length, token,
                                       target_user_bytes, message_bytes)
    send_message(socket, massage_user_massage, False)
    print("message: " + '"' + message + '" ' + "sent to: " + target_user)


def send_authorize(authorization_socket, token):
    message_number = 50
    message_length = len(token) + 2
    authorization_message = struct.pack("! h 10s", message_number, token)
    response = send_message(authorization_socket, authorization_message)
    return response


def send_broadcast(authorization_socket, user_token, auth_token, message):
    message_number = 21
    token = user_token
    auth_token = auth_token
    message_bytes = message.encode()
    message_length = len(message_bytes) + 20
    broadcast_message = struct.pack("! h i 10s 10s 34s", message_number, message_length, user_token, auth_token,
                                    message_bytes)
    send_message(authorization_socket, broadcast_message, False)


def send_notification(notification_socket, notification_type, exit_code):
    notification_payload = exit_code.encode('utf-8')
    notification_message = struct.pack("! h 20s", notification_type)
    send_message(notification_socket, notification_message, False)


def receive_notifications(client_socket, token, notification_type):
    print("Client is listening for notifications...")

    while True:
        notification_payload ="This Is My Exit Code"
        if notification_type == 1:
            print(f"Received Notification (Type {notification_type}):" + notification_payload)
            send_exit(client_socket, token, notification_payload)
            break

def notification_endpoint(server_ip, notification_port, server_port):
    notification_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    notification_socket.bind((server_ip, notification_port))

    print("[+] Notification Endpoint is running...")
    notification_type = 1
    notification_type = str(notification_type)
    notification_payload ="This Is My Exit Code"
    notification = notification_type.encode()
    notification_socket.close()
    return 1

def send_exit(client_socket, user_token, exit_code):
    message_number = 99
    message_length = len(user_token) + len(exit_code) + 4
    exit_code = exit_code.encode()
    exit_message = struct.pack("! h i 10s 20s", message_number, message_length, user_token, exit_code)
    send_message(client_socket, exit_message, False)


if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    # hello
    # ---------------------------------------------------------------------------
    user_name = "username".ljust(32).encode('utf-8')
    print("[+] Sending hello message:")
    hello_response = send_hello(client_socket, user_name)
    print()
    print("[+] Recived a hello message!")
    message_number, response_length, token = struct.unpack('!h i 10s', hello_response[:16])
    num_messages = (response_length - 16) // 202
    print("Message Number:", message_number)
    print("Response Length:", response_length)
    print("Token:", token)

    for i in range(num_messages):
        message_descriptor = struct.unpack("! h 200s", hello_response[16 + i * 202:16 + (i + 1) * 202])
        message_id, message_content = message_descriptor
        print()
        if i == 0:
            users_list_massage_number = message_id
        elif i == 1:
            massage_user_massage_number = message_id
        elif i == 2:
            broadcast_massage_number = message_id

        print("Message", i + 1, "ID:", message_id, "Message", i + 1, "Content:", message_content.decode('utf-8'))

    # list users
    # ---------------------------------------------------------------------------
    print()
    print("[+] Sending a users list message:")
    list_users_response = send_list_users(client_socket, token)
    print()
    print("[+] Received users list response:")
    message_number, response_length, user_type = struct.unpack('!h i h ', list_users_response[:8])
    print("Message Number:", message_number)
    print("Response Length:", response_length)
    print("User type:", user_type)
    num_users = (response_length - 6) // 32
    print("num_users: ", num_users)
    users = list_users_response[6:]
    print("list_of_users:")
    for i in range(num_users):
        start = i * 32
        end = start + 32
        user = str(users[start:end].strip().decode("utf-8"))
        if i == 2:
            user3 = user
        print(i + 1, ":", user, end=" ")
        print()

    # Message User
    # ---------------------------------------------------------------------------
    target_user = user3
    message = "Hi how are you " + target_user + " ?"
    print()
    print("[+] Sending message user:")
    send_message_user(client_socket, token, target_user, message)

    # Authorization
    # ---------------------------------------------------------------------------
    authorization_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    authorization_socket.connect((SERVER_IP, AUTHORIZATION_PORT))
    print("[+] Making an authorization:")
    print()
    authorization_response = send_authorize(authorization_socket, token)
    print("[+] Authorization succeeded!")
    message_number, authorization_code = struct.unpack('!h 10s ', authorization_response)
    print("Authorization_code: " + authorization_code.decode('utf-8'))

    # Broadcast
    # --------------------------------------------------------------------------
    print()
    message = "Hi everyone, welcome to the group!"
    print("[+] Broadcasting your message:")
    send_broadcast(authorization_socket, token, authorization_code, message)
    print('[+] Your message: "' + message + '" was broadcasted!')

    authorization_socket.close()

    # notification endpoint
    # ---------------------------------------------------------------------------
    notification_type =  notification_endpoint(SERVER_IP, NOTIFICATION_PORT, SERVER_PORT)
    print("[+] lisining to the notification server:")
    receive_notifications(client_socket,token,notification_type)
    client_socket.close()
