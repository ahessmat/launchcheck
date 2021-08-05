import socket

HOST = '127.0.0.1'
PORT = 10001

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
	s.connect((HOST, PORT))
	s.sendall('test1 test2 test3\r\n\r\n'.encode())
	data = s.recv(1024)
print('Received', repr(data))
