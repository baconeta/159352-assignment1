# Based on original file by Sunil Lal
# Written by Joshua Pearson for 159.352 Assignment 1 (20019455)

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

serverSocket = socket(AF_INET, SOCK_STREAM)
serverPort = 8080
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(("", serverPort))

serverSocket.listen(5)
print('The server is running.')


# Fetch the requested file, and send the contents back to the client in an HTTP response.
def getFile(filename):
    try:
        # open and read the file contents. This becomes the body of the HTTP response
        f = open(filename, "rb")
        body = f.read()
        header = "HTTP/1.1 200 OK\r\n\r\n".encode()
    except IOError:
        # Send HTTP response message for resource not found
        header = "HTTP/1.1 404 Not Found\r\n\r\n".encode()
        body = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode()
    return header, body


# Set up require authentication response
def need_authentication():
    header = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic\r\n".encode()
    body = "<html><head></head><body><h1>Authenticate please</h1></body></html>".encode()
    return header, body


# Parse the headers and return a dict containing the browsers request
def parse_headers(message):
    split_message = message.split()
    http_method = split_message[0]
    resource = split_message[1][1:]
    transfer_method = split_message[2]
    _, request_headers = message.split('\r\n', 1)
    answer = email.message_from_file(StringIO(request_headers))
    parsed_headers = dict(answer.items())
    parsed_headers["HTTP-Method"] = http_method
    parsed_headers["Resource"] = resource
    parsed_headers["Transfer-Method"] = transfer_method
    return parsed_headers


# Verify basic authentication from the browser
def check_authentication(auth_token):
    username_password_bytes = "20019455:20019455".encode()
    encoded_auth = base64.b64encode(username_password_bytes).decode()
    header_safe_auth = "Basic " + encoded_auth

    if header_safe_auth == auth_token:
        return True
    else:
        return False


# Used to verify and serve the specific required response and page the browser requested
def generate_requested_page(parsed_headers):
    resource_requested = parsed_headers.get("Resource")
    if resource_requested == "":
        return getFile("index.html")
    elif resource_requested == "portfolio":
        return getFile("portfolio.html")
    elif resource_requested == "research":
        return getFile("research.html")
    else:
        return getFile("404.html")


def serve_site(parsed_headers):
    # temporary response
    header = "HTTP/1.1 200 OK\r\n\r\n".encode()
    body = "<html><head></head><body><h1>You passed authentication</h1></body></html>".encode()
    request_type = parsed_headers.get("HTTP-Method")
    if request_type == "GET":
        header, body = generate_requested_page(parsed_headers)
    elif request_type == "POST":
        pass
        # handle_post_request(parsed_headers)

    return header, body


# We process client request here
def process_connection(this_connection_socket):
    # Receives the request message from the client
    message = this_connection_socket.recv(1024).decode()

    if len(message) > 1:
        parsed_headers = parse_headers(message)
        resource = parsed_headers.get("Resource")
        response_body, response_header = handle_request(parsed_headers)

        # Send the HTTP response header line to the connection socket
        this_connection_socket.send(response_header)
        # Send the content of the HTTP body (e.g. requested file) to the connection socket
        this_connection_socket.send(response_body)

    # Close the client connection socket
    this_connection_socket.close()


# Verifies authentication and responds with the appropriate response based on the browser request
def handle_request(parsed_headers):
    auth_token = parsed_headers.get("Authorization")
    if auth_token is not None:
        if check_authentication(auth_token):
            # successful auth, can now continue serving site
            response_header, response_body = serve_site(parsed_headers);
        else:
            # failed auth
            response_header, response_body = need_authentication()
    else:
        response_header, response_body = need_authentication()
    return response_body, response_header


# Main web server loop. It simply accepts TCP connections, and get the request processed in separate threads.
while True:
    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()
    # Clients timeout after 60 seconds of inactivity and must reconnect.
    connectionSocket.settimeout(60)
    # start new thread to handle incoming request
    _thread.start_new_thread(process_connection, (connectionSocket,))
