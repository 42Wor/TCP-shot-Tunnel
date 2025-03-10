import socket

def start_tcp_server(host='127.0.0.1', port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Server listening on {host}:{port}")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    s.close()
                print(f"Received data: {data.decode()}")
                conn.sendall(data)

if __name__ == "__main__":
    start_tcp_server()