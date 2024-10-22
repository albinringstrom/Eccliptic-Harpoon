import socket
import time

# Clear housekeeping data
f = open(r"Housekeeping_Log.txt", "w")
f.write('')
f.close()
# =========================
# Open Image Function
# =========================


#def openImage():
#    # Imports PIL module
#    from PIL import Image
#    import numpy as np
#    import random
#    #array of pictures
#    moonimages = np.array([[r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143648.png"], 
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143648.png"], 
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143712.png"], 
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143721.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143806.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143846.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143906.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143916.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143926.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143936.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143943.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 143953.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 144003.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 144015.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 144149.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 144235.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 144246.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 144321.png"],
#        [r"C:\Users\albin\Pictures\MOON_SURFACE\Screenshot 2024-10-18 144333.png",]])
#
# open method used to open different extension image file
#    randomimage = random.randint(0, len(moonimages))
#    im = Image.open(moonimages[randomimage])
#
#    # This method will show image in any image viewer
#    im.show()


# =========================
# Client Function
# =========================

def run_client():
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "127.0.0.1"  # replace with the server's IP address
    server_port = 10000  # replace with the server's port number
    # establish connection with server
    client.connect((server_ip, server_port))

    print("Reciever online")

    while True:
        # input message and send it to the server

        # receive message from the server
        response = client.recv(1024)
        response = response.decode("utf-8")

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if response.lower() == "closed":
            break

        # openImage()

        if response[0:5] != "TM.03":
            print(f"Received: {response}")

        # unreadable code that works
        check_word = f"{response.rsplit(' ', 2)[0]}"
        if response[0:5] == "TM.03":
            print(f"{response.rsplit(' ', 1)[0]}")
            if check_word[-3] == "s":
                f = open(r"Housekeeping_Log.txt", "a")
                f.write(response.rsplit(' ', 1)[0])
                f.close()
            else:
                f = open(r"Housekeeping_Log.txt", "a")
                word = f"{response.rsplit(' ', 1)[0]} On-Board Time: {response.rsplit(' ', 1)[1]}\n"
                f.write(word)
                f.close()


    # close client socket (connection to the server)
    client.close()
    print("Connection to server closed")


run_client()
