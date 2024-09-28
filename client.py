import socket
import time

def run_client():
    server_host = '192.168.100.11'  # Cambia esto si tu servidor está en otra dirección
    server_port = 8080          # Asegúrate de que coincida con el puerto del servidor

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))
    
    try:
        # Enviar el comando REGISTER
        client_socket.send("REGISTER\n".encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Server response: {response}")

        # Enviar el comando GET RANGES
        client_socket.send("GET RANGES\n".encode('utf-8'))
        response = client_socket.recv(1024).decode('utf-8')
        print(f"Server response: {response}")

        # Enviar el comando PUT
        for state in range(4):
            client_socket.send(f"PUT {state}\n".encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Server response: {response}")
            time.sleep(1)  # Espera 1 segundo entre comandos para evitar sobrecargar al servidor

    finally:
        client_socket.close()
        print("Client connection closed.")

if __name__ == "__main__":
    run_client()
