from struct import pack
from chat_server_logic import *
import sys

#INIT METHOD
class User:
    def __init__(self, name):
        self.name = name
        self.ROOM_DETAILS_LIST = []
        self.thisRoom = ''


class Room:
    def __init__(self, name):
        self.peoples = []
        self.NICK_NAMES_LIST = []
        self.name = name


"""
    Lists the available room details and members to a specified user.

    :param nickname: The nickname of the user.
"""
def list_room_details(nickname):
    user_socket = registered_users[nickname]
    print(len(room_details))
    
    # Checking if there are any rooms available or not
    if len(room_details) == 0:
        user_socket.send('No rooms are available to join'.encode('utf-8'))
    else:
        reply = "List of available rooms: \n"

        # Iterating through each room in room_details
        for room_name, room_info in room_details.items():
            reply += f"\nRoom: {room_info.name}\nMembers:\n"

            # Iterating through the nicknames in the room
            for member_nickname in room_info.NICK_NAMES_LIST:
                reply += f"- {member_nickname}\n"
        
        # Sending the list of available rooms and members to the user.
        user_socket.send(f'{reply}'.encode('utf-8'))



"""
    Allows a user to join a specified room.

    :param nickname: The nickname of the user.
    :param room_name: The name of the room to join.
"""
def join_room(nickname, room_name):
    user_socket = registered_users[nickname]
    current_user = active_users[nickname]

    #Checking whether the room exists or not
    if room_name not in room_details:

        # Since the room is not available, creating a new one.
        room = Room(room_name)
        room_details[room_name] = room
        room.peoples.append(user_socket)
        room.NICK_NAMES_LIST.append(nickname)

        # Updating user's current room and room history
        current_user.thisRoom = room_name
        current_user.ROOM_DETAILS_LIST.append(room)
        user_socket.send(f'{room_name} created'.encode('utf-8'))
    else:
        # If the room already exists
        room = room_details[room_name]

        # Checking if the user is already in the room or not
        if room_name in current_user.ROOM_DETAILS_LIST:
            user_socket.send('You are already in the room'.encode('utf-8'))
        else:
            # Adding the user to the room and update the user information.
            room.peoples.append(user_socket)
            room.NICK_NAMES_LIST.append(nickname)
            current_user.thisRoom = room_name
            current_user.ROOM_DETAILS_LIST.append(room)

            # Broadcasting a message to all users in the room about the new user
            message_broadcast(f'{nickname} joined the room', room_name)
            #user_socket.send('Joined room'.encode('utf-8'))


"""
    Allowing a user to switch to a different room.

    :param nickname: The nickname of the user.
    :param new_room_name: The name of the room to switch to.
"""
def switch_room(nickname, new_room_name):
    user = active_users[nickname]
    user_socket = registered_users[nickname]

    # Getting the current room of the user
    current_room = room_details[new_room_name]

    # Checking if the user is already in the specified room
    if new_room_name == user.thisRoom:
        user_socket.send('You are already in the room'.encode('utf-8'))
    
    # Checking if the user is not part of the specified room
    elif current_room not in user.ROOM_DETAILS_LIST:
        user_socket.send('Switch not available. You are not part of the current room'.encode('utf-8'))
    else:
        # Switching to the new room
        user.thisRoom = new_room_name
        user_socket.send(f'Switched to {new_room_name}'.encode('utf-8'))


"""
    Allows a user to exit the current room.

    :param nickname: The nickname of the user.
"""
def exit_room(nickname):
    user = active_users[nickname]
    user_socket = registered_users[nickname]

    # Checking if the user is not part of any room
    if user.thisRoom == '':
        user_socket.send('You are not part of any room'.encode('utf-8'))
    else:
        # Getting the details of the current room
        current_room_name = user.thisRoom
        current_room = room_details[current_room_name]

        # Update user information to indicate they are not in any room
        user.thisRoom = ''
        user.ROOM_DETAILS_LIST.remove(current_room)

        # Removing the user from the current room
        room_details[current_room_name].peoples.remove(user_socket)
        room_details[current_room_name].NICK_NAMES_LIST.remove(nickname)

        # Broadcasting a message to all users in the room about the user leaving
        message_broadcast(f'{nickname} left the room', current_room_name)

        # Notifying the user that they left the room
        user_socket.send('You left the room'.encode('utf-8'))

"""
    Sends a personal message from one user to another.

    Parameters:
    - message_string (str): The input message string containing sender, recipient, and message content.
    - registered_users_dict (dict): A dictionary containing registered users' usernames as keys
                                    and their corresponding sockets as values.

"""
def send_personal_message(message_string):
     # Spliting the incoming message into individual words
    message_args = message_string.split(" ")

    # Extracting relevant information from the message
    sender_username = registered_users[message_args[0]]
    recipient_username = message_args[2]

    # Checking if the sender is a registered user
    if recipient_username not in registered_users:
        # If not, send a message to the sender indicating that the user is not found
        sender_username.send('User not found'.encode('utf-8'))
    else:
        # Retrieving the recipient's socket from the registered users dictionary
        recipient_socket = registered_users[recipient_username]

        # Extracting the message content from the remaining arguments
        message_content = ' '.join(message_args[3:])

        # Formating and sending the personal message to both the sender and the recipient
        recipient_socket.send(f'[personal message] {message_args[0]}: {message_content}'.encode('utf-8'))
        sender_username.send(f'[personal message] {message_args[0]}: {message_content}'.encode('utf-8'))


