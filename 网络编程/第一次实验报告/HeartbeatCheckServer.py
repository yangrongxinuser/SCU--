import socket
import threading
import time

class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address, server):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.server = server
        self.last_response = time.time()

    def run(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    if data == "HEARTBEAT_ACK":
                        self.last_response = time.time()
                    elif (len(data) == 0):
                        break

                    else:
                        print(f"Received from {self.client_address}: {data}")
                    
                else:
                    # If no data is received, it means the client has closed the connection
                    break
            except:
                # Exception occurred, likely client closed connection abruptly
                break
        self.client_socket.close()
        self.server.disconnect_client(self)

class MessageManager(threading.Thread):
    def __init__(self, server, lock):
        threading.Thread.__init__(self)
        self.server = server
        self.lock = lock

    def run(self):
        while True:
            self.send_message()

    def send_message(self):
        message = input("Enter message to send: ")
        with self.lock:
            for client_thread in self.server.client_threads[:]:
                try:
                    client_thread.client_socket.sendall(message.encode('utf-8'))
                except:
                    self.server.disconnect_client(client_thread)

class HeartbeatManager(threading.Thread):
    def __init__(self, server, lock):
        threading.Thread.__init__(self)
        self.server = server
        self.lock = lock
        self.interval = 10000  # 每10秒检查一次

    def run(self):
        while True:
            time.sleep(self.interval)
            self.send_heartbeats()
            self.check_heartbeats()

    def send_heartbeats(self):
        with self.lock:
            for client_thread in self.server.client_threads[:]:
                try:
                    client_thread.client_socket.sendall(b'HEARTBEAT')
                except:
                    self.server.disconnect_client(client_thread)

    def check_heartbeats(self):
        current_time = time.time()
        with self.lock:
            for client_thread in self.server.client_threads[:]:
                if current_time - client_thread.last_response > 20:  # 20秒未响应
                    self.server.disconnect_client(client_thread)

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_threads = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.lock = threading.Lock()  # 创建线程锁
        # 启动心跳管理线程
        self.heartbeat_manager = HeartbeatManager(self, self.lock)
        self.heartbeat_manager.start()
        # 启动群发消息线程
        self.message_manager = MessageManager(self, self.lock)
        self.message_manager.start()

    def run(self):
        print(f"Listening on {self.host}:{self.port}")
        while True:
            # 接收新连接
            client_socket, client_address = self.server_socket.accept()
            new_thread = ClientThread(client_socket, client_address, self)
            new_thread.start()
            with self.lock:
                self.client_threads.append(new_thread)

    def disconnect_client(self, client_thread):
        print(f"Disconnecting client {client_thread.client_address}")
        client_thread.client_socket.close()
        with self.lock:
            self.client_threads.remove(client_thread)

# Start the server
if __name__ == "__main__":
    server = Server("127.0.0.1", 12001)
    server.run()

