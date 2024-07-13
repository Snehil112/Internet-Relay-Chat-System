import socket
import threading

#Creating a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Specifying the host and port to bind the socket
server_host = '127.0.0.1'
server_port = 9000

#Binding the the socket to above specified host and port.
server_socket.bind((server_host, server_port))

#Setting the socket to listen mode for incoming instructions.
server_socket.listen()


instructions = '\nList of commands:\n' \
               '1.#list:                       To list all the rooms\n' \
               '2.#join <roomname>:            To join or create the room\n' \
               '3.#switch <roomname>:          To switch room\n' \
               '4.#help:                       To list all the commands\n' \
               '5.#personal <name> <message>:  To send personal message\n' \
               '6.#leave:                      To leave the room \n' \
               '7.#quit:                       To quit'


# Creating empty lists and dictionaries
connected_clients = []
user_nicknames = []
room_details = {}
registered_users = {}
active_users = {}

"""
    Broadcasts a message to all clients in a specified room.

    :param message: The message to be broadcasted.
    :param room_name: The name of the room where the message should be broadcasted.
"""
def message_broadcast(message, room_name):
    ## Iterating through all clients in the specified room
    for client_socket in room_details[room_name].peoples:
        #Preparing the broadcast message with room details
        broadcast_msg = '[' + room_name + '] '+' '+ message
        #sending the broadcast message to the client
        client_socket.send(broadcast_msg.encode('utf-8'))
