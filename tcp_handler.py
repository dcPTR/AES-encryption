from logging.config import stopListening
import socket, sys

class TCPHandler:
    ID = "|.|"
    MAX_BUF = 8192

    def __init__(self, serverPort, clientPort):
        self.ServerPort = serverPort
        self.ClientPort = clientPort
        self.Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Connected = False
        self.Listening = True
        self.Received = []

    def stop_listen(self):
        self.Listening = False

    def is_listening(self):
        return self.Listening

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", self.ServerPort))
        server.listen()
        server.settimeout(5)

        while self.Listening:
            try:
                c, addr = server.accept()
            except:
                continue
            msg = ""
            buf = ""
            read_msg = False
            c.settimeout(5)
            while self.Listening:
                try:
                    data = c.recv(1)
                except:
                    continue

                if read_msg:
                    msg += data.decode()
                else:
                    buf += data.decode()

                if buf.startswith(TCPHandler.ID):
                    read_msg = True
                    buf = ""
                elif msg.endswith(TCPHandler.ID):
                    read_msg = False
                    self.Received.append(msg[0:-3])
                    msg = ""
                
            c.close()
    
    def try_connect(self):
        if self.is_connected():
            return False
            
        self.Connected = not self.Client.connect_ex(("localhost", self.ClientPort))
        return self.Connected

    def is_connected(self):
        return self.Connected

    def send(self, message):
        self.Client.send(f"{TCPHandler.ID}{message}{TCPHandler.ID}".encode())

    def disconnect(self):
        if self.is_connected:
            self.Client.close()
            self.Connected = False
            return True
        
        return False

    def recv(self):
        if len(self.Received) > 0:
            return self.Received.pop()

        return ""

"""
from threading import Thread

def print_receive(tcp):
    msg = tcp.recv()
    if len(msg) > 0:
        print(f"received {msg}")

tcp = TCPHandler(int(input("server port: ")), int(input("client port: ")))
thread = Thread(target = tcp.listen)
thread.start()

while True:
    msg = input("press any key to connect or x to exit")
    if msg == "x":
        break

    if tcp.try_connect():
        while True:
            msg = input("type message to send or r to receive or x to exit")
            if msg == "x":
                break

            if msg == "r":
                print_receive(tcp)

            tcp.send(msg)

tcp.stop_listen()
thread.join()
"""