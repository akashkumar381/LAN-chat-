import socket
import threading
import os

# Function to handle each client
def handle_client(client_socket, client_address, client_number):
    print(f"New connection from {client_address} (Client {client_number})")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                if message.startswith("/file"):
                    file_name = message.split()[1]
                    receive_file(client_socket, file_name, client_number)
                elif message.startswith("GET"):
                    print(f"Received HTTP-like request from Client {client_number}: {message}")
                else:
                    print(f"Received from Client {client_number} ({client_address}): {message}")
                    broadcast(f"Client {client_number}: {message}", client_socket)
            else:
                break
        except Exception as e:
            print(f"Error handling client {client_number}: {e}")
            break
    client_socket.close()
    del clients[client_number]  # Remove the client when it disconnects

# Function to receive a file from a client
def receive_file(client_socket, file_name, client_number):
    print(f"Receiving file '{file_name}' from Client {client_number}")
    broadcast(f"Client {client_number} is sending file: {file_name}", client_socket)
    
    with open(file_name, 'wb') as f:
        while True:
            file_data = client_socket.recv(1024)
            if not file_data:
                break
            f.write(file_data)
            print(f"Received chunk of size {len(file_data)} from Client {client_number}")
    
    print(f"File '{file_name}' received from Client {client_number}")
    broadcast(f"File '{file_name}' received from Client {client_number}. Sending to all clients...", client_socket)
    send_file_to_all(file_name, client_socket)

# Function to send a file to a specific client
def send_file_to_client(client_number, file_path):
    if client_number in clients:
        client_socket = clients[client_number]
        file_name = os.path.basename(file_path)
        client_socket.send(f"/file {file_name}".encode('utf-8'))
        print(f"Sending file '{file_name}' to Client {client_number}")
        
        with open(file_path, 'rb') as f:
            file_data = f.read(1024)
            while file_data:
                client_socket.send(file_data)
                print(f"Sent chunk of size {len(file_data)} to Client {client_number}")
                file_data = f.read(1024)
        print(f"File '{file_name}' sent to Client {client_number}")
    else:
        print(f"Client {client_number} not found.")

# Function to send a file to all clients
def send_file_to_all(file_name, current_socket=None):
    for client_number, client_socket in clients.items():
        if client_socket != current_socket:
            try:
                client_socket.send(f"/file {file_name}".encode('utf-8'))
                print(f"Sending file '{file_name}' to Client {client_number}")
                
                with open(file_name, 'rb') as f:
                    file_data = f.read(1024)
                    while file_data:
                        client_socket.send(file_data)
                        print(f"Sent chunk of size {len(file_data)} to Client {client_number}")
                        file_data = f.read(1024)
                print(f"File '{file_name}' sent to Client {client_number}")
            except Exception as e:
                print(f"Error sending file to Client {client_number}: {e}")
                client_socket.close()
                del clients[client_number]

# Function to send a message to a specific client
def send_message_to_client(client_number, message):
    if client_number in clients:
        try:
            clients[client_number].send(message.encode('utf-8'))
            print(f"Message sent to Client {client_number}")
        except Exception as e:
            print(f"Error sending message to Client {client_number}: {e}")
            clients[client_number].close()
            del clients[client_number]
    else:
        print(f"Client {client_number} not found.")

# Function to handle server input (for sending messages and files)
def server_send():
    while True:
        command = input("Server command (use 'Client <number> <message>' to send a message or 'Client <number> /file <file_path>' to send a file): ")
        
        if command.startswith("Client"):
            parts = command.split(' ', 3)
            
            if len(parts) >= 3:
                client_number = int(parts[1])
                if parts[2] == "/file" and len(parts) == 4:
                    file_path = parts[3]
                    send_file_to_client(client_number, file_path)
                else:
                    message = ' '.join(parts[2:])
                    send_message_to_client(client_number, message)
            else:
                print("Invalid format. Use 'Client <number> <message>' or 'Client <number> /file <file_path>'")
        else:
            broadcast(f"Server: {command}")

# Function to broadcast messages to all clients except the sender
def broadcast(message, current_socket=None):
    for client_socket in clients.values():
        if client_socket != current_socket:
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                client_socket.close()

# Main server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555))  # Bind to all interfaces on port 5555
server.listen(5)
print("Server listening on port 5555...")

clients = {}
client_count = 0

# Thread to handle server sending messages and files
server_thread = threading.Thread(target=server_send)
server_thread.start()

# Main loop to accept new clients
while True:
    client_socket, client_address = server.accept()
    client_count += 1
    clients[client_count] = client_socket
    print(f"Client {client_count} connected from {client_address}")
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, client_count))
    client_thread.start()
