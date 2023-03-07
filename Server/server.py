import configparser
import socket
import threading
import time

def loadConfig():
    global Maxplayers, ServerName, Password
    config = configparser.ConfigParser()
    config.read('config.ini')
    Maxplayers = config['DEFAULT']['MaxPlayers']
    print("Max Players = " + Maxplayers)
    ServerName = config['DEFAULT']['ServerName']
    print("Server Name = " + ServerName)
    Password = config['DEFAULT']['Password']
    print("Password = " + Password)

def setupNetwork():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", 1008))
    print("Server is listening on port 1008")

def listenCommand():
    data, addr = s.recvfrom(1024)
    stringdata = data.decode("utf-8")
    #stringdata is in format "msgtype,var1,var2,var3..." 
    #msgtype 
    #1X is for player
    #2X is for economy
    messagelist = stringdata.split(",")
    messagetype = messagelist[0]
    match messagetype:
        case "10":                          #player connected
            connectPlayer(messagelist[1], addr)
        
    time.sleep(0.1)


def sendCommand(command, addr):
    s.sendto(command.encode("utf-8"), addr)

def qkill():
    global keep_running
    keep_running = True
    while True:
        if input() == "exit":
            keep_running = False
            s.close()
            print("server is closing")

def connectPlayer(UserName, addr):
    print("Player " + UserName + " connected")
    playerlist.append(Player(UserName, addr))
    



class Player:
    UserName = ""
    addr = ""
    id = 0
    pos = 0
    def __init__(self, UserName, addr):
        self.UserName = UserName
        self.addr = addr
        for i in range(0, 1000):
            for player in playerlist:
                if player.id == i:
                    break
            id = i
        sendCommand("11," + ServerName + "," + self.id + "," + self.UserName, addr)
    



print("the server is starting")
loadConfig()
setupNetwork()
threadkill = threading.Thread(target=qkill, daemon=True).start()
print("Type exit to close the server")
playerlist = []
while keep_running:
    listenCommand()