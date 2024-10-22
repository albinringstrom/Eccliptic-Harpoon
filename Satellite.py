import socket
import time
import subprocess
import random
import threading
import math


# Check bottom-ish of the code for the code to open the files in new cmd windows if you want to use that

#start time
t0 = time.time()
#localtime or onboard time bool
time_switch = 0
#sequence counter
Seq_count = 0

# ==================================================================================================
# TIME FUNCTIONS
# ==================================================================================================

#generate local time function
def generate_local_time():
    time_local = [time.localtime()[3], time.localtime()[4], time.localtime()[5]]
    return time_local

#generate onboard time function
def generate_onboard_time():
    global t0

    time_now = time.time()
    time_now = math.floor(time_now)
    t_now = time_now - t0
    return t_now

#timetag format function
def sec_to_timetag():

    global time_switch

    if time_switch == 0:
        #use onboardtime
        sec = generate_onboard_time() 
        #separate the h, m and s 
        hours = math.floor(sec/3600)
        minutes = math.floor((sec - hours*3600)/60)
        sec = sec - hours*3600 - minutes*60
    
        #convert the integers to strings
        sec = str(sec)
        minutes = str(minutes)
        hours = str(hours)

    elif time_switch == 1:
        #use localtime
        localtime = generate_local_time()
        #separate the h,m and s
        hours = str(localtime[0])
        minutes = str(localtime[1])
        sec = str(localtime[2])
    #format time
    if len(sec) == 1:
        sec = '0' + sec
    if len(minutes) == 1:
        minutes = '0' + minutes
    if len(hours) == 1:
        hours = '0' + hours

    time = hours + ':' + minutes + ':' +  sec
    return time

# ==================================================================================================
# SCHEDULE FUNCTIONS
# ==================================================================================================

#schedule array function
def schedule_array(request1):
    global schedule
    timetag = tc_timetag(request1)
    tc = tc_telecommand(request1)
    i = len(schedule)
    
    schedule[0].append(tc)
    schedule[1].append(timetag)

#clear schedule function
def clearschedule():
    global schedule
    schedule.clear()
    schedule = [[],[]]

#telecommand timetag extraction function
def tc_timetag(request1):
    timetag = request1[9:]
    return timetag

#telecommand tc extraction function
def tc_telecommand(request1):
    tc = request1[0:8]
    return tc

#comparison of timetag and onboardtime function
def obtime_eq_tag():
    global schedule

    while True:
   
        #take in time
        time = sec_to_timetag()

        for t in range(len(schedule[0])):
            if time == schedule[1][t] or 'XX:XX:XX' == schedule[1][t]:

                command = schedule[0][t]
                schedule[1][t] = ''
                schedule[0][t] = ''

                execute_tc(command)

