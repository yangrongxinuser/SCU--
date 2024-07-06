import socket
import struct
import time

def send_message(sock, message):
    # 将消息转换为字节流，并发送
    message_bytes = message
    length = len(message_bytes)
    # 消息总长度为消息体长度加上消息头长度
    total_length = 4 + length
    header = struct.pack("!I", total_length)
    sock.sendall(header + message_bytes)

def receive_message(sock):
    # 接收消息
    header = sock.recv(8)
    total_length, command_id = struct.unpack("!II", header)
    message_body = sock.recv(total_length - 8)
    return message_body.decode()

def register(username, password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", 8888))
        # 构造注册请求消息
        message = f"{username.zfill(20)}{password.zfill(30)}"
        send_message(sock, struct.pack("!I", 1) + message.encode())
        response = receive_message(sock)
        print("Registration response:", response)

def login(username, password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("localhost", 8888))
        # 构造登录请求消息
        message = f"{username.zfill(20)}{password.zfill(30)}"
        send_message(sock, struct.pack("!I", 3) + message.encode())
        response = receive_message(sock)
        print("Login response:", response)

if __name__ == "__main__":
    # 示例注册和登录
    register("user1", "password1")
    time.sleep(1)
    login("user1", "password1")
