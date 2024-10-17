import socket
import time
import random
import threading



# Battery simulation settings
battery_percent = random.randint(40, 80)  # Initial battery percentage
is_charging = False  # Initial charging state
charge_interval = random.randint(10, 30)  # Duration for charging
update_interval = 5  # Time between status updates in seconds

def update_battery_status():
    """Update battery status based on charging state."""
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

def send_battery_status(client_socket):
    """Send battery status at precise intervals."""
    while True:
        update_battery_status()
        battery_info = f"TM.03.01 Battery Status:\n\t  Percent: {battery_percent:.1f}%\n\t  Charging: {is_charging}\n"
        client_socket.send(battery_info.encode("utf-8"))
        time.sleep(update_interval)  # Slower updates

def run_server():
    server_ip = "127.0.0.1"
    ground_send_port = 8000
    payload_port = 9000
    ground_receive_port = 10000

    ground_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    payload_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ground_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ground_sender.bind((server_ip, ground_send_port))
    payload_server.bind((server_ip, payload_port))
    ground_receiver.bind((server_ip, ground_receive_port))

    ground_sender.listen(1)
    payload_server.listen(1)
    ground_receiver.listen(1)

    print(f"Listening on {server_ip}:{ground_send_port}")
    print(f"Listening on {server_ip}:{payload_port}")
    print(f"Listening on {server_ip}:{ground_receive_port}")

    client_socket1, _ = ground_sender.accept()
    client_socket2, _ = payload_server.accept()
    client_socket3, _ = ground_receiver.accept()

    # Start the thread to send battery status
    threading.Thread(target=send_battery_status, args=(client_socket3,), daemon=True).start()

    while True:
        request1 = client_socket1.recv(1024).decode("utf-8")
        if request1.lower() == "close":
            client_socket1.send("closed".encode("utf-8"))
            client_socket2.send("closed".encode("utf-8"))
            client_socket3.send("closed".encode("utf-8"))
            break

        print(f"Received: {request1} at {time.strftime('%H:%M:%S')}")

        response1 = f"Echo: {request1}".encode("utf-8")
        client_socket1.send(response1)
        client_socket3.send(response1)

    # Close connection sockets with the clients
    client_socket1.close()
    client_socket2.close()
    client_socket3.close()
    ground_sender.close()
    payload_server.close()
    ground_receiver.close()


run_server()
