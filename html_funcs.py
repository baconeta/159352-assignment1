import json
import api_funcs

# Template data that is supplied into all pages created by the server
template_html_open = "<!DOCTYPE html>\n<html lang='en'>\n"
template_head_open = "<head>\n<meta charset='UTF-8'>\n<title>159352 Portfolio</title>\n"
template_head_close = "<link rel='stylesheet' href='main.css''>\n</head>\n"
template_body_open = "<body>\n<div class='navbar'>\n{0}</div>\n"
template_navs = ["<a {0} href='/index.html'>Home</a>\n", "<a {0} href='/portfolio'>Portfolio</a>\n",
                 "<a {0} href='/research'>Research</a>\n"]
template_body_close = "</body>\n"
template_html_close = "</html>\n"


# Used to verify and serve the specific required response and page the browser requested
def get_requested_page(resource_requested, post_reply="") -> tuple[bytes, bytes]:
    # Build requested HTML file
    if resource_requested == "" or resource_requested == "index.html":
        return make_html_file("index")
    elif resource_requested == "portfolio" or resource_requested == "portfolio.html":
        return make_html_file("portfolio", post_reply)
    elif resource_requested == "research" or resource_requested == "research.html":
        return make_html_file("research", post_reply)

    #  Or get file or resource and return that
    try:
        f = open(resource_requested, "rb")
        body = f.read()
        header = "HTTP/1.1 200 OK\r\n\r\n".encode()
        return header, body
    except IOError:
        return make_html_file("404", "<h1>\n404 Not Found\n</h1>\n")


# Creates an HTML file based on the filename given.
# Returns the header with the relevant HTTP response code, and the body data, all encoded as bytes
def make_html_file(filename, additional_body="") -> tuple[bytes, bytes]:
    if filename == "404":
        header = "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8')
    else:
        header = "HTTP/1.1 200 OK\r\n\r\n".encode('utf-8')

    body = template_html_open + template_head_open

    # page relevant header content is added here
    body += generate_html_head(filename)

    body += template_head_close + template_body_open.format(build_nav_bar(filename))

    # page relevant body content is added here
    body += generate_html_body(filename)
    body += additional_body

    body = body + template_body_close + template_html_close
    body = body.encode('utf-8')
    return header, body


# Fetch the requested file, and send the contents back to the client in an HTTP response.
def generate_html_head(filename) -> str:
    if filename == "portfolio":
        return "<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'></script>\n"
    if filename == "research":
        return "<script type='text/javascript' src='https://canvasjs.com/assets/script/canvasjs.stock.min.js'></script>\n"
    return ""


# Generate the html body based on filename. Returns nothing if we don't handle this specific page
def generate_html_body(filename) -> str:
    if filename == "portfolio":
        return generate_portfolio_body()
    if filename == "research":
        return generate_research_body()
    if filename == "index":
        return "<h3>Login successful.</h3>\n<h2>Welcome to your stock portfolio and research centre, Josh</h2>\n<p>" \
               "Use the links on the bar above to view and update your portfolio, or access your research centre.</p>\n"
    return ""


# Ensures the current page has the active class tag and all other nav tags have nothing
def build_nav_bar(page) -> str:
    return "".join([s.format("class='active'") if page in s else s.format("") for s in template_navs])


# Generate the portfolio html body
def generate_portfolio_body() -> str:
    portfolio_body = ""

    # first embed the list of symbols
    portfolio_body += get_autocomplete_symbols()

    portfolio_body += "<h1>Investment Portfolio</h1>\n<a href='https://iexcloud.io'>Data provided by IEX " \
                      "Cloud</a>\n<br>\n"

    # now build the table
    table_data = make_table_from_json_file()
    portfolio_body += table_data

    # add html form
    portfolio_body += "<br>\n<form method='post' target='_self'>\n<label for='stock-symbol' style='width: 100px;'>" \
                      "\nStock Symbol:\n</label>\n<input id='stock-symbol' name='stock-symbol' " \
                      "list='symbols' required type='text'>\n<br>\n<br>\n<label for='quantity' style='width: 100px; " \
                      "display:inline-block'>\nQuantity:\n</label>\n<input id='quantity' name='quantity' required " \
                      "step=any type='number' value='0'>\n<br>\n<br>\n<label for='price' style='width: 100px; " \
                      "display:inline-block'>\nShare price: $\n</label>\n<input id='price' name='price' step=0.01 " \
                      "type='number' value='0.00'>\n<br>\n<br>\n<button type='reset' inline='true'>\nReset\n</button>\n" \
                      "<button type='submit' formmethod='post' inline='true'>\nUpdate\n</button>\n</form>\n"
    return portfolio_body


# Grabs and formats the valid stock symbols (mostly used for the autocomplete symbol fields)
def get_autocomplete_symbols() -> str:
    symbols_list = "<datalist id='symbols'>\n"
    for symbol in api_funcs.get_symbols():
        symbols_list += f"<option value='{symbol}'>\n"
    symbols_list += "</datalist>\n"
    return symbols_list


