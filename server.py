# Written by Joshua Pearson for 159.352 Assignment 1 (20019455)
# Based on original server file by Sunil Lal

# This is a simple HTTP server which listens on port 8080, accepts connection request, and processes the client request
# in separate threads.

# This web server runs on python v3
# Usage: execute this program, open your browser (preferably chrome) and type http://servername:8080
# e.g. if server.py and browser are running on the same machine, then use http://localhost:8080
import base64
from io import StringIO
from json import JSONDecodeError
from socket import *
import _thread
import email
import json
import requests

template_html_open = "<!DOCTYPE html><html lang='en'>"
template_head_open = "<head><meta charset='UTF-8'><title>159352 Portfolio</title>"
template_head_close = "</head>"
template_body_open = "<body style='text-align:center;' id='body'>"
template_body_close = "</body>"
template_html_close = "</html>"

serverSocket = socket(AF_INET, SOCK_STREAM)
serverPort = 8080
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(("", serverPort))

serverSocket.listen(5)
print('The server is running.')
api_sandbox_ref_data = "https://sandbox.iexapis.com/stable/ref-data/symbols?token=Tsk_d4d4b130553e4bed98683e3cab9f360e"


def get_symbols_from_api():
    response = requests.get(api_sandbox_ref_data)
    list_of_symbols = []
    if response.status_code == 200:
        for symbol in response.json():
            if symbol.get("type") == "cs":
                list_of_symbols.append(symbol.get("symbol"))
    return list_of_symbols


# Fetch the requested file, and send the contents back to the client in an HTTP response.
def generate_html_head(filename):
    # TODO make sure this only uses the necessary header data
    if filename == "portfolio":
        return "<script data-main='scripts/main' src='scripts/require.js'></script> <script " \
               "src='scripts/main.js'></script> <script " \
               "src='https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'></script> "
    # TODO handle research page
    return ""


def generate_html_body(filename):
    # TODO make this populate the table correctly from the JSON file or else create a blank table (do both together?)
    # TODO make the stock symbol populate from API call data
    if filename == "portfolio":
        portfolio_body = ""

        # first prepare the symbols options
        portfolio_body += "<datalist id='symbols'>"
        for symbol in get_symbols_from_api():
            portfolio_body += f"<option value='{symbol}'>"
        portfolio_body += "</datalist>"

        # now build the table
        table_data = make_table_from_json_file()
        portfolio_body += "<h1>Josh's Investment Portfolio</h1>"
        portfolio_body += table_data
        portfolio_body += "<br> <form method='post' target='_self'> <label for='stock-symbol' style='width: 100px; " \
                          "display:inline-block'>Stock Symbol:</label> <input id='stock-symbol' name='stock-symbol' " \
                          "list='symbols' required type='text'><br><br> <label for='quantity' style='width: 100px; " \
                          "display:inline-block'>Quantity:</label> <input id='quantity' name='quantity' required " \
                          "step=any type='number' value='0'><br><br> <label for='price' style='width: 100px; " \
                          "display:inline-block'>Share price: $</label> <input id='price' name='price' step=0.01 " \
                          "type='number' value='0.00'><br><br> <button type='reset' inline='true'>Reset</button> " \
                          "<button type='submit' formmethod='post' inline='true'>Update</button> </form> "
        return portfolio_body
    # TODO handle research page
    return ""


def make_file(filename, additional_header="", additional_body=""):
    if filename == "404":
        return "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8'), \
               "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode('utf-8')

    header = "HTTP/1.1 200 OK\r\n\r\n".encode('utf-8')

    body = template_html_open + template_head_open

    # add any extra header content here
    body += generate_html_head(filename)
    body += additional_header

    body += template_head_close + template_body_open

    # add any extra body content here
    body += generate_html_body(filename)
    body += additional_body

    body = body + template_body_close + template_html_close
    body = body.encode('utf-8')
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
    if http_method == "POST":  # To ensure we grab the query payload for handling later
        parsed_headers["Query"] = message.split("\r\n")[-1]

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
def generate_requested_page(parsed_headers, post_reply=""):
    resource_requested = parsed_headers.get("Resource")
    if resource_requested == "" or resource_requested == "index.html":
        return make_file("index")
    elif resource_requested == "portfolio" or resource_requested == "portfolio.html":
        return make_file("portfolio", "", post_reply)
    elif resource_requested == "research" or resource_requested == "research.html":
        return make_file("research")
    else:
        return make_file("404")
    # TODO possibly add some way to handle extra embedded scripts from inside the html if required?


