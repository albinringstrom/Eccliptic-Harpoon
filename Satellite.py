from http import server
import socket
import time
import subprocess

# Check bottom-ish of the code for the code to open the files in new cmd windows if you want to use that


def tc_accept(var: bool):
    if var:
        groundrecieversocket.send("Telecommand accepted: success\n".encode("utf-8"))
    else:
        groundrecieversocket.send("Telecommand not accepted: failure\n".encode("utf-8"))

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


# Needs change because of modes later, "2" is placeholder
def tc_02_01():
    if mode != 1:   # Check correct mode
        tc_execution(False)
        groundrecieversocket.send("Not in correct mode to execute TC.02.01\n".encode("utf-8"))
        return
    else:   # If correct mode, execute command
        tc_execution(True)
        payloadsocket.send("TC.02.01".encode("utf-8"))  # Send command to payload
        tc_progress(True)
        payloadpower = payloadsocket.recv(1024) # Get response from payload
        payloadpower = payloadpower.decode("utf-8") # Convert bytes to string
        if payloadpower == "1":    # If power is already on, send message to ground reciever
            tc_complete(False)
            groundrecieversocket.send("Payload power already on\n".encode("utf-8"))
        else:                       # If power has been turned on, send message to ground reciever
            tc_complete(True)
            groundrecieversocket.send("Payload power on\n".encode("utf-8"))

# Needs change because of modes later, "2" is placeholder
def tc_02_02():
    if mode != 1:   #Check correct mode
        tc_execution(False)
        groundrecieversocket.send("\nNot in correct mode to execute TC.02.02\n".encode("utf-8"))
        return
    else:   # If correct mode, execute command
        tc_execution(True)  
        payloadsocket.send("TC.02.02".encode("utf-8"))  # Send command to payload
        tc_progress(True)
        payloadpower = payloadsocket.recv(1024) # Get response from payload
        payloadpower = payloadpower.decode("utf-8") # Convert bytes to string
        if payloadpower == "1":   # If power is on, turn it off and send message to ground reciever
            tc_complete(True)
            groundrecieversocket.send("Payload power off\n".encode("utf-8"))
        else:                        # If power is already off, send message to ground reciever
            tc_complete(False)
            groundrecieversocket.send("Payload power already off\n".encode("utf-8"))

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

        print(f"Received: {request1} at {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}\n")
        groundrecieversocket.send(request1.encode("utf-8"))

        match request1:
            case "TC.02.01":
                tc_accept(True)
                tc_02_01()
            case "TC.02.02":
                tc_accept(True)
                tc_02_02()
            case _:
                tc_accept(False)
                payloadsocket.send("Wrong command".encode("utf-8"))

        groundsendersocket.send("\n".encode("utf-8"))

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

# Temporary varible stuff before we finish other stuff
mode = 1

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
file1 = r"C:\Users\rjaco\Documents\Skolgrejs\Eccliptic-Harpoon\Ground_Station_Transmitter.py"
file2 = r"C:\Users\rjaco\Documents\Skolgrejs\Eccliptic-Harpoon\Payload.py"
file3 = r"C:\Users\rjaco\Documents\Skolgrejs\Eccliptic-Harpoon\Ground_Station_Reciever.py"

# Command to open files in new cmd windows
subprocess.Popen(['start', 'cmd', '/k', 'python', file1], shell=True)
subprocess.Popen(['start', 'cmd', '/k', 'python', file2], shell=True)
subprocess.Popen(['start', 'cmd', '/k', 'python', file3], shell=True)


# accept incoming connections
groundsendersocket, groundsenderaddress = groundsender.accept()
print(f"Accepted connection from {groundsenderaddress[0]}:{groundsenderaddress[1]}")
payloadsocket, payloadaddress = payloadserver.accept()
print(f"Accepted connection from {payloadaddress[0]}:{payloadaddress[1]}")
groundrecieversocket, groundrecieveraddress = groundreciever.accept()
print(f"Accepted connection from {groundrecieveraddress[0]}:{groundrecieveraddress[1]}")


run_server()
