# Written by Joshua Pearson for 159.352 Assignment 1 (20019455)
# Based on original server file by Sunil Lal

# This is a simple HTTP server which listens on port 8080, accepts connection request, and processes the client request
# in separate threads.

# This web server runs on python v3
# Usage: execute this program, open your browser (preferably chrome) and type http://servername:8080
# e.g. if server.py and browser are running on the same machine, then use http://localhost:8080

import base64
from io import StringIO
from socket import *
import _thread
import email
import sys

import api_funcs
import html_funcs
import portfolio_funcs

serverSocket = socket(AF_INET, SOCK_STREAM)
serverPort = int(sys.argv[1])
# serverPort = 8080
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(("", serverPort))


# We process client requests here
def process_connection(this_connection_socket):
    # Receives the request message from the client
    message = this_connection_socket.recv(8192).decode()  # Heroku uses an 8kb buffer
    parsed_headers = parse_headers(message)
    if "Content-Length" in message:
        expected_content_len = int(parsed_headers.get("Content-Length"))
        query = ""
        while len(query) < expected_content_len:  # Ensure we have received the entire query payload
            data = message.split("\r\n\r\n")
            if len(data[-1]) == expected_content_len:
                query = data[-1]
            else:
                message = this_connection_socket.recv(expected_content_len).decode()
        parsed_headers["Query"] = query
    if len(message) > 1:
        response_body, response_header = handle_request(parsed_headers)

        # Send the HTTP response combined header and body to the connection socket
        this_connection_socket.send(response_header + "\r\n".encode() + response_body)

    # Close the client connection socket
    this_connection_socket.close()


# Parse the headers and return a dict containing the browsers request
def parse_headers(message) -> dict:
    parsed_headers = {}
    if len(message.split(" ")) == 1:  # To ensure we grab the query payload for handling later
        parsed_headers["Query"] = message.split("\r\n")[-1]
        return parsed_headers

    _, request_headers = message.split('\r\n', 1)
    answer = email.message_from_file(StringIO(request_headers))

    parsed_headers = dict(answer.items())

    # Manually set the single data message inputs into the same dictionary
    split_message = message.split()
    http_method = split_message[0]
    parsed_headers["HTTP-Method"] = http_method
    resource = split_message[1][1:]
    parsed_headers["Resource"] = resource
    transfer_method = split_message[2]
    parsed_headers["Transfer-Method"] = transfer_method

    return parsed_headers


# Verifies authentication and responds with the appropriate response based on the browser request
def handle_request(parsed_headers) -> tuple[bytes, bytes]:
    auth_token = parsed_headers["Authorization"]
    if auth_token is not None:
        if check_authentication(auth_token):
            # successful auth, can now continue serving site
            response_header, response_body = serve_site(parsed_headers)
        else:
            # failed auth
            response_header, response_body = need_authentication()
    else:
        response_header, response_body = need_authentication()
    return response_body, response_header


# Set up require authentication response
def need_authentication() -> tuple[bytes, bytes]:
    header = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic\r\n".encode()
    body = "<html><head></head><body><h1>Authenticate please</h1></body></html>".encode()
    return header, body


# Verify basic authentication from the browser
def check_authentication(auth_token) -> bool:
    username_password_bytes = "20019455:20019455".encode()
    encoded_auth = base64.b64encode(username_password_bytes).decode()
    header_safe_auth = "Basic " + encoded_auth

    return header_safe_auth == auth_token


# Handles the generating and serving of all related site data once request is authenticated and validated
def serve_site(parsed_headers) -> tuple[bytes, bytes]:
    request_type = parsed_headers["HTTP-Method"]
    resource_requested = parsed_headers["Resource"]
    if request_type == "GET":
        header, body = html_funcs.get_requested_page(resource_requested)
    elif request_type == "POST":
        post_reply = ""
        if resource_requested == "portfolio" or resource_requested == "portfolio.html":
            post_reply = portfolio_funcs.handle_portfolio_change(parsed_headers["Query"])
        elif resource_requested == "research" or resource_requested == "research.html":
            post_reply = html_funcs.get_stock_stats(parsed_headers["Query"])
        header, body = html_funcs.get_requested_page(resource_requested, post_reply)
    else:  # this server only handles POST and GET requests
        header = "HTTP/1.1 501 Not Implemented\r\n\r\n".encode()
        body = "<html><head></head><body><h1>501 request not handled by server.</h1></body></html>".encode()

    return header, body


api_funcs.get_symbols_from_api()  # grabbed and cached at the beginning of server runtime for first page efficiency

serverSocket.listen(5)
print('The server is running and ready for requests.')

# Main web server loop. It accepts TCP connections, and get the request processed in separate threads.
while True:
    # Set up a new connection from the client
    connectionSocket, address = serverSocket.accept()
    # Clients timeout after 60 seconds of inactivity and must reconnect.
    connectionSocket.settimeout(60)
    # start new thread to handle incoming request
    _thread.start_new_thread(process_connection, (connectionSocket,))
