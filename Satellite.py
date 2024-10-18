import socket
import time
import random
import threading

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

def run_server():
    server_ip = "127.0.0.1"
    groundsendport = 8000
    payloadport = 9000
    groundrecieveport = 10000

    groundsender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    payloadserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    groundreciever = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    groundsender.bind((server_ip, groundsendport))
    payloadserver.bind((server_ip, payloadport))
    groundreciever.bind((server_ip, groundrecieveport))

    groundsender.listen(0)
    print(f"Listening on {server_ip}:{groundsendport}")
    payloadserver.listen(0)
    print(f"Listening on {server_ip}:{payloadport}")
    groundreciever.listen(0)
    print(f"Listening on {server_ip}:{groundrecieveport}")

    # accept incoming connections
    client_socket1, client_address1 = groundsender.accept()
    print(f"Accepted connection from {client_address1[0]}:{client_address1[1]}")
    client_socket2, client_address2 = payloadserver.accept()
    print(f"Accepted connection from {client_address2[0]}:{client_address2[1]}")
    client_socket3, client_address3 = groundreciever.accept()
    print(f"Accepted connection from {client_address3[0]}:{client_address3[1]}")

    # Start threads for sending battery status and thermal data
    threading.Thread(target=send_battery_status, args=(client_socket3,), daemon=True).start()
    threading.Thread(target=send_thermal_data, args=(client_socket3,), daemon=True).start()

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
            client_socket3.send("closed".encode("utf-8"))
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
        client_socket3.send(response1)
        client_socket2.send(response2)

    # close connection socket with the client
    client_socket1.close()
    print("Connection to client1 closed")
    client_socket2.close()
    print("Connection to client2 closed")
    client_socket3.close()
    print("Connection to client3 closed")
    # close server1 socket
    groundsender.close()
    payloadserver.close()
    groundreciever.close()

run_server()
