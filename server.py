import socket
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import paho.mqtt.client as mqtt
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

# === AES Configuration ===
KEY = b"ThisIsA16ByteKey"
IV = b"ThisIsA16ByteIV!"

# === MQTT Broker Setup ===
import subprocess
subprocess.run(["sudo", "systemctl", "start", "mosquitto"])

# Create MQTT client for publishing
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()

# === Start HTTP Server for Leaflet Dashboard ===
def start_http_server():
    PORT = 9004
    handler = SimpleHTTPRequestHandler
    with TCPServer(("", PORT), handler) as httpd:
        print(f"[?] Leaflet dashboard at http://192.168.16.254:{PORT}")
        httpd.serve_forever()

http_thread = threading.Thread(target=start_http_server, daemon=True)
http_thread.start()

# === Start Raw Socket Listener ===
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 5050))
print("[?] Listening on UDP 5050 for encrypted GPS data...")

while True:
    data, addr = sock.recvfrom(1024)
    try:
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted = unpad(cipher.decrypt(data), AES.block_size)
        gps_data = json.loads(decrypted.decode())
        print(f"[UDP] From {addr}: {gps_data}")
       
        # Forward the decrypted data to MQTT
        mqtt_client.publish("gps/phones", json.dumps(gps_data))
        print(f"[MQTT] Published GPS data to gps/phones")
    except Exception as e:
        print("Error processing data:", e)
