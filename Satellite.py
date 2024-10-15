import socket
import time


def run_server():

    server1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "127.0.0.1"
    port1 = 8000
    port2 = 9000

    server1.bind((server_ip, port1))
    server2.bind((server_ip, port2))

    server1.listen(0)
    print(f"Listening on {server_ip}:{port1}")
    server2.listen(0)
    print(f"Listening on {server_ip}:{port2}")

    # accept incoming connections
    client_socket1, client_address1 = server1.accept()
    print(f"Accepted connection from {client_address1[0]}:{client_address1[1]}")
    client_socket2, client_address2 = server2.accept()
    print(f"Accepted connection from {client_address2[0]}:{client_address2[1]}")

    while True:
        request1 = client_socket1.recv(1024)
        request1 = request1.decode("utf-8")  # convert bytes to string

        # if we receive "close" from the client, then we break
        # out of the loop and close the connection
        if request1.lower() == "close":
            # send response to the client which acknowledges that the
            # connection should be closed and break out of the loop
            client_socket1.send("closed".encode("utf-8"))
            client_socket2.send("closed".encode("utf-8"))
            break

        print(f"Received: {request1} at {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}")

        if request1 == "poop":
            response1 = "yes please".encode("utf-8")  # convert string to bytes
            response2 = "yes pleaseeee".encode("utf-8")
        elif request1 == "not poop":
            response1 = "aaahh shit".encode("utf-8")
            response2 = "no shit sherlock".encode("utf-8")
        else:
            response1 = "not a valid command srry man".encode("utf-8")
            response2 = "the fuck u on about".encode("utf-8")
        client_socket1.send(response1)
        client_socket2.send(response2)

    # close connection socket with the client
    client_socket1.close()
    print("Connection to client1 closed")
    client_socket2.close()
    print("Connection to client2 closed")
    # close server1 socket
    server1.close()
    server2.close()


run_server()
