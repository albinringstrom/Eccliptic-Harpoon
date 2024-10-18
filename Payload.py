import socket
import time

# Check if power is on or off
def power_check(power: str):
    if power == "1":
        client.send("1".encode("utf-8"))
    elif power == "0":
        client.send("0".encode("utf-8"))
    else:
        print("Mega-super error just occured, please no more yoghurt")
    return

def run_client():

    power = "1"

    while True:

        # receive message from the server
        TCommand = client.recv(1024)
        TCommand = TCommand.decode("utf-8")

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if TCommand.lower() == "closed":
            break

        print(f"Received: {TCommand}")

        #print(mode)

        match TCommand:
            case "TC.02.01":   #Power on
                power_check(power)
                power = "1"
            case "TC.02.02":   #Power off
                power_check(power)
                power = "0"



    # close client socket (connection to the server)
    client.close()
    print("Connection to server closed")

# Temporary varible stuff before we finish other stuff


# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = "127.0.0.1"  # replace with the server's IP address
server_port = 9000  # replace with the server's port number
# establish connection with server
client.connect((server_ip, server_port))

print("Payload online")

run_client()
