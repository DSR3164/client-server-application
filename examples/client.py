import socket

with socket.socket() as s:
    s.connect(('192.168.0.16', 12345))
    while True:
        message = input("Enter message: ")
        if message.lower() == 'exit':
            break
        s.sendall(message.encode())
        data = s.recv(1024)
        print(f"Received from server: {data.decode()}")