# ==================================================================================================
# EVENT REPORTING FUNCTION
# ==================================================================================================
left_panel_reported = '0' # Information an anomaly with the left solar panel has already been reported 
right_panel_reported = '0' # Information an anomaly with the left solar panel has already been reported 
Battery_state = 1   
anomaly_check_interval = 10 # How many seconds between anomaly checks
def anomaly_reporting(client_socket):
    
    event_simulation()
    # Detects anomalies and reports what has happened

    
    while True:
        anomaly = "TM.05.01 Event reporting\n"
        anomaly_detected = False
        # Checks if the maximum battery capacity is below a certain tresh hold and reports it
        if battery_max_capacity<50 and battery_state == 1:
            
            anomaly_detected = '1'
            battery_state=2
            
            anomaly = anomaly + (
                f"Max battery capacity is below 50% of the original value and is currently at {battery_max_capacity}\n%."
                )
        elif battery_max_capacity<25 and battery_state == 2:

                anomaly_detected = '1'
                battery_state=3

                anomaly = anomaly + (
                    f"Max battery capacity is below 25% of the original value and is currently at {battery_max_capacity}\n%."
                )
            
    
        #  Checks if the solar panels are working
        if left_solar_panel_status == '0' and left_panel_reported == '0':
            anomaly_detected = '1'

            left_panel_reported = '1' # Sets left_panel_reported to '1' because the anomaly has been reported with the left solar panel

            anomaly = anomaly + (
                "The left solar panel is malfunctioning\n"
            )
        elif left_panel_reported == '1' and left_solar_panel_status == '1':
                anomaly_detected = '1'

                left_panel_reported = '0' # Sets left_panel_problem_reported to '0' because the left solar panel has been reported to function again
                
                anomaly = anomaly + (
                "The left solar panel is functioning again\n"
            )

        if right_solar_panel_status == False and right_panel_reported == False:
            anomaly_detected = '1'

            right_panel_reported = '1' # Sets right_panel_reported to '1' because the anomaly has been reported with the right solar panel
            anomaly = anomaly + (
                "The right solar panel is malfunctioning\n"
            )

        elif right_sps_reported == '1' and right_solar_panel_status == '1':
                anomaly_detected = '1'
                
                right_sps_reported = '0' # Sets right_panel_reported to '0' because the right solar panel has been reported to function again

                anomaly = anomaly + (
                "The right solar panel is functioning again\n"
            )
                
        # Checks if any anomalys have been detected
        if anomaly_detected == '1':
            if time_switch == 1:
                tajm = f"Local time:"
                OB_time = f"{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}"
            else:
                tajm = f"On-Board Time:"
                OB_time = f"{generate_onboard_time()} seconds"
            anomaly = anomaly + (
                f"\t  {tajm} {OB_time}\n"
                f"\t  {generate_onboard_time()}\n"
            )
            client_socket.send(anomaly.encode("utf-8"))
        
        time.sleep(anomaly_check_interval) # How often the satellite will check for anomalys

# ==================================================================================================
# EVENT SIMULATION SETTING
# ==================================================================================================
battery_max_capacity = 100 # Maximum capacity of the battery
right_solar_panel_status = '1'
left_solar_panel_status = '1'
def event_simulation():

    if random.random()>0.994: # the close the number is to 1 the less chance there will be for the solar panel to fail
        right_solar_panel_status = '0'
    else:
        right_solar_panel_status = '1'
    
    if random.random()>0.994:
        left_solar_panel_status = '0'
    else:
        left_solar_panel_status = '1'
    
    # Random chance for the battery to degrade
    if random.random()>0.95:
        battery_max_capacity = battery_max_capacity-random.uniform(1,5)
    
# ==================================================================================================
# BATTERY AND THERMAL DATA FUNCTIONS
# ==================================================================================================

def send_battery_status(client_socket):
    """
    Send battery status at precise intervals.
    """
    while True:
        update_battery_status()
        if time_switch == 1:
            tajm = f"Local time:"
            OB_time = f"{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}"
        else:
            tajm = f"On-Board Time:"
            OB_time = f"{generate_onboard_time()} seconds"
        battery_info = (
            f"TM.03.01 Battery Status:\n"
            f"\t  Percent: {battery_percent:.1f}%\n"
            f"\t  Charging: {is_charging}\n"
            f"\t  {tajm} {OB_time}\n"
            f"\t  {generate_onboard_time()}\n"
        )
        client_socket.send(battery_info.encode("utf-8"))
        time.sleep(battery_update_interval)  # Slower updates

def send_thermal_data(client_socket):
    """
    Send thermal data every 30 seconds.
    """
    while True:
        thermal_data = generate_thermal_data()
        if time_switch == 1:
            tajm = f"Local time:"
            OB_time = f"{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}"
        else:
            tajm = f"On-Board Time:"
            OB_time = f"{generate_onboard_time()} seconds"
        thermal_info = (
            f"TM.03.02 Thermal Data:\n"
            f"\t  Camera: {thermal_data['Camera']}C\n"
            f"\t  CPU: {thermal_data['CPU']}C\n"
            f"\t  PDU: {thermal_data['PDU']}C\n"
            f"\t  {tajm} {OB_time}\n"
            f"\t  {generate_onboard_time()}\n"
        )
        client_socket.send(thermal_info.encode("utf-8"))
        time.sleep(thermal_update_interval)

