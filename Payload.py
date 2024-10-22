import socket
import time
import random

# Check if power is on or off
def power_check(power: str):
    if power == "1":    # If power is on, we send "1" to the server
        client.send("1".encode("utf-8"))
    elif power == "0":  # If power is off, we send "0" to the server
        client.send("0".encode("utf-8"))
    else:               # If power is neither on or off, we print an error message
        print("Mega-super error just occured, please no more yoghurt")
    return


# Send an image to the server
def image_send():
    transferred = 0
    transfer_rate = random.randint(5, 10) # Random transfer rate between 5 and 10 MB/s
    file_size = random.randint(30, 50)     # Random file size between 30 and 50 MB
    client.send(str('').encode("utf-8"))
    client.send(str(file_size/transfer_rate).encode("utf-8")) # Send the time it takes to transfer the image to the server
    #while transferred < file_size:
    #    client.send(f"Transferred {transferred:.2f}/{file_size} MB ({(transferred/file_size)*100:.2f}%)".encode("utf-8"))
    #    transferred = transferred + transfer_rate
    #    time.sleep(1)
    #client.send(f"Transferred {file_size:.2f}/{file_size} MB ({(file_size/file_size)*100:.2f}%)".encode("utf-8"))
        

def run_client():

    power = "0"         # Power is off by default
    camera_power = "0"  # Camera is off by default

    while True:

        # receive message from the server
        TCommand = client.recv(1024)
        TCommand = TCommand.decode("utf-8")

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if TCommand.lower() == "closed":
            break

        print(f"Received: {TCommand}")

        match TCommand:
            case "TC.02.01":   # Power on
                power_check(power)
                power = "1"
            case "TC.02.02":   # Power off
                power_check(power)
                power = "0"
                camera_power = "0"
            case "TC.02.03":    # Camera on
                power_check(power)
                if power == "1":    # Only if power is on do we check if camera is on/off
                    power_check(camera_power)
                    camera_power = "1"                
            case "TC.02.04":    # Camera off
                power_check(power)
                if power == "1":    # Only if power is on do we check if camera is on/off
                    power_check(camera_power)
                    camera_power = "0"
            case "TC.13.01":
                power_check(power)
                if power == "1":
                    power_check(camera_power)
                    if camera_power == "1":
                        image_send()
                    
    # close client socket (connection to the server)
    client.close()
    print("Connection to server closed")


# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = "127.0.0.1"  # replace with the server's IP address
server_port = 9000  # replace with the server's port number
# establish connection with server
client.connect((server_ip, server_port))

# To see that payload is online, can be removed if not fitting
print("Payload online")

run_client()
