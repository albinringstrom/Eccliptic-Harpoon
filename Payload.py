import socket
import time

# Check if power is on or off
def power_check(power: str):
    if power == "1":    # If power is on, we send "1" to the server
        client.send("1".encode("utf-8"))
    elif power == "0":  # If power is off, we send "0" to the server
        client.send("0".encode("utf-8"))
    else:               # If power is neither on or off, we print an error message
        print("Mega-super error just occured, please no more yoghurt")
    return

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
