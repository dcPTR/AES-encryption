from time import sleep
from tcp_handler import MsgType, TCPHandler, Package

class MessageSender():

    def get_message_parts(self, msg):
        parts = []
        count = len(msg) / TCPHandler.MAX_BUF
        if len(msg) % TCPHandler.MAX_BUF != 0:
            count += 1

        while len(parts) < count:
            if len(msg) <= TCPHandler.MAX_BUF:
                parts.append(msg)
                break
            else:
                parts.append(msg[len(parts) * TCPHandler.MAX_BUF:len(parts) * TCPHandler.MAX_BUF + TCPHandler.MAX_BUF])

        return parts

    def send_message(self, tcp, messageBytes, fileName="", gui=None):
        # self.exchange_public_key()
        msg = bytearray(messageBytes)
        parts = self.get_message_parts(msg)
        n = len(parts)
        numPack = Package(MsgType.NUM, n, bytearray(f"{fileName}".encode()))
        tcp.send_package(numPack)

        for i, p in enumerate(parts):
            sleep(0.01)
            pack = Package(MsgType.MSG, i, p)
            tcp.send_package(pack)
            if gui is not None:
                gui.update_progress(i, n - 1)