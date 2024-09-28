import socket
import json
import threading

class TCPServer:
    def __init__(self, host='0.0.0.0', port=1000):
        """
        Inicializa el servidor con el host y puerto especificados, 
        y define los valores por defecto para stride y leds_qty.
        """
        self.host = host
        self.port = port
        self.stride = 6
        self.leds_qty = 3
        self.server_socket = self.create_server_socket()

    def create_server_socket(self):
        """
        Crea y configura el socket del servidor para aceptar múltiples conexiones.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return server_socket

    def start(self):
        """
        Inicia el servidor y escucha conexiones entrantes.
        """
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
        """
        Acepta una nueva conexión de un cliente.
        """
        client_socket, client_address = self.server_socket.accept()
        print(f"Accepted connection from {client_address}")
        return client_socket, client_address

    def handle_client_in_thread(self, client_socket, client_address):
        """
        Crea un nuevo hilo para manejar las solicitudes del cliente.
        """
        client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
        client_thread.start()

    def handle_client(self, client_socket, client_address):
        """
        Maneja las solicitudes de un cliente específico.
        """
        print(f"Client {client_address} connected.")
        try:
            while True:
                request = self.receive_request(client_socket)
                if not request:
                    print(f"Client {client_address} disconnected.")
                    break

                print(f"Received from {client_address}: {request}")
                response = self.process_request(request)
                self.send_response(client_socket, response)

        except Exception as e:
            print(f"Error with client {client_address}: {e}")
        finally:
            self.close_connection(client_socket, client_address)

    def receive_request(self, client_socket):
        """
        Recibe una solicitud del cliente.
        """
        return client_socket.recv(1024).decode('utf-8')

    def send_response(self, client_socket, response):
        """
        Envía la respuesta al cliente.
        """
        client_socket.send(response.encode('utf-8'))

    def process_request(self, request):
        """
        Procesa el comando del cliente y retorna la respuesta adecuada.
        """
        if request.startswith("GET RANGES"):
            return self.handle_get_ranges()
        elif request.startswith("REGISTER"):
            return self.handle_register()
        elif request.startswith("PUT"):
            return self.handle_put(request)
        else:
            return "Unknown Command\n"

    def handle_get_ranges(self):
        """
        Procesa el comando GET RANGES.
        """
        return json.dumps({"stride": self.stride, "LEDs_qty": self.leds_qty}) + "\n"

    def handle_register(self):
        """
        Procesa el comando REGISTER.
        """
        return "ACK REGISTER\n"

    def handle_put(self, request):
        """
        Procesa el comando PUT con el estado recibido.
        """
        try:
            state = int(request.split()[-1])
            return f"State updated to: {state}\n"
        except ValueError:
            return "Invalid state\n"

    def close_connection(self, client_socket, client_address):
        """
        Cierra la conexión con el cliente.
        """
        client_socket.close()
        print(f"Client {client_address} connection closed.")

if __name__ == "__main__":
    server = TCPServer()
    server.start()
