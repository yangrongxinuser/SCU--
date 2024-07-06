import socket
import threading
import time
 #region 
# class NodeA:
#     def __init__(self, host, port, file_path, B_host, B_port):
#         self.host = host
#         self.port = port
#         self.file_path = file_path
#         self.B_host = B_host
#         self.B_port = B_port
#         self.file_content = b''
#         self.connections = []
#         self.file_downloaded = False

#     def start_server(self):
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.bind((self.host, self.port))
#         self.server.listen(5)
#         print(f'Node A server started on {self.host}:{self.port}')

#         while True:
#             conn, addr = self.server.accept()
#             print(f'Node A client connected from {addr}')
#             self.connections.append(conn)
#             threading.Thread(target=self.handle_client, args=(conn,)).start()

#     def handle_client(self, conn):
#         try:
#             if not self.file_downloaded:
#                 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                     s.connect((self.B_host, self.B_port))
#                     with open(self.file_path, 'wb') as file:
#                         while True:
#                             data = s.recv(1024)
#                             if not data:
#                                 break
#                             file.write(data)
#                             conn.sendall(data)
#                     self.file_downloaded = True
#             else:
#                 with open(self.file_path, 'rb') as file:
#                     while True:
#                         data = file.read(1024)
#                         if not data:
#                             break
#                         conn.sendall(data)
#         except Exception as e:
#             print(f'Error: {e}')
#         finally:
#             conn.close()

#     def run(self):
#         threading.Thread(target=self.start_server).start()
#endregion 
class NodeA:
    def __init__(self, host, port, file_path, B_host, B_port):
        self.host = host
        self.port = port
        self.file_path = file_path
        
        self.B_host = B_host
        self.B_port = B_port
        self.file_content = b''
        self.connections = []
        self.file_downloaded_event = threading.Event()

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f'Node A server started on {self.host}:{self.port}')

        while True:
            conn, addr = self.server.accept()
            print(f'Node A client connected from {addr}')
            self.connections.append(conn)
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def handle_client(self, conn):
        try:
            # Wait until the file is downloaded
            self.file_downloaded_event.wait()

            # Send the file to the client
            with open(self.file_path, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    conn.sendall(data)
        except Exception as e:
            print(f'Error: {e}')
        finally:
            conn.close()

    def download_file_from_B(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.B_host, self.B_port))
                with open(self.file_path, 'wb') as file:
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        file.write(data)
                       
                # Set the event to signal that the file is fully downloaded
                self.file_downloaded_event.set()
        except Exception as e:
            print(f'Error: {e}')

    def run(self):
        threading.Thread(target=self.start_server).start()
        threading.Thread(target=self.download_file_from_B).start()
    

class NodeC:
    def __init__(self, host, port, file_path):
        self.host = host
        self.port = port
        self.file_path = file_path

    def download_file(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                with open(self.file_path, 'wb') as file:
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        file.write(data)
        except Exception as e:
            print(f'Error: {e}')

    def run(self):
        threading.Thread(target=self.download_file).start()

class NodeB:
    def __init__(self, host, port, file_path):
        self.host = host
        self.port = port
        self.file_path = file_path

    def start_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.bind((self.host, self.port))
                server.listen(5)
                print(f'Node B server started on {self.host}:{self.port}')

                while True:
                    conn, addr = server.accept()
                    print(f'Node B client connected from {addr}')
                    threading.Thread(target=self.handle_client, args=(conn,)).start()
        except Exception as e:
            print(f'Error: {e}')

    def handle_client(self, conn):
        try:
            with open(self.file_path, 'rb') as file:
                while True:
                    data = file.read(1024)
                    if not data:
                        break
                    conn.sendall(data)
        except Exception as e:
            print(f'Error: {e}')
        finally:
            conn.close()

    def run(self):
        threading.Thread(target=self.start_server).start()

if __name__ == "__main__":
    A_host = '127.0.0.1'
    A_port = 8888
    B_host = '127.0.0.1'
    B_port = 9999
    # C_host = '127.0.0.1'
    # C_port = 7777

    node_a = NodeA(A_host, A_port, 'file_to.txt', B_host, B_port)
    node_b = NodeB(B_host, B_port, 'file_to_share.txt')
    node_c = NodeC(A_host, A_port,'download_file_1.txt')
    node_d = NodeC(A_host, A_port,'download_file_2.txt')
    node_e = NodeC(A_host, A_port,'download_file_3.txt')

    node_b.run()
    node_a.run()
    
    node_c.run()
   
    node_d.run()
    node_e.run()
