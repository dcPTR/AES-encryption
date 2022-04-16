import socket, sys

class TCPHandler:
    ID = "|.|"

    def __init__(self, serverPort, clientPort):
        self.ServerPort = serverPort
        self.ClientPort = clientPort
        self.Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Connected = False
        self.Received = []

    def listen(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", self.ServerPort))
        server.listen()

        while True:
            c, addr = server.accept()
            msg = ""
            buf = ""
            read_msg = False
            while True:
                data = c.recv(1)
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
        
        try:
            self.Client.connect(("localhost", self.ClientPort))
        except:
            self.Connected = False
            
        self.Connected = True
        return self.Connected

    def is_connected(self):
        return self.Connected

    def send(self, message):
        self.Client.send(f"{TCPHandler.ID}{message}{TCPHandler.ID}".encode())

    def disconnect(self):
        if self.is_connected:
            self.Client.close()

    def recv(self):
        if len(self.Received) > 0:
            return self.Received.pop(0)

        return ""


from threading import Thread

def print_receives(tcp):
    while True:
        msg = tcp.recv()
        if len(msg) > 0:
            print(f"received {msg}")

tcp = TCPHandler(int(input("server port: ")), int(input("client port: ")))
thread = Thread(target = tcp.listen)
thread.start()
thread2 = Thread(target = print_receives, args=(tcp,))
thread2.start()

while True:
    msg = input("press any key to connect or x to exit")
    if msg == "x":
        break

    if tcp.try_connect():
        while True:
            msg = input("type message to send or x to exit")
            if msg == "x":
                break

            tcp.send(msg)

thread2.join()
thread.join()