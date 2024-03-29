import socket
import threading
import time

class Player:
    UserName = ""
    addr = ""
    id = 0
    pos = 0
    b_s = None
    def __init__(self, UserName, addr, playerlist):
        print("Init player " + UserName)
        self.UserName = UserName
        self.addr = addr
        for i in range(0, 1000):
            if not any(player.id == i for player in playerlist):
                self.id = i
                break
        print("Added player " + UserName + " with id " + str(self.id))
        self.b_s = BufferSender(addr)
    def getBufferSender(self):
        return self.b_s
        

class BufferSender:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    outbox = []
    addr = None
    def __init__(self, addr):
        self.addr = addr
        threading.Thread(target=self.send, daemon=True).start()
    
    def send(self):
        while True:
            messageString = "S"
            while len(messageString) < 16384:
                if(len(self.outbox) == 0 and messageString != "S"):
                    break
                if(len(self.outbox) != 0):
                    if(messageString != "S"):
                        messageString += ";"    
                    messageString += self.outbox.pop(0).getString()
            print("Sending " + messageString + " to " + str(self.addr))
            self.s.sendto(messageString.encode("utf-8"), self.addr)
            messageString = ""
            threading.wait(1/20)


    def put(self, message):
        print("Putting " + message.getString() + " in outbox")
        self.outbox.append(message)