def leave_server(self, client_name):
    if client_name in self.room_details:
        for room_name in self.room_details[client_name]:
            self.room_details[room_name].remove(client_name)
        del self.room_details[client_name]
    client_socket = self.connected_clients[client_name]["address"]
    client_socket.close()
    print("Disconnected the client %s" % client_name)
    sys.exit(1)


"""
    Removes a client with the specified nickname from the chat system.

    Parameters:
    - nickname (str): The nickname of the client to be removed.

"""
def remove_client_from_chat(nickname):
    # Removing the client's nickname from the list of user nicknames
    user_nicknames.remove(nickname)

    # Retrieving the client's socket from the registered users dictionary
    client_socket = registered_users[nickname]

    # Retrieving the active user instance associated with the nickname
    active_user = active_users[nickname]

    # Clearing the current room assignment for the user
    active_user.thisRoom = ''
    
    #  Iterating through the rooms the user is a part of
    for room in active_user.ROOM_DETAILS_LIST:
        print(room.name)

        # Removing the client from the list of people in the room
        room.peoples.remove(client_socket)
        print(f'Updated People List: {room.peoples}')

        # Removing the user's nickname from the list of nicknames in the room
        if room.NICK_NAMES_LIST:
            room.NICK_NAMES_LIST.remove(nickname)
            print(f'Updated Nickname List: {room.NICK_NAMES_LIST}')

        # Broadcast a message to the room indicating that the user left
        message_broadcast(f'{nickname} left the room', room.name)
        print('End of message broadcast')
    return


"""
    Handles the interaction with a connected client.

    Parameters:
    - client_socket (socket): The socket representing the connected client.
"""
def handle_client_interaction(client_socket):
    client_nickname=''
    while True:
        try:
            # Receive and decode the incoming message from the client
            received_message = client_socket.recv(1024).decode('utf-8')

            # Split the message into individual arguments
            message_args = received_message.split(" ")

            # Extract the sender's registered name from the registered users dictionary
            sender_name_socket = registered_users[message_args[0]]
            client_nickname = message_args[0]

            # Handle different commands based on the received message
            if '#help' in received_message:
                sender_name_socket.send(instructions.encode('utf-8'))
            elif '#list' in received_message:
                list_room_details(message_args[0])
            elif '#join' in received_message:
                join_room(message_args[0], ' '.join(message_args[2:]))
            elif '#leave' in received_message:
                exit_room(message_args[0])
            elif '#switch' in received_message:
                switch_room(message_args[0], message_args[2])
            elif '#personal' in received_message:
                send_personal_message(received_message)
            elif '#quit' in received_message:
                # Remove the client from the chat, send a QUIT message, and close the connection
                remove_client_from_chat(message_args[0])
                sender_name_socket.send('QUIT'.encode('utf-8'))
                sender_name_socket.close()
            else:
                # Process general messages
                if active_users[message_args[0]].thisRoom == '':
                    sender_name_socket.send('You are not part of any room'.encode('utf-8'))
                else:
                    msg = ' '.join(message_args[1:])
                    message_broadcast(f'{message_args[0]}: {msg}',active_users[message_args[0]].thisRoom)

        except Exception as e:
            # Handle exceptions and clean up resources if necessary
            print("exception occured ", e)
            index = connected_clients.index(client_socket)
            connected_clients.remove(client_socket)
            client_socket.close()
            print(f'nick name is {client_nickname}')

            # Remove the client from the chat if it hasn't been removed already
            #if client_nickname in user_nicknames:
                #remove_client_from_chat(client_nickname)

            # Remove the nickname from the list of user nicknames
            if client_nickname in user_nicknames:
                user_nicknames.remove(client_nickname)
            break

# Function to handle the connection with a client
def handle_client_connection():
    # Infinite loop to continuously accept incoming connections
    while True:
        # Accept a connection from a client, obtaining the client socket and address
        client_socket, client_address = server_socket.accept()

        # Print information about the connection
        print(f'connected with {str(client_address)}')
        print(client_socket)

        # Send the 'NICK' message to the client
        client_socket.send('NICK'.encode('utf-8'))

        # Receive the nickname from the client
        nickname = client_socket.recv(1024).decode('utf-8')

        # Store the received nickname and client socket in appropriate lists
        user_nicknames.append(nickname)
        connected_clients.append(client_socket)

        # Create a User object with the received nickname
        user = User(nickname)

        # Add the user to the active users dictionary
        active_users[nickname] = user

        # Add the user's nickname and client socket to the registered users dictionary
        registered_users[nickname] = client_socket

        # Print the nickname of the connected client
        print(f'Nickname of the client is {nickname}')
        
        # Send a welcome message to the client
        client_socket.send('Connected to the server!'.encode('utf-8'))

        # Send instructions to the client
        client_socket.send(instructions.encode('utf-8'))

        # Start a new thread to handle interactions with the connected client
        thread = threading.Thread(target=handle_client_interaction, args=(client_socket,))
        thread.start()

print('Server is listening...........')
handle_client_connection()