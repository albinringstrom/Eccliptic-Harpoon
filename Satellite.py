from http import server
import socket
import time
import subprocess
import random
import threading

# Check bottom-ish of the code for the code to open the files in new cmd windows if you want to use that


# =========================
# Telecommand Acception Functions
# =========================

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

# =========================
# Battery Simulation Settings
# =========================
battery_percent = random.randint(40, 80)  # Initial battery percentage
is_charging = False  # Initial charging state
charge_interval = random.randint(10, 30)  # Duration for charging
battery_update_interval = 10  # Time between status updates every 10 seconds

def update_battery_status():
    """
    Update battery status based on charging state.
    """
    global battery_percent, is_charging, charge_interval

    change_rate = round(random.uniform(0.01, 1), 2)  # Random change rate for battery status

    # Random chance to stop charging while charging
    if is_charging and random.random() < 0.1:  # 10% chance to stop charging
        is_charging = False

    if is_charging:
        battery_percent = min(100, battery_percent + change_rate)
        charge_interval -= 1
        if charge_interval <= 0:
            is_charging = False  # Stop charging after the interval
    else:
        battery_percent = max(1, battery_percent - change_rate)
        # Randomly decide to start charging again
        if random.random() < 0.25:  # 25% chance to start charging
            is_charging = True
            charge_interval = random.randint(10, 30)

# =========================
# Thermal Simulation Settings
# =========================
thermal_update_interval = 30  # Time between thermal data updates in seconds

def generate_thermal_data():
    """
    Simulate thermal data for different parts of the spacecraft.
    """
    # Generating realistic temperature ranges in Celsius for different components
    # External surface in sunlight: 100C to 120C
    # External surface in shadow: -170C to -120C
    # Internal components: 20C to 40C
    thermal_data = {
        "external_sunlit_surface": round(random.uniform(100, 120), 2),
        "external_shadow_surface": round(random.uniform(-170, -120), 2),
        "internal_component_1": round(random.uniform(20, 40), 2),
        "internal_component_2": round(random.uniform(20, 40), 2)
    }
    return thermal_data

# =========================
# Telecommand power on/off Functions
# =========================

# Needs change because of modes later, "1" is placeholder
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

# Needs change because of modes later, "1" is placeholder
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

# =========================
# Telecommand camera on/off Functions
# =========================

def tc_02_03():
    if mode != 1:   #Check correct mode
        tc_execution(False)
        groundrecieversocket.send("\nNot in correct mode to execute TC.02.03\n".encode("utf-8"))
        return
    else:   # If correct mode, execute command
        tc_execution(True)  
        payloadsocket.send("TC.02.03".encode("utf-8"))  # Send command to payload
        payloadpower = payloadsocket.recv(1024) # Get payloadpower response from payload
        payloadpower = payloadpower.decode("utf-8") # Convert bytes to string
        if payloadpower == "0":   
            tc_progress(False)
            groundrecieversocket.send("Payload power is off, camera unavailable\n".encode("utf-8"))
        else:                        
            tc_progress(True)
            camerapower = payloadsocket.recv(1024) # Get camerapower response from payload
            camerapower = camerapower.decode("utf-8") # Convert bytes to string
            if camerapower == "0":   # If camera is off, turn it on and send message to ground reciever
                tc_complete(True)
                groundrecieversocket.send("Camera on\n".encode("utf-8"))
            else:                       
                tc_complete(False)  # If camera is already on, send message to ground reciever
                groundrecieversocket.send("Camera already on\n".encode("utf-8"))

def tc_02_04():
    if mode != 1:   #Check correct mode
        tc_execution(False)
        groundrecieversocket.send("\nNot in correct mode to execute TC.02.04\n".encode("utf-8"))
        return
    else:   # If correct mode, execute command
        tc_execution(True)  
        payloadsocket.send("TC.02.04".encode("utf-8"))  # Send command to payload
        payloadpower = payloadsocket.recv(1024) # Get payloadpower response from payload
        payloadpower = payloadpower.decode("utf-8") # Convert bytes to string
        if payloadpower == "0":   
            tc_progress(False)
            groundrecieversocket.send("Payload power is off, camera unavailable\n".encode("utf-8"))
        else:                        
            tc_progress(True)
            camerapower = payloadsocket.recv(1024) # Get camerapower response from payload
            camerapower = camerapower.decode("utf-8") # Convert bytes to string
            if camerapower == "1":   # If camera is on, turn it off and send message to ground reciever
                tc_complete(True)
                groundrecieversocket.send("Camera off\n".encode("utf-8"))
            else:                       
                tc_complete(False)  # If camera is already off, send message to ground reciever
                groundrecieversocket.send("Camera already off\n".encode("utf-8"))



# =========================
# Battery and Thermal Data Functions
# =========================

def send_battery_status(client_socket):
    """
    Send battery status at precise intervals.
    """
    while True:
        update_battery_status()
        battery_info = (
            f"TM.03.01 Battery Status:\n"
            f"\tPercent: {battery_percent:.1f}%\n"
            f"\tCharging: {is_charging}\n"
        )
        client_socket.send(battery_info.encode("utf-8"))
        time.sleep(battery_update_interval)  # Slower updates

def send_thermal_data(client_socket):
    """
    Send thermal data every 30 seconds.
    """
    while True:
        thermal_data = generate_thermal_data()
        thermal_info = (
            f"TM.03.02 Thermal Data:\n"
            f"\t  External Sunlit Surface: {thermal_data['external_sunlit_surface']}C\n"
            f"\t  External Shadow Surface: {thermal_data['external_shadow_surface']}C\n"
            f"\t  Internal Component 1: {thermal_data['internal_component_1']}C\n"
            f"\t  Internal Component 2: {thermal_data['internal_component_2']}C\n"
        )
        client_socket.send(thermal_info.encode("utf-8"))
        time.sleep(thermal_update_interval)

# =========================
# Server Function
# =========================

def run_server():

    threading.Thread(target=send_battery_status, args=(groundrecieversocket,), daemon=True).start()
    threading.Thread(target=send_thermal_data, args=(groundrecieversocket,), daemon=True).start()

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
            case "TC.02.01TXX:XX:XX":
                tc_accept(True)
                tc_02_01()
            case "TC.02.02TXX:XX:XX":
                tc_accept(True)
                tc_02_02()
            case "TC.02.03TXX:XX:XX":
                tc_accept(True)
                tc_02_03()
            case "TC.02.04TXX:XX:XX":
                tc_accept(True)
                tc_02_04()
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

# =========================
# Server Setup
# =========================

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
