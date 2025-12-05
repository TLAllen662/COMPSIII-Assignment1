import socket
import sys

host = '127.0.0.1'
port = 5000

s = socket.socket()
s.settimeout(2)
try:
    s.connect((host, port))
    print('connect ok')
except Exception as e:
    print('connect failed:', type(e).__name__, e)
    sys.exit(1)
finally:
    s.close()
