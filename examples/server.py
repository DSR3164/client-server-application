import socket

with socket.socket() as s:
    s.bind(('0.0.0.0', 12345))
    s.listen()
        
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data or data.decode().lower() == 'quit':
                break                
            print(f"Received: {data.decode()}")
            conn.sendall(data)
