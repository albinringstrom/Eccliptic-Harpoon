import socket
import time
import numpy as np
import sys

Seq_count = 0

#array containing telecommands
tc_matrix = np.array([['TC.02.01', 'Turn On Payload'],
    ['TC.02.02', 'Turn Off Payload'],
    ['TC.02.03', 'Turn On Camera'],
    ['TC.02.04', 'Turn Off Camera'],
    ['TC.03.01', 'Overall System Health Status Request'],
    ['TC.03.02', 'Change Housekeeping Rate'],
    ['TC.09.01', 'Switch to Local Time'],
    ['TC.09.02', 'Display Onboard Time'],
    ['TC.11.01', 'Reset Command Schedule'],
    ['TC.11.02', 'Delete Specific Command in Schedule'],
    ['TC.11.03', 'Display Schedule'],
    ['TC.13.01', 'Send Image Data'],
    ['TC.18.01', 'Turn on spacecraft'],
    ['TC.18.02', 'Enter SAFE Mode'],
    ['TC.18.03', 'Enter Moon-Pointing Mode'],
    ['TC.18.04', 'Enter Sun-Pointing Mode'],
    ['TC.18.05', 'Enter Manoeuvre Mode'],
    ['TC.18.06', 'Enter Data-Sending Mode'],
    ['TC.69.69', 'Enter Super Mega Death Mode']])


# create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = "127.0.0.1"  # replace with the server's IP address
server_port = 8000  # replace with the server's port number
# establish connection with server
client.connect((server_ip, server_port))

#Function that sends TC to OBC
def sendmessage(TC):
    global Seq_count # Sequence counter
    # input message and send it to the server
    Seq_count += 1
    TC = TC + f"{Seq_count}"
    client.send(TC.encode("utf-8")[:1024])

    #check if confirmation is needed
    if f"{TC[3]}{TC[4]}" == "18":
        response = client.recv(1024)
        response = response.decode("utf-8")
        print(f"Received: {response}")
        confirmation = input()
        client.send(confirmation.encode("utf-8")[:1024])
        return
    else:
        return



#Function that checks if input TC exists
def create_and_validateTC():
    while True:
        print('\nEnter TC:    \nFormat: TC.XX.XX')
        inputTC = input()

        #Option to close program
        if inputTC == 'close':
            sendmessage(inputTC)
            break
        else:
            #convert input to uppercase
            inputTC = inputTC.upper()
            validTC = 0
            for row in tc_matrix:
                validTC = (row == inputTC)
                if validTC[0] == 1:
                    time.sleep(1)
                    print('\n' + inputTC + ' "' + row[1] +'" command')
                    return inputTC

            #if no TC matched:
            print('ERROR: TC not found.')

    client.close()
    print("Connection to server closed rn")
    sys.exit()


def run_client():
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = "127.0.0.1"  # replace with the server's IP address
    server_port = 8000  # replace with the server's port number
    # establish connection with server
    client.connect((server_ip, server_port))

def close_client():
    client.close()
    print("Connection to server closed rn")
    sys.exit()

def execution_time():
    while True:
        #take execution time from user
        print('\nEnter execution time: \nFormat: hh:mm:ss ,\nEnter "discard" to discard TC')
        extime = input()

        if extime == 'discard':
            main()
        else:
            #if format is correct
            try:
                time.strptime(extime, '%H:%M:%S')
                return extime
            #if format is incorrect
            except ValueError:
                print("\nERROR: Invalid time.\n")

def main():
    while True:
        
        #take input TC and validate.
        inputTC = create_and_validateTC()

        #schedule TC?
        time.sleep(0.5)
        print('\nSchedule execution of command?\n')
        exflag = input('Y/N?')
        exflag = exflag.upper()
        if exflag == 'Y':
            extime = execution_time()
        else:
            extime = 'XX:XX:XX'
        #confirm TC before sending
        print('\nDo you want to send: ' + inputTC +'T'+ extime +'?\n' )
        confirmTC = input('Y/N?')
        confirmTC = confirmTC.upper()
        if confirmTC == 'Y':
            time.sleep(0.5)
            print('\n' + inputTC +', ' + extime + ' confirmed.')
            
            #Format TC to send
            TC = inputTC +'T'+ extime

            #call send function
            sendmessage(TC)
        else:
            print('\n' +inputTC +', ' + extime + ' discarded.')
            sendmessage("Discard".upper())

        # receive message from the server
        response = client.recv(1024)
        response = response.decode("utf-8")

        # if server sent us "closed" in the payload, we break out of the loop and close our socket
        if response.lower() == "closed":
            break

    # close client socket (connection to the server)
    client.close()
    print("Connection to server closed rn")

#set up client
run_client()
#run main
main()