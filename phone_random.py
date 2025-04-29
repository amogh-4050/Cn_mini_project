import socket
import json
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import paho.mqtt.client as mqtt_client
import random

# AES Configuration
KEY = b'ThisIsA16ByteKey'     # Must match listener
IV = b'ThisIsA16ByteIV!'      # Must match listener

# MQTT Setup
client_id = "Phone2"  
mqtt_client = mqtt_client.Client(client_id=client_id)
mqtt_client.connect("192.168.193.254", 1883, 60)  # Match your Raspberry Pi's IP
mqtt_client.loop_start()

# Simulate GPS Data
def get_mock_gps():
    return {
        "device": client_id,
        "latitude": round(random.uniform(12.91, 12.96), 6),  # Slightly different range
        "longitude": round(random.uniform(77.61, 77.66), 6), # Slightly different range
        "timestamp": time.time()
    }

# Encrypt and send GPS data
def send_data():
    while True:
        gps_data = get_mock_gps()
        print(f"[GPS] Sending: {gps_data}")
        raw_data = json.dumps(gps_data).encode()
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        encrypted = cipher.encrypt(pad(raw_data, AES.block_size))
        
        # Send encrypted GPS over raw socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("192.168.193.254", 5050))  # Match your Raspberry Pi's IP
            sock.sendall(encrypted)
            sock.close()
        except Exception as e:
            print(f"[SOCKET ERROR] {e}")
        
        # Also publish via MQTT (optional)
        try:
            mqtt_client.publish("gps/phones", json.dumps(gps_data))
            print("[MQTT] Published directly to gps/phones")
        except Exception as e:
            print(f"[MQTT ERROR] {e}")
            
        time.sleep(5)

if __name__ == "__main__":
    send_data()
