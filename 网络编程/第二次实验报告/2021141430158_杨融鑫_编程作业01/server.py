import socket
import struct
import threading
import json

def load_users():
    try:
        with open("C:\\Users\\杨融鑫\\Desktop\\users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open("C:\\Users\\杨融鑫\\Desktop\\users.json", "w") as file:
        json.dump(users, file)

def handle_registration_request(data):
    # 处理注册请求消息
    username, password = struct.unpack("!20s30s", data)
    username = username.decode().strip()
    password = password.decode().strip()
    
    users = load_users()  # 从文件中加载用户信息
    
    if username in users:
        return struct.pack("!I", 2) + struct.pack("!c64s", b'\x00', b"Username already exists.")
    else:
        # 保存新用户信息
        users[username] = password
        save_users(users)  # 将用户信息保存到文件中
        return struct.pack("!I", 2) + struct.pack("!c64s", b'\x01', b"Registration successful.")

def handle_login_request(data):
    # 处理登录请求消息
    username, password = struct.unpack("!20s30s", data)
    username = username.decode().strip()
    password = password.decode().strip()
    
    users = load_users()  # 从文件中加载用户信息
    
    
    
    if username in users and users[username] == password:
        return struct.pack("!I", 4) + struct.pack("!c64s", b'\x01', b"Login successful.")
    else:
        return struct.pack("!I", 4) + struct.pack("!c64s", b'\x00', b"Username or password is incorrect.")

def handle_client_connection(conn):
    with conn:
        while True:
            # 接收消息头
            header = conn.recv(4)
            if not header:
                break
            total_length = struct.unpack("!I", header)[0]
            # 接收消息体
            data = conn.recv(total_length - 4)
            command_id = struct.unpack("!I", data[:4])[0]
            if command_id == 1:  # 注册请求消息
                response = handle_registration_request(data[4:])
            elif command_id == 3:  # 登录请求消息
                response = handle_login_request(data[4:])
            else:
                response = struct.pack("!I", 4) + struct.pack("!c64s", b'\x00', b"Invalid command ID.")
            response_bytes = response
            length = len(response_bytes)
            total_length = 4 + length
            header = struct.pack("!I", total_length)
            conn.sendall(header+response_bytes)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 8888))
        s.listen()
        print("Server is listening on port 8888...")
        while True:
            conn, addr = s.accept()
            print("Connected to", addr)
            # 为每个客户端连接创建一个新的线程
            client_thread = threading.Thread(target=handle_client_connection, args=(conn,))
            client_thread.start()

if __name__ == "__main__":
    start_server()
