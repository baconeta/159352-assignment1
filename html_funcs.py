import json
import api_funcs

template_html_open = "<!DOCTYPE html><html lang='en'>"
template_head_open = "<head><meta charset='UTF-8'><title>159352 Portfolio</title>"
template_head_close = "</head>"
template_body_open = "<body style='text-align:center;' id='body'>"
template_body_close = "</body>"
template_html_close = "</html>"


# Used to verify and serve the specific required response and page the browser requested
def get_requested_page(parsed_headers, post_reply="") -> tuple[bytes, bytes]:
    resource_requested = parsed_headers.get("Resource")
    if resource_requested == "" or resource_requested == "index.html":
        return make_html_file("index")
    elif resource_requested == "portfolio" or resource_requested == "portfolio.html":
        return make_html_file("portfolio", post_reply)
    elif resource_requested == "research" or resource_requested == "research.html":
        return make_html_file("research", post_reply)
    # try and return a file? otherwise 404
    else:
        return make_html_file("404")


def make_html_file(filename, additional_body="") -> tuple[bytes, bytes]:
    if filename == "404":
        return "HTTP/1.1 404 Not Found\r\n\r\n".encode('utf-8'), \
               "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode('utf-8')
    header = "HTTP/1.1 200 OK\r\n\r\n".encode('utf-8')

    body = template_html_open + template_head_open

    # page relevant header content is added here
    body += generate_html_head(filename)

    body += template_head_close + template_body_open

    # page relevant body content is added here
    body += generate_html_body(filename)
    body += additional_body

    body = body + template_body_close + template_html_close
    body = body.encode('utf-8')
    return header, body


# Fetch the requested file, and send the contents back to the client in an HTTP response.
def generate_html_head(filename) -> str:
    if filename == "portfolio":
        return "<script src='https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js'></script> "
    if filename == "research":
        return "<script type='text/javascript' src='https://canvasjs.com/assets/script/canvasjs.stock.min.js'></script>"
    return ""


def generate_html_body(filename) -> str:
    if filename == "portfolio":
        return generate_portfolio_body()
    if filename == "research":
        return generate_research_body()
    return ""


# Generate the portfolio html body
def generate_portfolio_body() -> str:
    portfolio_body = ""

    # first prepare the symbols options
    portfolio_body += "<datalist id='symbols'>"
    for symbol in api_funcs.list_of_symbols:
        portfolio_body += f"<option value='{symbol}'>"
    portfolio_body += "</datalist>"

    # now build the table
    table_data = make_table_from_json_file()
    portfolio_body += "<h1>Josh's Investment Portfolio</h1><a href='https://iexcloud.io'>Data provided by IEX " \
                      "Cloud</a><br>"
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


# Generate the portfolio html body
def generate_research_body() -> str:
    research_body = ""

    # first prepare the symbols options
    research_body += "<datalist id='symbols'>"
    for symbol in api_funcs.list_of_symbols:
        research_body += f"<option value='{symbol}'>"
    research_body += "</datalist>"

    research_body += "<h1>Josh's Stock Research Centre</h1><a href='https://iexcloud.io'>Data provided by IEX " \
                     "Cloud</a><br>"
    research_body += "<br> <form method='post' target='_self'> <label for='stock-symbol' style='width: 100px; " \
                     "display:inline-block'>Stock Symbol:</label> <input id='stock-symbol' name='stock-symbol' " \
                     "required type='text' list='symbols' inline='true'> <button type='submit' formmethod='post' " \
                     "inline='true'>Research</button> </form> "
    return research_body


def make_table_from_json_file() -> str:
    portfolio_data = {"Stock_Data": []}
    table_str = "<table align='center' id='table' border='1'><tr><th style='width:120px'>Stock</th><th " \
                "style='width:120px'>Quantity</th><th style='width:120px'>Price</th><th " \
                "style='width:120px'>Gain/Loss</th></tr>"
    try:
        with open("portfolio.json", "r") as f:
            portfolio_data = json.load(f)  # returns a dictionary {"Stock_Data": [LIST OF STOCKS HELD]}
    except IOError:
        # file doesn't exist
        pass

    # Handle batch query to grab prices of all stocks in the portfolio
    stocks_to_price = [sym.get("stock-symbol") for sym in portfolio_data["Stock_Data"]]
    prices = api_funcs.get_batch_current_prices(stocks_to_price)
    prices = {k: v['quote']['latestPrice'] for (k, v) in prices.items()}

    for stock in portfolio_data["Stock_Data"]:
        paid_price = float(stock.get("price"))
        gain = 100 * (float(prices[stock['stock-symbol']]) - paid_price) / paid_price
        gain = round(gain, 2)  # price should be to 2 decimal places
        table_str += "<tr>"
        table_str += f"<td>{stock.get('stock-symbol')}</td>"
        table_str += f"<td>{stock.get('quantity')}</td>"
        table_str += f"<td>{stock.get('price')}</td>"
        table_str += f"<td>{str(gain)}%</td>"
        table_str += "</tr>"

    # add empty row and close tag
    table_str += "<tr><td><br></td><td> </td><td> </td><td> </td></tr></table>"
    return table_str


def get_stock_stats(stock_to_research) -> str:
    try:
        stock_symbol = stock_to_research.split("=")[1]
        stats = api_funcs.get_stock_data(stock_symbol)

        data = "<div style='text-align: left; width: 350px; margin: auto; font-size: 18px'>"
        if stats is None:
            data += "Error grabbing stock stat data. Data below may be incomplete.<br>"

        # stats.get() calls will be empty objects if stats is None which is good behaviour here
        data += "<br>Symbol: " + stock_symbol.upper()
        data += "<br>Company Name: " + stats.get("companyName")
        data += "<br>PE ratio: " + str(stats.get("peRatio"))
        data += "<br>Market Capitalization: " + str(stats.get("marketcap"))
        data += "<br>52 week high: " + str(stats.get("week52high"))
        data += "<br>52 week low: " + str(stats.get("week52low"))
        data += "</div>"

        # prepare the chart
        data += build_stock_chart(stock_symbol.upper())

        # now add the chart
        data += "<div id='stockChart' style='height: 450px; width: 50%; margin-left: auto; margin-right: auto;'></div>"
        return data
    except (IndexError, KeyError) as e:
        print(e)
        return "<br>The stock you entered doesn't exist or was entered incorrectly."


def build_stock_chart(stock) -> str:
    # get stock data
    chart_data = api_funcs.get_chart_data(stock)
    if chart_data is None:
        return f"<br>Error grabbing data about {stock}. Try again or another stock.<br>"

    # add script and embed stock data
    chart = "<script type='text/javascript'> window.onload = function () { let dataPoints = []; let json_data = "
    chart += str(chart_data) + "; "
    chart += "let stockChart = new CanvasJS.StockChart('stockChart', { charts: [{ data: [{ type: 'line', dataPoints: " \
             "dataPoints }] }], navigator: { slider: { minimum: new Date(2021,04,07), maximum: new Date(2022," \
             "04,07) } } }); for (let i = 0; i < json_data.length; i++) { dataPoints.push({x: new Date(json_data[" \
             "i].date), y: Number(json_data[i].close)}); } stockChart.render(); }</script>"
    return chart
