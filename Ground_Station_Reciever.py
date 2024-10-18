import socket
import time

def openImage():
    # Imports PIL module
    from PIL import Image

    # open method used to open different extension image file
    im = Image.open(r"C:\Users\albin\Pictures\moon1.png")

    # This method will show image in any image viewer
    im.show()


def run_client():
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "127.0.0.1"  # replace with the server's IP address
    server_port = 10000  # replace with the server's port number
    # establish connection with server
    client.connect((server_ip, server_port))

    while True:
        # input message and send it to the server

        # receive message from the server
        response = client.recv(1024)
        response = response.decode("utf-8")

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if response.lower() == "closed":
            break

        print(f"Received: {response}")
        openImage()

        

    # close client socket (connection to the server)
    client.close()
    print("Connection to server closed")


run_client()
