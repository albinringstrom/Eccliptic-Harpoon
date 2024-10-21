from http import server
import sched
import socket
import time
import subprocess
import random
import threading
from urllib import request
import numpy as np

# Check bottom-ish of the code for the code to open the files in new cmd windows if you want to use that

# =========================
# Schedule Array Function
# =========================
def schedule_array(request1,i):
    timetag = tc_timetag(request1)
    tc = tc_telecommand(request1)
    
    schedule_array = [['commands'], ['timetags']]
    schedule_array[0][i] = tc
    schedule_array[1][i] = timetag

    i += 1
    return schedule_array

# =========================
# Telecommand Time Tag Extraction Function
# =========================
def tc_timetag(request1):
    timetag = request1[9:]
    print('timetag = ' + timetag)
    return timetag

# =========================
# Telecommand TC Extraction Function
# =========================
def tc_telecommand(request1):
    tc = request1[0:8]
    print('tc = ' + tc)
    return tc

# =========================
# Comparison of timetag and onboardtime Function
# =========================
def obtime_eq_tag():
    global schedule

    #take in onboard time
    OBT = onboard_time()
    onboardtimestring = OBT[1]

    while True:
        for t in schedule[1]:
            if onboardtimestring == schedule[1][i]:
                execute_tc(schedule[0][i])
                
                
            
        
def execute_tc():
    match finalTC:
    case "TC.02.01":
        tc_accept(True)
        tc_02_01(mode)
    case "TC.02.02":
        tc_accept(True)
        tc_02_02(mode)
    case "TC.02.03":
        tc_accept(True)
        tc_02_03(mode)
    case "TC.02.04":
        tc_accept(True)
        tc_02_04(mode)
    case "TC.18.01":
        tc_accept(True)
        tc_18_01(mode)
        mode = 1
    case "TC.18.02":
        tc_accept(True)
        tc_18_02(mode)
        mode = 1
        print(mode)
    case "TC.18.03TXX:XX:XX":
        tc_accept(True)
        tc_18_03(mode)
        mode = 2
        print(mode)
    case "TC.18.04TXX:XX:XX":
        tc_accept(True)
        tc_18_04(mode)
        mode = 3
    case "TC.18.05TXX:XX:XX":
        tc_accept(True)
        tc_18_05(mode)
        mode = 4
    case "TC.18.06TXX:XX:XX":
        tc_accept(True)
        tc_18_06(mode)
        mode = 5
    case _:
        tc_accept(False)
        payloadsocket.send("Wrong command".encode("utf-8"))


    

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
        groundrecieversocket.send("Telecommand execution started: success\n".encode("utf-8"))
    else:
        groundrecieversocket.send("Telecommand not executed: failure\n".encode("utf-8"))

def tc_progress(var: bool):
    if var:
        groundrecieversocket.send("Telecommand in progress: success\n".encode("utf-8"))
    else:
        groundrecieversocket.send("Telecommand not in progress: failure\n".encode("utf-8"))

def tc_complete(var: bool):
    if var:
        groundrecieversocket.send("Telecommand completed: success\n".encode("utf-8"))
    else:
        groundrecieversocket.send("Telecommand not completed: failure\n".encode("utf-8"))

# =========================
# Battery Simulation Settings
# =========================
battery_percent = random.randint(40, 80)  # Initial battery percentage
is_charging = False  # Initial charging state
charge_interval = random.randint(10, 30)  # Duration for charging
battery_update_interval = 50  # Time between status updates every 10 seconds

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
thermal_update_interval = 50  # Time between thermal data updates in seconds

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
def tc_02_01(mode):
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
def tc_02_02(mode):
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

# Needs change because of modes later, "1" is placeholder
def tc_02_03(mode):
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

# Needs change because of modes later, "1" is placeholder
def tc_02_04(mode):
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
# Telecommand mode Functions
# =========================

def tc_18_01(mode):
    tc_execution(True)
    if mode != 0:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already on\n".encode("utf-8"))
    else:
        tc_progress(True)
        groundrecieversocket.send("Spacecraft on, entering safe mode\n".encode("utf-8"))
        tc_complete(True)
        threading.Thread(target=send_battery_status, args=(groundrecieversocket,), daemon=True).start()
        threading.Thread(target=send_thermal_data, args=(groundrecieversocket,), daemon=True).start()
        
def tc_18_02(mode):
    tc_execution(True)
    if mode == 1:
        print(mode)
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in safe mode\n".encode("utf-8"))
    else:
        tc_progress(True)
        groundrecieversocket.send("Spacecraft in safe mode\n".encode("utf-8"))
        tc_complete(True)

def tc_18_03(mode):
    tc_execution(True)
    if mode == 2:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in moon pointing mode\n".encode("utf-8"))
    else:
        tc_progress(True)
        groundrecieversocket.send("Spacecraft in moon pointing mode\n".encode("utf-8"))
        tc_complete(True)

def tc_18_04(mode):
    tc_execution(True)
    if mode == 3:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in sun pointing mode\n".encode("utf-8"))
    else:
        tc_progress(True)
        groundrecieversocket.send("Spacecraft in sun pointing mode\n".encode("utf-8"))
        tc_complete(True)

def tc_18_05(mode):
    tc_execution(True)
    if mode == 4:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in manoeuvre mode\n".encode("utf-8"))
    else:
        tc_progress(True)
        groundrecieversocket.send("Spacecraft in manoeuvre mode\n".encode("utf-8"))
        tc_complete(True)

def tc_18_06(mode):
    tc_execution(True)
    if mode == 5:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in data-sending mode\n".encode("utf-8"))
    else:
        tc_progress(True)
        groundrecieversocket.send("Spacecraft in data-sending mode\n".encode("utf-8"))
        tc_complete(True)

# =========================
# Onboard time function
# =========================

def onboard_time():
    onboardtime = [time.localtime()[3]-starttime[0],time.localtime()[4]-starttime[1],time.localtime()[5]-starttime[2]]
    for i in [1,2]:
        if onboardtime[i] < 0:
            onboardtime[i] += 60
            onboardtime[i-1] -= 1

    #take each element of integer array and conv to str
    onboardhour = str(onboardtime[0])
    onboardminute = str(onboardtime[1])
    onboardsecond = str(onboardtime[2])

    #add a 0 beforevalue if length == 1
    if len(onboardhour) == 1:
        onboardhour = '0' + onboardhour
    if len(onboardminute) == 1:
        onboardminute = '0' + onboardminute
    if len(onboardsecond) == 1:
        onboardsecond = '0' + onboardsecond

    #convert to correct format XX:XX:XX
    onboardtimestring = onboardhour + ':' + onboardminute + ':' +  onboardsecond 
    #return array with onboardtime int array and string
    OBT = [onboardtime, onboardtimestring]
    return OBT



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

    mode = 0
    #initial value for schedule_array
    schedule = []
    i = 0

    

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

        if request1 != "discard".upper():
            print(f"Received: {request1} at {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}\n")
            groundrecieversocket.send(request1.encode("utf-8"))
        
        if request1 == "discard".upper():
            discard = 0
        elif mode == 0 and request1 != "TC.18.01TXX:XX:XX":
            tc_accept(False)
            groundrecieversocket.send("Satellite not on\n".encode("utf-8"))
        else:
            #run schedule function to insert tc and timetag in array
            schedule = schedule_array(request1, i)
            #Supposed to return the command to run
            finalTC = obtime_eq_tag(schedule)


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

starttime = [time.localtime()[3],time.localtime()[4],time.localtime()[5]]

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

def bootup():
    threading.Thread(target=run_server).start()

bootup()