# Generate the portfolio html body
def generate_research_body() -> str:
    research_body = ""

    # first embed the list of symbols
    research_body += get_autocomplete_symbols()

    research_body += "<h1>Stock Research Centre</h1>\n<a href='https://iexcloud.io'>Data provided by IEX " \
                     "Cloud</a>\n<br>\n"

    # add form
    research_body += "<br>\n<form method='post' target='_self'>\n<label for='stock-symbol' style='width: 100px;'>" \
                     "\nStock Symbol:\n</label>\n<input id='stock-symbol' name='stock-symbol' " \
                     "required type='text' list='symbols' inline='true'>\n<button type='submit' formmethod='post' " \
                     "inline='true'>\nResearch\n</button>\n</form>\n"
    return research_body


# Grabs portfolio data from file and builds an HTML table out of it. Returns HTML as a single formatted string
def make_table_from_json_file() -> str:
    portfolio_data = {"Stock_Data": []}
    table_str = "<table align='center' id='table' border='1'>\n<tr>\n<th style='width:120px'>\nStock\n</th>\n<th " \
                "style='width:120px'>\nQuantity\n</th>\n<th style='width:120px'>\nPrice\n</th>\n<th " \
                "style='width:120px'>\nGain/Loss\n</th>\n</tr>"
    try:
        with open("portfolio.json", "r") as f:
            portfolio_data = json.load(f)  # returns a dictionary {"Stock_Data": [LIST OF STOCKS HELD]}
    except IOError:
        # file doesn't exist
        pass

    # Handle batch query to grab prices of all stocks in the portfolio
    stocks_to_price = [s["stock-symbol"] for s in portfolio_data["Stock_Data"]]
    if stocks_to_price:  # this will fail if there were no stocks supplied or no json data returned i.e. empty portfolio
        prices = api_funcs.get_batch_current_prices(stocks_to_price)
        prices = {k: v['quote']['latestPrice'] for (k, v) in prices.items()}

        for stock in portfolio_data["Stock_Data"]:
            paid_price = float(stock["price"])
            gain = round(100 * (float(prices[stock['stock-symbol']]) - paid_price) / paid_price, 2)
            table_str += "<tr>\n"
            table_str += f"<td>{stock['stock-symbol']}</td>\n"
            table_str += f"<td>{stock['quantity']}</td>\n"
            table_str += f"<td>{stock['price']}</td>\n"
            table_str += f"<td>{str(gain)}%</td>\n"
            table_str += "</tr>\n"

    # add empty row and close tag
    table_str += "<tr><td><br></td><td> </td><td> </td><td> </td></tr></table>\n"
    return table_str


# Builds stock statistics for a specific stock HTML output
def get_stock_stats(stock_to_research) -> str:
    try:
        stock_symbol = stock_to_research.split("=")[1]
        stats = api_funcs.get_stock_data(stock_symbol)

        data = "<div style='text-align: left; width: 400px; margin: auto; font-size: 18px'>\n"
        data += "\n<br>\nSymbol:<i> " + stock_symbol.upper() + "</i>"

        if stats is None:
            data += "Error grabbing stock stat data. Maybe that stock doesn't exist?\n<br>\n"
        else:  # Only put the rest of the data in the HTML if we were able to grab stats for this stock
            data += "\n<br>\nCompany Name:<i> " + stats["companyName"] + "</i>"
            data += "\n<br>\nPE ratio:<i> " + str(round(stats["peRatio"], 4)) + "</i>"
            data += "\n<br>\nMarket Capitalization:<i> " + "{:,}".format(stats["marketcap"]) + "</i>"
            data += "\n<br>\n52 week high:<i> " + str(stats["week52high"]) + "</i>"
            data += "\n<br>\n52 week low:<i> " + str(stats["week52low"]) + "</i>"
        data += "\n</div>\n"

        # prepare the chart
        data += build_stock_chart(stock_symbol.upper())

        # now add the chart
        data += "<div id='stockChart' style='height: 450px; width: 50%; margin-left: auto; margin-right: auto;'>\n</div>\n"
        return data
    except (IndexError, KeyError, AttributeError):
        return "\n<br>\nThe stock you entered doesn't exist or was entered incorrectly.\n"


# Builds stock chart for a specific stock for HTML output
def build_stock_chart(stock) -> str:
    # get stock data
    chart_data = api_funcs.get_chart_data(stock)
    if chart_data is None:
        return f"\n<br>\nError grabbing data about {stock}. Try again or another stock.\n<br>\n"

    # add script and embed stock data
    chart = "\n<script type='text/javascript'>\nwindow.onload = function () { let dataPoints = []; let json_data = "
    chart += str(chart_data) + "; "
    chart += "let stockChart = new CanvasJS.StockChart('stockChart', { charts: [{ data: [{ type: 'line', dataPoints: " \
             "dataPoints }] }], navigator: { slider: { minimum: new Date(2021,04,07), maximum: new Date(2022," \
             "04,07) } } }); for (let i = 0; i < json_data.length; i++) { dataPoints.push({x: new Date(json_data[" \
             "i].date), y: Number(json_data[i].close)}); } stockChart.render(); }\n</script>\n"
    return chart