# ==================================================================================================
# BATTERY SIMULATION SETTINGS
# ==================================================================================================
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

# ==================================================================================================
# THERMAL SIMULATION SETTINGS
# ==================================================================================================

thermal_update_interval = 50  # Time between thermal data updates in seconds

def generate_thermal_data():
    """
    Simulate thermal data for different parts of the spacecraft.
    """
    # Generating realistic temperature ranges in Celsius for different components
    # Internal components: 20C to 40C
    thermal_data = {
        "Camera": round(random.uniform(20, 40), 2),
        "CPU": round(random.uniform(20, 40), 2),
        "PDU": round(random.uniform(20, 40), 2)
    }
    return thermal_data

# ==================================================================================================
# DATA STORAGE STATUS SETTINGS
# ==================================================================================================
storage_update_interval = 50  # Time between storage data updates in seconds
storage_capacity = 10000  # Total storage capacity in MB
reserved_storage = 200  # Initial used storage in MB
used_storage = reserved_storage  # Used storage in MB
image_data_size = 25  # Size of image data in MB

def update_storage_status():
    """
    Simulate data storage status.
    """
    global used_storage
    # Increment used storage
    used_storage = min(storage_capacity, used_storage + image_data_size)
    return used_storage

def reset_storage_status():
    """
    Reset data storage status after sending image data.
    """
    global used_storage
    used_storage = max(0, reserved_storage)

def send_storage_status(client_socket):
    """
    Send data storage status at precise intervals.
    """
    while True:
        used_storage = update_storage_status()
        if time_switch == 1:
            tajm = f"Local time:"
            OB_time = f"{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}"
        else:
            tajm = f"On-Board Time:"
            OB_time = f"{generate_onboard_time()} seconds"
        storage_info = (
            f"TM.03.04 Data Storage Status:\n"
            f"\t  Used Storage: {used_storage:.1f} MB\n"
            f"\t  Total Capacity: {storage_capacity} MB\n"
            f"\t  {tajm} {OB_time}\n"
            f"\t  {generate_onboard_time()}\n"
        )
        client_socket.send(storage_info.encode("utf-8"))
        time.sleep(storage_update_interval)

# ==================================================================================================
# ATTITUDE CONTROL SYSTEM SETTINGS
# ==================================================================================================
attitude_update_interval = 50  # Time between attitude data updates in seconds

def update_attitude_status():
    """
    Simulate attitude control system data.
    """
    # Generating realistic attitude data in degrees for different axes
    attitude_data = {
        "Roll": round(random.uniform(-180, 180), 2),
        "Pitch": round(random.uniform(-90, 90), 2),
        "Yaw": round(random.uniform(-180, 180), 2)
    }
    return attitude_data

def send_attitude_status(client_socket):
    """
    Send attitude status at precise intervals.
    """
    while True:
        attitude_data = update_attitude_status()
        if time_switch == 1:
            tajm = f"Local time:"
            OB_time = f"{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}"
        else:
            tajm = f"On-Board Time:"
            OB_time = f"{generate_onboard_time()} seconds"
        attitude_info = (
            f"TM.03.03 Attitude Status:\n"
            f"\t  Roll: {attitude_data['Roll']} degrees\n"
            f"\t  Pitch: {attitude_data['Pitch']} degrees\n"
            f"\t  Yaw: {attitude_data['Yaw']} degrees\n"
            f"\t  {tajm} {OB_time}\n"
            f"\t  {generate_onboard_time()}\n"
        )
        client_socket.send(attitude_info.encode("utf-8"))
        time.sleep(attitude_update_interval)

