import json
import socket
import time

HOST, PORT = "logstash", 10155

m = {"id": 2, "name": "abc"}

data = json.dumps(m)
received = ""
i = 0
# Create a socket (SOCK_STREAM means a TCP socket)
while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to server and send data
        print("Looking for at least a connection...")
        sock.connect((HOST, PORT))
        sock.sendall(bytes(data, encoding="utf-8"))
        print("[client] SENT")

        # Receive data from the server and shut down
        print("Sent:     {}".format(data))
        sock.close()
    except Exception:
        i += 1
        print(f"Tentativo di connessione fallito numero {i}")
    time.sleep(5)
