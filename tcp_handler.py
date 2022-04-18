from logging.config import stopListening
import socket, sys
from enum import Enum
class MsgType(Enum):
    MSG = 1
    ACK = 2
    NUM = 3

class Package:
    ID = "|.|"

    def __init__ (self, cmd, param, msg):
        self.cmd = cmd
        self.param = param
        self.msg = msg

    def get_request(self):
        return f"{Package.ID}{self.cmd.value}{Package.ID}{self.param}{Package.ID}{self.msg}{Package.ID}"

class TCPHandler:
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
            cmd = ""
            param = ""
            buf = ""
            read_cmd = False
            read_msg = False
            read_param = False
            c.settimeout(5)
            while self.Listening:
                try:
                    data = c.recv(1)
                except:
                    continue

                if read_msg:
                    msg += data.decode()
                elif read_cmd:
                    cmd += data.decode()
                elif read_param:
                    param += data.decode()
                else:
                    buf += data.decode()

                if buf.startswith(Package.ID):
                    read_cmd = True
                    buf = ""
                elif cmd.endswith(Package.ID):
                    read_cmd = False
                    read_param = True
                    cmd = cmd[0:-3]
                elif param.endswith(Package.ID):
                    read_param = False
                    read_msg = True
                    param = param[0:-3]
                elif msg.endswith(Package.ID):
                    read_msg = False
                    msg = msg[0:-3]
                    pck = Package(MsgType(int(cmd)), param, msg)
                    self.Received.append(pck)
                    msg = ""
                    cmd = ""
                    param = ""
                
            c.close()
    
    def try_connect(self):
        if self.is_connected():
            return False
            
        self.Connected = not self.Client.connect_ex(("localhost", self.ClientPort))
        return self.Connected

    def is_connected(self):
        return self.Connected

    def get_message_parts(self, msg):
        parts = []
        while len(msg) > 0:
            if len(msg) <= TCPHandler.MAX_BUF:
                parts.append(msg)
                break
            else:
                parts.append(msg[0:TCPHandler.MAX_BUF - 1])
                msg = msg[TCPHandler.MAX_BUF:]

        return parts

    def send_message(self, message):
        parts = self.get_message_parts(message)
        numPack = Package(MsgType.NUM, len(parts), "")
        self.send_package(numPack)
        i = 0
        for p in parts:
            pack = Package(MsgType.MSG, i, p)
            self.send_package(pack)
            i += 1

    def send_package(self, package):
        self.Client.send(package.get_request().encode())

    def disconnect(self):
        if self.is_connected:
            self.Client.close()
            self.Connected = False
            return True
        
        return False

    def recv(self):
        if len(self.Received) > 0:
            if self.Received[0].cmd != MsgType.NUM:
                return None

            count = int(self.Received[0].param)
            current = 0
            indexes = []
            while current < count:
                i = 0
                for p in self.Received:
                    if p.cmd == MsgType.MSG and int(p.param) == current:
                        indexes.append(i)
                        break
                    i += 1
                current += 1

            if (len(indexes) == count):
                msg = ""
                for index in indexes:
                    msg += self.Received[index].msg

                for i in range(len(indexes) + 1):
                    self.Received.pop(0)

                return msg

        return None
