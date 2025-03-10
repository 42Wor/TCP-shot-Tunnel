#!/usr/bin/env python3

import http.server
import socketserver
import socket
import json
import sys

# ANSI escape codes for colors
COLOR_RESET = '\033[0m'
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_YELLOW = '\033[93m'
COLOR_BLUE = '\033[94m'
COLOR_CYAN = '\033[96m'

HOST = '127.0.0.1'
PORT = 8000
PORT1 = None

def colored_print(text, color_code=COLOR_RESET):
    print(f"{color_code}{text}{COLOR_RESET}")

class MyHandler(http.server.BaseHTTPRequestHandler):
    tcp_socket = None # Class-level socket, initialized to None
    connected_and_logged_in = False # Flag to track login status

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": "Simple HTTP service is running (try POST requests)"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        colored_print("GET request served.", COLOR_GREEN)

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                post_data_json = json.loads(post_data.decode('utf-8'))
                colored_print(f"Received POST data from HTTP client: {post_data_json}", COLOR_BLUE)
            except json.JSONDecodeError as e:
                self.send_error_response(400, {"error": f"Invalid JSON data from HTTP client: {e}"})
                colored_print(f"Invalid JSON data from HTTP client: {e}", COLOR_RED)
                return

            try:
                colored_print(f"Forwarding data to TCP server (persistent connection): {post_data_json}", COLOR_YELLOW)
                MyHandler.tcp_socket.sendall((json.dumps(post_data_json) + '\n').encode('utf-8'))

                data = self.recv_all(MyHandler.tcp_socket)
                if not data:
                    colored_print("No data received from TCP server.", COLOR_RED)
                    response_data_json = {"warning": "No response from TCP server"}
                else:
                    response_data = data.decode('utf-8')
                    try:
                        response_data_json = json.loads(response_data)
                        colored_print(f"Received response from TCP server: {response_data_json}", COLOR_GREEN)
                    except json.JSONDecodeError as e:
                        response_data_json = {"error": f"Invalid JSON response from TCP server: {e}", "raw_response": response_data}
                        colored_print(f"Invalid JSON response from TCP server: {e}, raw response: {response_data}", COLOR_RED)

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_data_json).encode('utf-8'))
                colored_print("HTTP response sent to client.", COLOR_GREEN)

            except socket.error as tcp_e:
                colored_print(f"TCP Error during data exchange: {tcp_e}", COLOR_RED)
                self.send_error_response(500, {"error": f"Error communicating with TCP server: {tcp_e}"})
                MyHandler.close_tcp_connection() # Close and reset on communication error

        except Exception as http_e:
            colored_print(f"HTTP Server Error in do_POST: {http_e}", COLOR_RED)
            self.send_error_response(500, {"error": f"HTTP Server Error: {http_e}"})

    def send_error_response(self, status_code, error_message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(error_message).encode('utf-8'))
        colored_print(f"HTTP Error Response sent: {error_message}", COLOR_RED)

    @classmethod
    def close_tcp_connection(cls):
        if cls.tcp_socket:
            cls.tcp_socket.close()
            colored_print("Persistent TCP connection closed.", COLOR_YELLOW)
            cls.tcp_socket = None
            cls.connected_and_logged_in = False # Reset login flag

    @classmethod
    def server_close(cls, server): # Hook to close TCP on server shutdown
        colored_print("HTTP Server is closing...", COLOR_YELLOW)
        cls.close_tcp_connection()
        server.server_close()

    def recv_all(self, sock, buffer_size=1024):
        data = b''
        while True:
            part = sock.recv(buffer_size)
            data += part
            if len(part) < buffer_size:
                break
        return data

def serve_forever_with_shutdown(server_address, handler_class):
    with socketserver.TCPServer(server_address, handler_class) as httpd:
        import signal
        def signal_handler(signum, frame):
            colored_print("Shutting down HTTP server...", COLOR_YELLOW)
            handler_class.server_close(httpd) # Use the class method for shutdown
            httpd.shutdown()
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        colored_print(f"Serving dynamic HTTP content, forwarding to TCP server at port {PORT1}, on HTTP port {PORT}", COLOR_CYAN)
        # Initialize TCP connection and login *before* starting to serve
        try:
            MyHandler.tcp_socket = socket.create_connection((HOST, PORT1))
            colored_print(f"Connected to TCP server at {HOST}:{PORT1}", COLOR_GREEN)
        except socket.error as e:
            colored_print(f"Failed to connect to TCP server at {HOST}:{PORT1}: {e}", COLOR_RED)
            return

        httpd.serve_forever()

        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            PORT1 = int(sys.argv[1])
        except ValueError:
            colored_print(f"Error: Invalid TCP port.", COLOR_RED) # Simplified error
            sys.exit(1)
    else:
        colored_print(f"Usage: tst.py <TCP_PORT>", COLOR_RED) # Kept usage
        sys.exit(1)

    try:
        serve_forever_with_shutdown(("", PORT), MyHandler)
    except OSError as e:
        if e.errno == 98:
            colored_print(f"Error: Port {PORT} already in use.", COLOR_RED) # Simplified error
        else:
            colored_print(f"OSError starting server.", COLOR_RED) # Simplified error
    except Exception as e:
        colored_print(f"Server start error.", COLOR_RED) # Simplified error