# ==================================================================================================
# TELECOMMAND ACCEPT FUNCTIONS
# ==================================================================================================
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

# ==================================================================================================
# TELECOMMAND EXECUTION FUNCTION
# ==================================================================================================

def execute_tc(finalTC):
    global mode
    match finalTC:
        case "TC.02.01":
            tc_accept(True)
            tc_02_01()
        case "TC.02.02":
            tc_accept(True)
            tc_02_02()
        case "TC.02.03":
            tc_accept(True)
            tc_02_03()
        case "TC.02.04":
            tc_accept(True)
            tc_02_04()
        case "TC.09.01":
            tc_accept(True)
            tc_09_01()
        case "TC.09.02":
            tc_accept(True)
            tc_09_02()
        case "TC.11.01":
            tc_accept(True)
            tc_11_01()
        case "TC.11.02":
            tc_accept(True)
            tc_11_02()
        case "TC.13.01":
            tc_accept(True)
            tc_13_01()
        case "TC.18.01":
            tc_accept(True)
            tc_18_01()
            mode = 1
        case "TC.18.02":
            tc_accept(True)
            tc_18_02()
            mode = 1
        case "TC.18.03":
            tc_accept(True)
            tc_18_03()
            mode = 2
        case "TC.18.04":
            tc_accept(True)
            tc_18_04()
            mode = 3
        case "TC.18.05":
            tc_accept(True)
            tc_18_05()
            mode = 4
        case "TC.18.06":
            tc_accept(True)
            tc_18_06()
            mode = 5
        case "TC.69.69":
            tc_accept(True)
            tc_69_69()
        case _:
            tc_accept(False)
            payloadsocket.send("Wrong command".encode("utf-8"))

#===================================================================================================
#==========================================TELECOMMANDS=============================================
# ==================================================================================================
# TC 2: PAYLOAD MANAGEMENT
# ==================================================================================================

#turn on payload command
def tc_02_01():
    global mode
    if mode == 0:   # Check correct mode
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

#turn off payload command
def tc_02_02():
    global mode
    if mode == 0:   #Check correct mode
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

#turn on camera command
def tc_02_03():
    global mode
    if mode == 0:   #Check correct mode
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

#turn off camera command
def tc_02_04():
    global mode
    if mode == 0:   #Check correct mode
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

# ==================================================================================================
# TC 9: TIME MANAGEMENT
# ==================================================================================================

#Switch to local time command
def tc_09_01():
    global mode
    global time_switch

    if time_switch == 0:
        time_switch = 1
    else:
        time_switch = 0

#display onboard time command
def tc_09_02():
    global mode
    global t0

    t_now = generate_onboard_time()
    tstring = f"On-board time: {t_now} seconds"
    groundrecieversocket.send(str(tstring).encode("utf-8"))

# ==================================================================================================
# TC 11: SCHEDULE MANAGEMENT
# ==================================================================================================

#reset command schedule command
def tc_11_01():
    clearschedule()
   
#display command schedule command
def tc_11_02():
    global schedule
    print(schedule)

# ==================================================================================================
# TC 13: LARGE DATA TRANSFER
# ==================================================================================================

