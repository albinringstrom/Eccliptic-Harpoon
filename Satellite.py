import socket
import time
import subprocess

# Check bottom-ish of the code for the code to open the files in new cmd windows if you want to use that


def tc_accept(var: bool):
    if var:
        groundrecieversocket.send("Telecommand accepted: success".encode("utf-8"))
    else:
        groundrecieversocket.send("Telecommand not accepted: failure".encode("utf-8"))

def tc_execution(var: bool):
    if var:
        groundrecieversocket.send("Telecommand executed: success".encode("utf-8"))
    else:
        groundrecieversocket.send("Telecommand not executed: failure".encode("utf-8"))

def tc_progress(var: bool):
    if var:
        groundrecieversocket.send("Telecommand in progress: success".encode("utf-8"))
    else:
        groundrecieversocket.send("Telecommand not in progress: failure".encode("utf-8"))

def tc_complete(var: bool):
    if var:
        groundrecieversocket.send("Telecommand completed: success".encode("utf-8"))
    else:
        groundrecieversocket.send("Telecommand not completed: failure".encode("utf-8"))




def run_server():

    while True:
        request1 = groundsendersocket.recv(1024)
        request1 = request1.decode("utf-8")  # convert bytes to string

        # if we receive "close" from the client, then we break
        # out of the loop and close the connection
        if request1.lower() == "close":
            # send response to the client which acknowledges that the
            # connection should be closed and break out of the loop
            groundsendersocket.send("closed".encode("utf-8"))
            payloadsocket.send("closed".encode("utf-8"))
            groundrecieversocket.send("closed".encode("utf-8"))
            break

        print(f"Received: {request1} at {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}")

        if request1 == "poop":
            response1 = "yes please".encode("utf-8")  # convert string to bytes
            response2 = "yes pleaseeee".encode("utf-8")
            tc_accept(True)
        elif request1 == "not poop":
            response1 = "aaahh shit".encode("utf-8")
            response2 = "no shit sherlock".encode("utf-8")
        else:
            response1 = "not a valid command srry man".encode("utf-8")
            response2 = "the fuck u on about".encode("utf-8")
        groundsendersocket.send(response1)
        groundrecieversocket.send(response1)
        payloadsocket.send(response2)

    # close connection socket with the client
    groundsendersocket.close()
    print("Connection to client1 closed")
    payloadsocket.close()
    print("Connection to client2 closed")
    groundrecieversocket.close()
    print("Connection to client3 closed")
    # close server1 socket
    groundsender.close()
    payloadserver.close()
    groundreciever.close()



groundsender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
payloadserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
groundreciever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = "127.0.0.1"
groundsendport = 8000
payloadport = 9000
groundrecieveport = 10000

groundsender.bind((server_ip, groundsendport))
payloadserver.bind((server_ip, payloadport))
groundreciever.bind((server_ip, groundrecieveport))

groundsender.listen(0)
print(f"Listening on {server_ip}:{groundsendport}")
payloadserver.listen(0)
print(f"Listening on {server_ip}:{payloadport}")
groundreciever.listen(0)
print(f"Listening on {server_ip}:{groundrecieveport}")


# This is the code to open the files in new cmd windows
# If you want to use, change file names to the names on your computer
# Otherwise just comment out the code, and open the files manually
  
# Paths to the files you want to open
#file1 = r"C:\Users\rjaco\Documents\Skolgrejs\Eccliptic-Harpoon\Ground_Station_Transmitter.py"
#file2 = r"C:\Users\rjaco\Documents\Skolgrejs\Eccliptic-Harpoon\Payload.py"
#file3 = r"C:\Users\rjaco\Documents\Skolgrejs\Eccliptic-Harpoon\Ground_Station_Reciever.py"

# Command to open files in new cmd windows
#subprocess.Popen(['start', 'cmd', '/k', 'python', file1], shell=True)
#subprocess.Popen(['start', 'cmd', '/k', 'python', file2], shell=True)
#subprocess.Popen(['start', 'cmd', '/k', 'python', file3], shell=True)


# accept incoming connections
groundsendersocket, groundsenderaddress = groundsender.accept()
print(f"Accepted connection from {groundsenderaddress[0]}:{groundsenderaddress[1]}")
payloadsocket, payloadaddress = payloadserver.accept()
print(f"Accepted connection from {payloadaddress[0]}:{payloadaddress[1]}")
groundrecieversocket, groundrecieveraddress = groundreciever.accept()
print(f"Accepted connection from {groundrecieveraddress[0]}:{groundrecieveraddress[1]}")


run_server()
