import configparser
import socket
import threading
import time


bufferlist = []
playerlist = []
itemslist = []
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
    data, addr = s.recvfrom(16384)
    stringdata = data.decode("utf-8")
    #stringdata is in format "msgtype,var1,var2,var3..." 
    #msgtype 
    #1X is for player
    #2X is for items  
    #If stringdata begins with C
    if stringdata[0] == "C":
        globalmessagelist = stringdata.split(";")
        #remove the C
        globalmessagelist[0] = globalmessagelist[0][1:]
        for globalmessage in globalmessagelist:
            messagelist = globalmessage.split(",")
            messagetype = messagelist[0]
            match messagetype:
                case "0":                           #player is moving
                    movePlayer(messagelist[1], messagelist[2], addr)
                case "2":                           #player is moving item
                    moveItem(messagelist[1], messagelist[2], messagelist[3])
                case "10":                          #player connected
                    connectPlayer(messagelist[1], addr)
                case "12":                          #player disconnected
                    disconnectPlayer(messagelist[1])
                case "101":                        #takeCola
                    Station1.takeCola()
            
            for buffer in bufferlist:
                if buffer.addr == addr:
                    buffer.flush()
                    break




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
    bufferlist.append(Buffer(addr))
    for clientplayer in playerlist:
        clientplayer.announceMyself()
    
def disconnectPlayer(UserName):
    print("Player " + UserName + " disconnected")
    for player in playerlist:
        if player.UserName == UserName:
            playerlist.remove(player)
            break

def movePlayer(ID, pos, addr):
    for player in playerlist:
        if player.id == int(ID):
            player.pos = pos
            sendPlayerStatus(addr)
            break

def sendPlayerStatus(addr):
    message = "1,"
    for player in playerlist:
        message += str(player.id) + "," + str(player.pos) + ","
    message = message[:-1]
    sendCommand(message, addr)

def sendCommand(command, addr):
    for buffer in bufferlist:
        if buffer.addr == addr:
            buffer.add(command)
            break

def sendUDP(command, addr):
    s.sendto(command.encode("utf-8"), addr)

def createItem(ItemType, posX, posY, State):
    ItemID = 0
    for i in range(0, 10000):
        if not any(item.id == i for item in itemslist):
            ItemID = i
            break
    match ItemType:
        case "0":
            itemslist.append(Cola(posX, posY)) 
    for clientplayer in playerlist:
        sendCommand("20," + str(ItemID) + "," + ItemType + "," + State, clientplayer.addr)

def destroyItem(ItemID):
    for item in itemslist:
        if item.id == int(ItemID):
            itemslist.remove(item)
            break
    for clientplayer in playerlist:
        sendCommand("21," + ItemID, clientplayer.addr)

def changeItemState(ItemID, NewState):
    for item in itemslist:
        if item.id == int(ItemID):
            item.state = NewState
            break
    for clientplayer in playerlist:
        sendCommand("22," + ItemID + "," + NewState, clientplayer.addr)

def moveItem(ItemID, NewPosX, NewPosY):
    for item in itemslist:
        if item.id == int(ItemID):
            item.posX = int(NewPosX)
            item.posY = int(NewPosY)
            break
    moveItemStatus(ItemID, NewPosX, NewPosY)

def moveItemStatus(ItemID, NewPosX, NewPosY):
    for clientplayer in playerlist:
        sendCommand("3," + str(ItemID) + "," + str(NewPosX) + "," + str(NewPosY), clientplayer.addr)

class Player:
    UserName = ""
    addr = ""
    id = 0
    pos = 0
    def __init__(self, UserName, addr):
        print("Init player " + UserName)
        self.UserName = UserName
        self.addr = addr
        for i in range(0, 1000):
            if not any(player.id == i for player in playerlist):
                self.id = i
                break
    
    def announceMyself(self):
        for clientplayer in playerlist:
            print("Sending 11," + ServerName + "," + str(self.id) + "," + self.UserName + " to " + clientplayer.UserName + " at " + str(clientplayer.addr))
            sendCommand("11," + ServerName + "," + str(self.id) + "," + self.UserName, clientplayer.addr)


class Buffer:
    addr = ""
    buffer = "S"
    def __init__(self, addr):
        self.addr = addr
    def add(self, data):
        if self.buffer == "S":
            self.buffer += data
        else:
            self.buffer += ";" + data

    def flush(self):
        if self.buffer != "S":
            sendUDP(self.buffer, self.addr)
            self.buffer = "S"



#======Items======
#State is a string legth 16 used to store infos about the item
class Item:
    posX = 0
    posY = 0
    id = 0
    state = "0000000000000000"
    def __init__(self, posX, posY, state):
        self.posX = posX
        self.posY = posY
        self.state = state
        for i in range(0, 10000):
            if not any(item.id == i for item in itemslist):
                self.id = i
                break


class Cola(Item): #ID 0
    opened = False
    def __init__(self, posX, posY):
        super().__init__(posX, posY, "0000000000000000")
    def open(self):
        self.opened = True
        self.state = "0000000000000001"


#======Stations======

class SnackStation:
    posX = 21
    def __init__(self, posX):
        self.posX = posX
    def takeCola(self):
        createItem("0", self.posX, 0, "0000000000000000")
        moveItem(itemslist[-1].id, self.posX+0, 0)
        
class counterStation:
    posX = 0
    customerarray = []
    def __init__(self, posX):
        self.posX = posX
        self.customerarray.append(customer("Joe Biden"))

class customer:
    name = ""
    orderarray = []
    def __init__(self, name):
        self.name = name
        self.orderarray.append(menuItem("Cola", 0))
    def giveItem(self, item):
        for i in self.orderarray:
            if i.itemID == item.itemID and i.readyItemState == item.readyItemState:
                self.orderarray.remove(i)
                destroyItem(item.id)
                self.isFinished()
                return True
        return False
    def isFinished(self):
        if len(self.orderarray) == 0:
            
            return True
        else:
            return False

class menuItem:
    name = ""
    itemID = -1
    readyItemState = ""
    def __init__(self, name, itemID):
        self.itemID = itemID
        match itemID:
            case 0:
                self.name = "Cola"
                self.readyItemState = "0000000000000001"


print("the server is starting")
loadConfig()
setupNetwork()
threadkill = threading.Thread(target=qkill, daemon=True).start()
print("Type exit to close the server")
tick_time = time.time()
Station1 = SnackStation(0)
while keep_running:
    tick_time = time.time()
    listenCommand()
    #Calculate tickrate in ms with accuracy 0.1ms and divide by amount of players

    tickrate = round(((time.time() - tick_time) * 1000) * len(playerlist), 1)
    print("Tickrate: " + str(tickrate) + "ms")