#send image data command
def tc_13_01():
    global mode
    if mode != 5:
        tc_execution(False)
        groundrecieversocket.send("Not in correct mode to execute TC.13.01\n".encode("utf-8"))
        return
    else:
        tc_execution(True)
        payloadsocket.send("TC.13.01".encode("utf-8"))
        payloadpower = payloadsocket.recv(1024) # Get payloadpower response from payload
        payloadpower = payloadpower.decode("utf-8") # Convert bytes to string
        if payloadpower == "0":
            tc_progress(False)
            groundrecieversocket.send("Payload power is off, image data transfer unavailable\n".encode("utf-8"))
        else:
            tc_progress(True)
            camerapower = payloadsocket.recv(1024)
            camerapower = camerapower.decode("utf-8")
            if camerapower == "0":
                tc_progress(False)
                groundrecieversocket.send("Camera is off, data transfer unavailable\n".encode("utf-8"))
            else:
                tc_progress(True)
                groundrecieversocket.send("Image data transfer started\n".encode("utf-8"))
                transfer_time = payloadsocket.recv(1024) # Get transfer time from payload
                transfer_time = transfer_time.decode("utf-8") # Convert bytes to string
                time.sleep(math.ceil(float(transfer_time)))
                #for i in range(math.ceil(float(transfer_time))):
                #    image_progress = payloadsocket.recv(1024) # Get image transfer progress from payload
                #    image_progress = image_progress.decode("utf-8") # Convert bytes to string
                #    groundrecieversocket.send(image_progress.encode("utf-8"))
                #image_progress = payloadsocket.recv(1024) # Get image transfer progress from payload
                #image_progress = image_progress.decode("utf-8") # Convert bytes to string
                #groundrecieversocket.send(image_progress.encode("utf-8"))
                reset_storage_status()
                tc_complete(True)
                groundrecieversocket.send('image_sent'.encode("utf-8"))

# ==================================================================================================
# TC 18: MODE MANAGEMENT
# ==================================================================================================

#turn on spacecraft command
def tc_18_01():
    global t0

    global mode
    tc_execution(True)
    yesno = tm_05_03("TC.18.01")

    if mode != 0:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already on\n".encode("utf-8"))
    elif yesno == 0:        
        groundrecieversocket.send("Cancelled command\n".encode("utf-8"))
    else:
        tc_progress(True)
        time.sleep(random.randint(1,10))
        groundrecieversocket.send("Spacecraft on, entering safe mode\n".encode("utf-8"))
        mode = 1

        # Initialize on board time
        t0 = time.time()
        t0 = math.floor(t0)

        tc_complete(True)

        # Start sending housekeeping
        threading.Thread(target=send_battery_status, args=(groundrecieversocket,), daemon=True).start()
        threading.Thread(target=send_thermal_data, args=(groundrecieversocket,), daemon=True).start()

#enter SAFE-Mode command
def tc_18_02():
    global mode
    tc_execution(True)
    yesno = tm_05_03("TC.18.02")

    if mode == 1:
        print(mode)
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in safe mode\n".encode("utf-8"))
    elif yesno == 0:
        groundrecieversocket.send("Cancelled command\n".encode("utf-8"))
    else:
        tc_progress(True)
        time.sleep(random.randint(1,20))
        groundrecieversocket.send("Spacecraft in safe mode\n".encode("utf-8"))
        tc_complete(True)
        mode = 1

#enter MOON-Pointing mode command
def tc_18_03():
    global mode
    tc_execution(True)
    yesno = tm_05_03("TC.18.03")

    if mode == 2:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in moon pointing mode\n".encode("utf-8"))
    elif yesno == 0:
        groundrecieversocket.send("Cancelled command\n".encode("utf-8"))
    else:
        tc_progress(True)
        time.sleep(random.randint(1,20))
        groundrecieversocket.send("Spacecraft in moon pointing mode\n".encode("utf-8"))
        tc_complete(True)
        mode = 2

#enter SUN-Pointing mode command
def tc_18_04():
    global mode
    tc_execution(True)
    yesno = tm_05_03("TC.18.04")

    if mode == 3:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in sun pointing mode\n".encode("utf-8"))
    elif yesno == 0:
        groundrecieversocket.send("Cancelled command\n".encode("utf-8"))
    else:
        tc_progress(True)
        time.sleep(random.randint(1,20))
        groundrecieversocket.send("Spacecraft in sun pointing mode\n".encode("utf-8"))
        tc_complete(True)
        mode = 3

