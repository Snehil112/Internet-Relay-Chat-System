import threading
import socket
import sys

# Get user input for their name
user_input = input('Enter your name: ')

# List to store threads (if applicable) - renamed for clarity
thread_list = []

# Establish a connection to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 9000))

"""
    Continuously receives and processes messages from the server.

    This function handles messages such as NICK (to send the user's name)
    and QUIT (to exit the program).

"""
def receive_messages():
    while True:
        try:
            # Receive a message from the server and decode it
            received_message = client_socket.recv(1024).decode('utf-8')

            # Check the type of the received message
            if received_message == 'NICK':
                # Send the user's name to the server
                client_socket.send(user_input.encode('utf-8'))
            elif received_message == 'QUIT':
                # Exit the program if the server signals to quit
                print(f'Quit message was received from server!!')
                client_socket.close()
                sys.exit(2)
            else:
                # Print the received message
                print(received_message)
        
        except Exception as e:
            # Handle exceptions, close the client socket, and exit the program
            print('Server not responding')
            client_socket.close()
            sys.exit(2)


"""
    Continuously prompts the user for input, formats it with their name, and sends it to the server.

"""
def send_user_input():
    while True:
        # Prompt the user for input and format it with their name
        formatted_message = '{} {}'.format(user_input, input(''))
        
        try:
             # Send the formatted message to the server
            client_socket.send(formatted_message.encode('utf-8'))
        except Exception as e:
            # Handle exceptions, exit the program if an error occurs
            print('Error sending message:', e)
            sys.exit(0)

# Create and start a thread for receiving messages
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Add the receive thread to the list of active threads
thread_list.append(receive_thread)

# Create and start a thread for sending user input
send_thread = threading.Thread(target=send_user_input)
send_thread.start()

# Add the send thread to the list of active threads
thread_list.append(send_thread)