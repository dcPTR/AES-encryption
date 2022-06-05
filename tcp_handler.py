# from logging.config import stopListening
import socket, sys
from enum import Enum
from time import sleep


class MsgType(Enum):
    MSG = 1
    ACK = 2
    NUM = 3


class Package:
    CMD_BYTES = 16
    PARAM_BYTES = 64

    def __init__(self, cmd, param="", msg=bytearray(0)):
        self.cmd = cmd
        self.param = param
        self.msg = msg

    def get_request(self):
        cmd_bytes = bytearray(str(self.cmd.value).encode())
        while len(cmd_bytes) < Package.CMD_BYTES:
            cmd_bytes = bytearray('0'.encode()) + cmd_bytes

        param_bytes = bytearray(str(self.param).encode())
        while len(param_bytes) < Package.PARAM_BYTES:
            param_bytes = bytearray('0'.encode()) + param_bytes
            
        while len(self.msg) < TCPHandler.MAX_BUF:
            self.msg = bytearray('0'.encode()) + self.msg
            
        return cmd_bytes + param_bytes + self.msg

class TCPHandler():
    MAX_BUF = 64512#4096 * 8

    def __init__(self, serverPort, clientPort):
        self.ServerPort = serverPort
        self.ClientPort = clientPort
        self.Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Connected = False
        self.Listening = True
        self.JustAcknowledged = False
        self.Received = []

    def connectAckListener(self, method):
        self.ack_signal.connect(method)

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
            
            c.settimeout(5)
            prevData = ""
            while self.Listening:
                try:
                    data = c.recv(TCPHandler.MAX_BUF + Package.CMD_BYTES + Package.PARAM_BYTES, socket.MSG_WAITALL)
                except Exception as e:
                    print(f"exc {e}")
                    continue
                
                print(f"recv {data[0:Package.CMD_BYTES]} {data[Package.CMD_BYTES:Package.CMD_BYTES + Package.PARAM_BYTES]} {len(data)}")
                cmd_b = data[0:Package.CMD_BYTES]
                cmd = cmd_b.decode()
                param = data[Package.CMD_BYTES:Package.CMD_BYTES + Package.PARAM_BYTES].decode()
                msg = data[Package.CMD_BYTES + Package.PARAM_BYTES:]
                pck = Package(MsgType(int(cmd)), param, msg)
                self.Received.append(pck)

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
        count = len(msg) / TCPHandler.MAX_BUF
        if len(msg) % TCPHandler.MAX_BUF != 0:
            count += 1

        while len(parts) < count:
            if (len(parts) % 100 == 0):
                print(f"parts: {len(parts)} {count}")
            if len(msg) <= TCPHandler.MAX_BUF:
                parts.append(msg)
                break
            else:
                parts.append(msg[len(parts) * TCPHandler.MAX_BUF:len(parts) * TCPHandler.MAX_BUF + TCPHandler.MAX_BUF])

        return parts

    def send_message(self, messageBytes, fileName=""):
        msg = bytearray(messageBytes)
        parts = self.get_message_parts(msg)
        numPack = Package(MsgType.NUM, len(parts), bytearray(f"{fileName}".encode()))
        self.send_package(numPack)
        i = 0
        for p in parts:
            sleep(0.01)
            pack = Package(MsgType.MSG, i, p)
            self.send_package(pack)
            i += 1

    def send_package(self, package):
        self.Client.send(package.get_request())

    def disconnect(self):
        if self.is_connected:
            self.Client.close()
            self.Connected = False
            return True

        return False

    def hasJustAcknowledged(self):
        return self.JustAcknowledged

    def recv(self):
        self.JustAcknowledged = False
        if len(self.Received) > 0:
            if self.handleAckMessages():
                return (None, None)
            if self.Received[0].cmd != MsgType.NUM:
                return (None, None)

            partsCount = int(self.Received[0].param)
            fileName = self.Received[0].msg.decode()
            indexes = self.collectMessagePartsIndexes(partsCount)
            
            if (len(indexes) == partsCount):
                self.sendAck()
                return (self.joinMessageAndPop(indexes), fileName)

        return (None, None)

    def handleAckMessages(self):
        if self.Received[0].cmd == MsgType.ACK:
            self.JustAcknowledged = True
            self.Received.pop(0)
            return True

        return False

    def collectMessagePartsIndexes(self, count):
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

        return indexes

    def sendAck(self):
        pck = Package(MsgType.ACK)
        self.send_package(pck)

    def joinMessageAndPop(self, indexes):
        msg = bytearray(0)
        for index in indexes:
            msg += self.Received[index].msg

        for i in range(len(indexes) + 1):
            self.Received.pop(0)
        return msg