#enter MANOEUVRE mode command
def tc_18_05():
    global mode
    tc_execution(True)
    yesno = tm_05_03("TC.18.05")

    if mode == 4:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in manoeuvre mode\n".encode("utf-8"))
    elif yesno == 0:
        groundrecieversocket.send("Cancelled command\n".encode("utf-8"))
    else:
        tc_progress(True)
        time.sleep(random.randint(1,20))
        groundrecieversocket.send("Spacecraft in manoeuvre mode\n".encode("utf-8"))
        tc_complete(True)
        mode = 4

#enter DATA-Sending mode command
def tc_18_06():
    global mode
    tc_execution(True)
    yesno = tm_05_03("TC.18.06")

    if mode == 5:
        tc_progress(False)
        groundrecieversocket.send("Spacecraft already in data-sending mode\n".encode("utf-8"))
    elif yesno == 0:
        groundrecieversocket.send("Cancelled command\n".encode("utf-8"))
    else:
        tc_progress(True)
        time.sleep(random.randint(1,20))
        groundrecieversocket.send("Spacecraft in data-sending mode\n".encode("utf-8"))
        tc_complete(True)
        mode = 5

#enter secret mode command
def tc_69_69(mode):
    # Use Popen to stream the output line by line
    process = subprocess.Popen(['curl', 'ascii.live/rick'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Continuously read the output and print it as it arrives
    try:
        for line in process.stdout:
            print(line, end='')  # Print each line as it is received
    except KeyboardInterrupt:
        print("\nProcess interrupted.")
    finally:
        process.stdout.close()  # Close the stream when done
        process.wait() # Wait for the process to finish


def tm_05_03(command):
    groundrecieversocket.send(f"Are you sure you want to execute {command}\n Y/N: ".encode("utf-8"))
    groundsendersocket.send(f"Are you sure you want to execute {command}\n Y/N: ".encode("utf-8"))
    confirmation = groundsendersocket.recv(1024)
    confirmation = confirmation.decode("utf-8")
    if confirmation == "Y" or confirmation == "y":
        return 1
    else:
        return 0

#===================================================================================================

# ==================================================================================================
# SERVER FUNCTION
# ==================================================================================================

def run_server():


    global Seq_count, mode, schedule

    mode = 0

    while True:

        request1 = groundsendersocket.recv(1024)
        request1 = request1.decode("utf-8")  # convert bytes to string

        # Sequence stuff
        Seq_count += 1
        Seq_count_ground = request1[17:]
        request1 = request1[0:17]
        


        # if we receive "close" from the client, then we break
        # out of the loop and close the connection
        if request1.lower() == "close":
            # send response to the client which acknowledges that the
            # connection should be closed and break out of the loop
            groundsendersocket.send("closed".encode("utf-8"))
            payloadsocket.send("closed".encode("utf-8"))
            groundrecieversocket.send("closed".encode("utf-8"))
            break

        if request1[0:7] != "discard".upper():
            print(f"Received: {request1} at {time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}\n")
            groundrecieversocket.send(request1.encode("utf-8"))
        if request1[0:7] == "discard".upper():
            groundrecieversocket.send('DISCARDED'.encode("utf-8"))
        elif mode == 0 and request1 != "TC.18.01TXX:XX:XX":
            tc_accept(False)
            groundrecieversocket.send("Satellite not on\n".encode("utf-8"))
        elif str(Seq_count) != str(Seq_count_ground):
            tc_accept(False)
            groundrecieversocket.send("Sequence counter not correct\n".encode("utf-8"))
        else:

            #run schedule function to insert tc and timetag in array
            schedule_array(request1)
            if f"{request1[3]}{request1[4]}" == "18" or f"{request1[3]}{request1[4]}" == '13':
                time.sleep(2)
                

        
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

# ==================================================================================================
# SERVER SETUP
# ==================================================================================================

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
    threading.Thread(target=obtime_eq_tag).start()

schedule = [[],[]]
bootup()

