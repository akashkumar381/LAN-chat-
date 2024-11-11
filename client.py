import socket
import os
import threading

# Function to receive messages and files from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message.startswith("/file"):
                file_name = message.split()[1]
                print(f"Server is sending file: {file_name}")
                receive_file(client_socket, file_name)
            else:
                print(f"Message received: {message}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Function to receive a file from the server
def receive_file(client_socket, file_name):
    print(f"Receiving file: {file_name}")
    
    # Open the file in write-binary mode
    with open(file_name, 'wb') as f:
        while True:
            # Receive file data in chunks
            file_data = client_socket.recv(1024)
            if not file_data:
                # When no more data is received, exit loop
                print(f"File '{file_name}' received and saved.")
                break
            f.write(file_data)
            print(f"Received chunk of size {len(file_data)}")

# Function to send a file to the server
def send_file(client_socket, file_path):
    file_name = os.path.basename(file_path)
    client_socket.send(f"/file {file_name}".encode('utf-8'))
    print(f"Sending file: {file_name}")
    
    with open(file_path, 'rb') as f:
        file_data = f.read(1024)
        while file_data:
            client_socket.send(file_data)
            print(f"Sent chunk of size {len(file_data)}")
            file_data = f.read(1024)
    
    # Indicating that file transmission is complete
    client_socket.send(b'')
    print(f"File '{file_name}' sent to the server.")

# Function to send a message or file to the server
def send_message_or_file(client_socket):
    while True:
        user_input = input("Enter message or file path to send (e.g., '/file /path/to/file.txt'): ")
        
        if user_input.startswith('/file'):
            send_file(client_socket, user_input.split(' ', 1)[1])
        else:
            client_socket.send(user_input.encode('utf-8'))

# Main client setup
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = input("Enter server IP address: ")
    
    try:
        client.connect((server_address, 5555))
        print("Connected to server successfully!")

        # Start receiving messages in a separate thread
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.start()

        # Start sending messages or files
        send_message_or_file(client)
    
    except OSError as e:
        print(f"Connection failed: {e}")
    
    finally:
        client.close()

if __name__ == "__main__":
    main()