def serve_site(parsed_headers):
    request_type = parsed_headers.get("HTTP-Method")
    if request_type == "GET":
        header, body = generate_requested_page(parsed_headers)
    elif request_type == "POST":
        post_reply = handle_portfolio_change(parsed_headers.get("Query"))  # currently, the only POST available
        header, body = generate_requested_page(parsed_headers, post_reply)
        # handle_post_request(parsed_headers) TODO to add other post request handling?
    else:
        header = "HTTP/1.1 501 Not Implemented\r\n\r\n".encode()
        body = "<html><head></head><body><h1>501 request not handled by server.</h1></body></html>".encode()

    return header, body


# We process client request here
def process_connection(this_connection_socket):
    # Receives the request message from the client
    message = this_connection_socket.recv(2048).decode()
    # print(message)
    if len(message) > 1:
        parsed_headers = parse_headers(message)
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
            response_header, response_body = serve_site(parsed_headers)
        else:
            # failed auth
            response_header, response_body = need_authentication()
    else:
        response_header, response_body = need_authentication()
    return response_body, response_header


# Gets the portfolio file from the filesystem, and creates it if it doesn't exist
def get_portfolio_file():
    try:
        with open("portfolio.json") as f:
            portfolio_data = f.read()
            return portfolio_data
    except FileNotFoundError:
        return ""


def add_json_to_file(stock_data):
    pass


# Hardcoded handling of adding a new stock into the file
def add_stock(data):
    d = data.split("&")
    ticker = d[0].split("=")
    quantity = d[1].split("=")
    price = d[2].split("=")
    new_json_dict = {ticker[0]: ticker[1],
                     quantity[0]: quantity[1],
                     price[0]: price[1]}

    portfolio_data = {"Stock_Data": []}

    new_quantity = float(quantity[1])

    try:
        with open("portfolio.json", "r") as f:
            portfolio_data = json.load(f)  # returns a dictionary {"Stock_Data": [LIST OF STOCKS HELD]}
    except IOError:
        # file doesn't exist yet, we create it later
        pass
    except JSONDecodeError:
        # json file formatted incorrectly, abort operation
        return "<br>Error in portfolio.json file. Please see server operator."

    stock_exists = False
    for stock in portfolio_data["Stock_Data"]:
        if stock.get("stock-symbol") == ticker[1]:
            new_quantity += float(stock.get("quantity"))
            stock_exists = True
            if new_quantity < 0:
                return "<br>No short selling allowed."  # not enough stocks to sell, no short selling allowed
            elif new_quantity == 0:
                portfolio_data["Stock_Data"].remove(stock)
                break
            else:
                buy_price = float(price[1])
                add_quantity = float(quantity[1])
                old_price = float(stock.get("price"))
                old_quantity = float(stock.get("quantity"))

                if add_quantity > 0:
                    new_price = round((((old_price * old_quantity) + (buy_price * add_quantity)) / new_quantity), 2)
                else:
                    new_price = old_price
                stock.update({"price": str(new_price), "quantity": str(new_quantity)})

    if not stock_exists:
        if new_quantity > 0:
            portfolio_data["Stock_Data"].append(new_json_dict)
        else:
            return "<br>You can't sell shares you don't have!"

    with open("portfolio.json", "w") as f:
        json.dump(portfolio_data, f, indent=4)

    if new_quantity == 0:
        return f"<br>All available shares of {ticker[1]} sold."
    return "<br>Portfolio updated."


def handle_portfolio_change(data):
    # output any relevant messages to the html

    # if the stock is not in the portfolio, then add it to the portfolio
    return add_stock(data)


def make_table_from_json_file():
    portfolio_data = {"Stock_Data": []}
    table_str = "<table align='center' id='table' border='1'><tr><th style='width:120px'>Stock</th><th " \
                "style='width:120px'>Quantity</th><th style='width:120px'>Price</th><th " \
                "style='width:120px'>Gain/Loss</th></tr>"
    try:
        with open("portfolio.json", "r") as f:
            portfolio_data = json.load(f)  # returns a dictionary {"Stock_Data": [LIST OF STOCKS HELD]}
    except IOError:
        # file doesn't exist yet
        pass

    for stock in portfolio_data["Stock_Data"]:
        table_str += "<tr>"
        table_str += "<td>" + stock.get("stock-symbol") + "</td>"
        table_str += "<td>" + stock.get("quantity") + "</td>"
        table_str += f"<td>{stock.get('price')}</td>"
        table_str += "<td>" "</td>"  # TODO add gain/loss here
        table_str += "</tr>"

    # add empty row and close tag
    table_str += "<tr><td><br></td><td> </td><td> </td><td> </td></tr></table>"
    return table_str


# Main web server loop. It simply accepts TCP connections, and get the request processed in separate threads.
while True:
    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()
    # Clients timeout after 60 seconds of inactivity and must reconnect.
    connectionSocket.settimeout(60)
    # start new thread to handle incoming request
    _thread.start_new_thread(process_connection, (connectionSocket,))
