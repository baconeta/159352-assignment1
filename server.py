# Author: Sunil Lal

# This is a simple HTTP server which listens on port 8080, accepts connection request, and processes the client request
# in separate threads. It implements basic service functions (methods)
# which generate HTTP response to service the HTTP requests.
# Currently, there are 3 service functions; default, welcome and getFile.
# The process function maps the request URL pattern to the service function.
# When the requested resource in the URL is empty,
# the default function is called which currently invokes the welcome function.
# The welcome service function responds with a simple HTTP response: "Welcome to my homepage".
# The getFile service function fetches the requested html or img file and
# generates an HTTP response containing the file contents and appropriate headers.

# To extend this server's functionality, define your service function(s),
# and map it to suitable URL patterns in the process function.

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
print('The server is running')


# Server should be up and running and listening to the incoming connections

# Extract the given header value from the HTTP request message
def getHeader(message, header):
    if message.find(header) > -1:
        value = message.split(header)[1].split()[0]
    else:
        value = None

    return value


# service function to fetch the requested file, and send the contents back to the client in a HTTP response.
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


# service function to generate HTTP response with a simple welcome message
def need_authentication():
    header = "HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic\r\n".encode()
    body = "<html><head></head><body><h1>Authenticate please</h1></body></html>".encode()

    return header, body


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


# default service function
def check_authentication(auth_token):
    username_password_bytes = "20019455:20019455".encode()
    encoded_auth = base64.b64encode(username_password_bytes).decode()
    header_safe_auth = "Basic " + encoded_auth

    if header_safe_auth == auth_token:
        return True
    else:
        return False


# We process client request here. The requested resource in the URL is mapped to a
# service function which generates the HTTP response that is eventually returned to the client.
def serve_site(parsed_headers):
    # temporary response
    header = "HTTP/1.1 200 OK\r\n\r\n".encode()
    body = "<html><head></head><body><h1>You passed authentication</h1></body></html>".encode()
    return header, body


def process(this_connection_socket):
    # Receives the request message from the client
    message = this_connection_socket.recv(1024).decode()

    if len(message) > 1:
        parsed_headers = parse_headers(message)
        resource = parsed_headers.get("Resource")
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

        # Send the HTTP response header line to the connection socket
        this_connection_socket.send(response_header)
        # Send the content of the HTTP body (e.g. requested file) to the connection socket
        this_connection_socket.send(response_body)

    # Close the client connection socket
    this_connection_socket.close()


# Main web server loop. It simply accepts TCP connections, and get the request processed in separate threads.
while True:
    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()
    # Clients timeout after 60 seconds of inactivity and must reconnect.
    connectionSocket.settimeout(60)
    # start new thread to handle incoming request
    _thread.start_new_thread(process, (connectionSocket,))

# # Extract the path of the requested object from the message
# # Because the extracted path of the HTTP request includes
# # a character '/', we read the path from the second character
# resource = message.split()[1][1:]
#
# # map requested resource (contained in the URL) to specific function which generates HTTP response
# if resource == "":  # should serve index.html if authenticated
#     response_header, response_body = default(message)
# elif resource == "portfolio" or "research":  # assignment specific resources
#     response_header, response_body = authentication(message, resource + ".html")
# else:  # serve the requested file if authentication passes
#     response_header, response_body = authentication(message, resource)
