import socket
import json
import threading

class TCPServer:
    def __init__(self, host='192.168.100.11', port=8080):
        self.host = host
        self.port = port
        self.stride = 6
        self.leds_qty = 3
        self.server_socket = self.create_server_socket()
        self.sensors = []  # Lista para almacenar clientes sensores
        self.actuators = []  # Lista para almacenar clientes actuadores

    def create_server_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return server_socket

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            try:
                client_socket, client_address = self.accept_client()
                self.handle_client_in_thread(client_socket, client_address)
            except Exception as e:
                print(f"Error while accepting client: {e}")

    def accept_client(self):
        client_socket, client_address = self.server_socket.accept()
        print(f"Accepted connection from {client_address}")
        return client_socket, client_address

    def handle_client_in_thread(self, client_socket, client_address):
        client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
        client_thread.start()

    def handle_client(self, client_socket, client_address):
        print(f"Client {client_address} connected.")
        try:
            while True:
                request = self.receive_request(client_socket)
                if not request:
                    print(f"Client {client_address} disconnected.")
                    break

                print(f"Received from {client_address}: {request}")
                response = self.process_request(client_socket, request)
                if response:
                    self.send_response(client_socket, response)

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"Connection error with client {client_address}: {e}")
        finally:
            self.close_connection(client_socket, client_address)

    def receive_request(self, client_socket):
        return client_socket.recv(1024).decode('utf-8')

    def process_request(self, client_socket, request):
        if request.startswith("GET RANGES"):
            return self.handle_get_ranges()
        elif request.startswith("REGISTER SENSOR"):
            self.sensors.append(client_socket)
        elif request.startswith("REGISTER ACTUATOR"):
            self.actuators.append(client_socket)
            return f"PUT 0\n"
        elif request.startswith("PUT"):
            return self.handle_put(client_socket, request)
        else:
            return "Unknown Command\n"

    def send_response(self, client_socket, response):
        client_socket.send(response.encode('utf-8'))

    def handle_get_ranges(self):
        return json.dumps({'stride': self.stride, 'LED_qty': self.leds_qty}) + "\n"

    def handle_put(self, client_socket, request):
        try:
            state = int(request.split()[-1])
            response = f"State updated to: {state}\n"

            if self.actuators:
                for actuator in self.actuators:
                    try:
                        self.send_response(actuator, f"{request}\n")
                    except (BrokenPipeError, ConnectionResetError):
                        print("Actuator disconnected, removing from list.")
                        self.actuators.remove(actuator)
            else:
                response += "No actuators registered\n"

            return response
        except ValueError:
            return "Invalid state\n"

    def close_connection(self, client_socket, client_address):
        client_socket.close()
        print(f"Client {client_address} connection closed.")

        if client_socket in self.sensors:
            self.sensors.remove(client_socket)
        if client_socket in self.actuators:
            self.actuators.remove(client_socket)

if __name__ == "__main__":
    server = TCPServer()
    server.start()
