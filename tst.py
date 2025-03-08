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
    tcp_socket = None
    connected_and_logged_in = False

    @classmethod
    def initialize_tcp_connection(cls):
        if cls.tcp_socket is None:
            if PORT1 is None:
                colored_print(f"{COLOR_RED}Error: TCP Port not set.{COLOR_RESET}", COLOR_RED)
                return False
            try:
                colored_print(f"{COLOR_CYAN}Connecting to TCP server...{COLOR_RESET}") # Simplified
                cls.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                cls.tcp_socket.connect((HOST, PORT1))
                colored_print(f"{COLOR_GREEN}TCP Connected.{COLOR_RESET}", COLOR_GREEN) # Simplified

                login_data = {"username": "testuser", "password": "testpassword", "databaseName": "mydatabase"}
                cls.tcp_socket.sendall((json.dumps(login_data) + '\n').encode('utf-8'))

                login_response_data = cls.tcp_socket.recv(1024)
                if not login_response_data:
                    raise socket.error("No login response")
                login_response_json = json.loads(login_response_data.decode('utf-8'))
                if 'error' in login_response_json:
                    colored_print(f"{COLOR_RED}TCP Login Error: {login_response_json['error']}{COLOR_RESET}", COLOR_RED)
                    cls.close_tcp_connection()
                    return False
                else:
                    colored_print(f"{COLOR_GREEN}TCP Logged in.{COLOR_RESET}", COLOR_GREEN) # Simplified
                    cls.connected_and_logged_in = True
                    return True
            except socket.error as tcp_e:
                colored_print(f"{COLOR_RED}TCP Connection Error: {tcp_e}{COLOR_RESET}", COLOR_RED)
                cls.close_tcp_connection()
                return False
        return cls.connected_and_logged_in

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": "Simple HTTP service is running (try POST requests)"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        colored_print(f"{COLOR_BLUE}GET request served.{COLOR_RESET}", COLOR_BLUE) # Kept, but simpler message

    def do_POST(self):
        if not MyHandler.initialize_tcp_connection():
            self.send_error_response(500, {"error": "TCP connection failed."}) # Simplified error message
            return

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                post_data_json = json.loads(post_data.decode('utf-8'))
                # Removed: colored_print(f"{COLOR_CYAN}Received POST data...{COLOR_RESET}") - Less important detail
            except json.JSONDecodeError as e:
                self.send_error_response(400, {"error": "Invalid JSON data"}) # Simplified error message
                colored_print(f"{COLOR_RED}Error: Invalid JSON from client.{COLOR_RESET}", COLOR_RED) # More concise error
                return

            try:
                # Removed: colored_print(f"{COLOR_CYAN}Forwarding data to TCP server...{COLOR_RESET}") - Less important detail
                MyHandler.tcp_socket.sendall((json.dumps(post_data_json) + '\n').encode('utf-8'))

                data = MyHandler.tcp_socket.recv(1024)
                if not data:
                    response_data_json = {"warning": "No TCP response"} # Simplified warning
                    colored_print(f"{COLOR_YELLOW}Warning: No TCP response.{COLOR_RESET}", COLOR_YELLOW) # Kept warning
                else:
                    response_data = data.decode('utf-8')
                    try:
                        response_data_json = json.loads(response_data)
                        # Removed: colored_print(f"{COLOR_CYAN}Received TCP response: {response_data_json}{COLOR_RESET}") - Detail in response
                    except json.JSONDecodeError as e:
                        response_data_json = {"error": "Invalid JSON from TCP", "raw_response": response_data} # Simplified error
                        colored_print(f"{COLOR_RED}Error: Invalid JSON from TCP server.{COLOR_RESET}", COLOR_RED) # More concise error

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_data_json).encode('utf-8'))
                colored_print(f"{COLOR_GREEN}POST response sent.{COLOR_RESET}", COLOR_GREEN) # Simplified success message

            except socket.error as tcp_e:
                colored_print(f"{COLOR_RED}TCP Data Error: {tcp_e}{COLOR_RESET}", COLOR_RED) # More concise error
                self.send_error_response(500, {"error": "TCP communication error"}) # Simplified error
                MyHandler.close_tcp_connection()


        except Exception:
            colored_print(f"{COLOR_RED}HTTP POST Error.{COLOR_RESET}", COLOR_RED) # More concise error
            self.send_error_response(500, {"error": "HTTP Server Error"}) # Simplified error


    def send_error_response(self, status_code, error_message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(error_message).encode('utf-8'))
        colored_print(f"{COLOR_RED}HTTP Error Response: {error_message}{COLOR_RESET}", COLOR_RED) # Kept error message

    @classmethod
    def close_tcp_connection(cls):
        if cls.tcp_socket:
            cls.tcp_socket.close()
            colored_print(f"{COLOR_YELLOW}TCP connection closed.{COLOR_RESET}", COLOR_YELLOW) # Simplified
            cls.tcp_socket = None
            cls.connected_and_logged_in = False

    @classmethod
    def server_close(cls, server):
        colored_print(f"{COLOR_BLUE}HTTP Server closing.{COLOR_RESET}", COLOR_BLUE) # Simplified
        cls.close_tcp_connection()
        server.server_close()

def serve_forever_with_shutdown(server_address, handler_class):
    with socketserver.TCPServer(server_address, handler_class) as httpd:
        import signal
        def signal_handler(signum, frame):
            colored_print(f"{COLOR_BLUE}Shutting down server...{COLOR_RESET}", COLOR_BLUE) # Simplified
            handler_class.server_close(httpd)
            httpd.shutdown()
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        colored_print(f"{COLOR_CYAN}Starting HTTP service...{COLOR_RESET}") # Simplified
        if not handler_class.initialize_tcp_connection():
            colored_print(f"{COLOR_RED}Failed to start TCP connection.{COLOR_RESET}", COLOR_RED) # Simplified error
            return

        colored_print(f"{COLOR_GREEN}HTTP Server started.{COLOR_RESET}", COLOR_GREEN) # Simplified success
        httpd.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            PORT1 = int(sys.argv[1])
        except ValueError:
            colored_print(f"{COLOR_RED}Error: Invalid TCP port.{COLOR_RESET}", COLOR_RED) # Simplified error
            sys.exit(1)
    else:
        colored_print(f"{COLOR_RED}Usage: tst.py <TCP_PORT>{COLOR_RESET}", COLOR_RED) # Kept usage
        sys.exit(1)

    try:
        serve_forever_with_shutdown(("", PORT), MyHandler)
    except OSError as e:
        if e.errno == 98:
            colored_print(f"{COLOR_RED}Error: Port {PORT} already in use.{COLOR_RESET}", COLOR_RED) # Simplified error
        else:
            colored_print(f"{COLOR_RED}OSError starting server.{COLOR_RESET}", COLOR_RED) # Simplified error
    except Exception as e:
        colored_print(f"{COLOR_RED}Server start error.{COLOR_RESET}", COLOR_RED) # Simplified error