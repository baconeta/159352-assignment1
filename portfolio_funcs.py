import json
import api_funcs
from json import JSONDecodeError


def handle_portfolio_change(data) -> str:
    # returns any relevant error or info messages as text to the requester based on the change and validation
    return update_stock_portfolio(data)


# Updates the stock portfolio based on the POST data given and returns an appropriate response or error.
# A very large function that could be handled better but works with very good error handling.
def update_stock_portfolio(data) -> str:
    # Split the query into its separate elements
    try:
        d = data.split("&")
        ticker = d[0].split("=")
        quantity = d[1].split("=")
        price = d[2].split("=")
        new_json_dict = {ticker[0]: ticker[1],
                         quantity[0]: quantity[1],
                         price[0]: price[1]}
    except IndexError as e:
        print(e)
        return "<br>Error handling request."

    ticker[1] = ticker[1].upper()

    # Check if the stock exists in our API data
    if ticker[1] not in api_funcs.get_symbols():
        return f"<br>The stock {ticker[1]} doesn't exist."

    new_quantity = float(quantity[1])

    # Ensure valid purchase input and price
    if new_quantity == 0:
        return "<br>You can't do anything with 0 shares."

    if new_quantity > 0 and float(price[1]) <= 0:
        return "<br>You can't buy shares for nothing...or less."

    portfolio_data = {"Stock_Data": []}

    # Read and prepare existing portfolio data, if we have any
    try:
        with open("portfolio.json", "r") as f:
            portfolio_data = json.load(f)  # returns a dictionary {"Stock_Data": [LIST OF STOCKS HELD]}
    except IOError:
        # file doesn't exist yet, we create it later
        pass
    except JSONDecodeError:
        # json file formatted incorrectly, abort operation
        return "<br>Error in portfolio.json file. Please see server operator."

    # Handle the portfolio change request
    stock_exists = False
    for stock in portfolio_data["Stock_Data"]:
        if stock["stock-symbol"] == ticker[1]:
            new_quantity += float(stock["quantity"])
            stock_exists = True
            if new_quantity < 0:
                return "<br>No short selling allowed."
            elif new_quantity == 0:
                portfolio_data["Stock_Data"].remove(stock)
                break  # we break since we still need to save the updated portfolio change back to the file
            else:
                buy_price = float(price[1])
                add_quantity = float(quantity[1])
                old_price = float(stock["price"])
                old_quantity = float(stock["quantity"])

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

    # Save the portfolio data back to file
    with open("portfolio.json", "w") as f:
        json.dump(portfolio_data, f, indent=4)

    if new_quantity == 0:
        return f"<br>All available shares of {ticker[1]} sold."

    return "<br>Portfolio updated."
