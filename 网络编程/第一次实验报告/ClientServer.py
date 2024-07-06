import socket
import threading
import time

class HeartbeatSender(threading.Thread):
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket

    def run(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data == "HEARTBEAT":
                    self.send_heartbeat_ack()
                elif (len(data) == 0):
                    break
                else :
                    

                    print(f"服务器的群发消息为:{data}")
                
            except Exception as e:
                print(f"Error receiving heartbeat: {e}")
                break

    def send_heartbeat_ack(self):
        try:
            self.client_socket.sendall('HEARTBEAT_ACK'.encode('utf-8'))
        except Exception as e:
            print(f"Failed to send heartbeat ACK: {e}")

def main():
    host = "127.0.0.1"
    port = 12001

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print("Connected to server.")
        heartbeat_sender = HeartbeatSender(client_socket)
        heartbeat_sender.start()

        while True:
            message = input("Enter message to send (type 'quit' to exit): ")
            
            if message == "quit":
                break
                #exit(0)
            
            try:
                client_socket.sendall(message.encode('utf-8'))
            except Exception as e:
                print(f"Failed to send message: {e}")

    except Exception as e:
        print(f"Failed to connect to server: {e}")

    finally:
        print("before close........")
        client_socket.shutdown(socket.SHUT_WR)
        time.sleep(10)

if __name__ == "__main__":
    main()


