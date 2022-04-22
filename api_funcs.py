from json import JSONDecodeError
import requests

api_symbols = "https://cloud.iexapis.com/stable/ref-data/symbols?filter=symbol,type&token=pk_95a04004620544349cd846204159cae9"
api_stock_quote = "https://cloud.iexapis.com/stable/stock/{0}/quote?token=pk_95a04004620544349cd846204159cae9"
api_batch_quote = "https://cloud.iexapis.com/stable/stock/market/batch?symbols={0}&types=quote&filter=latestPrice&token=pk_95a04004620544349cd846204159cae9"
api_stats_call = "https://cloud.iexapis.com/stable/stock/{0}/stats?token=pk_95a04004620544349cd846204159cae9"
api_chart_call = "https://sandbox.iexapis.com/stable/stock/{" \
                 "0}/chart/5y?chartCloseOnly=true&filter=date,close&token=Tpk_e5772b90e3cd48d2aa922e55682b5c5a"
list_of_symbols = []


def get_symbols_from_api():
    response = requests.get(api_symbols)
    if response.status_code == 200:
        list_of_symbols.extend([s['symbol'] for s in response.json() if s['type'] == 'cs'])
    else:
        print("Error getting symbols data from API.")


def get_current_price_from_api(stock) -> float:
    api_url = api_stock_quote.format(stock.upper())
    try:
        stock_data = requests.get(api_url).json()
        if "latestPrice" not in stock_data:
            raise ValueError("Latest price data doesn't exist.")
        return stock_data.get("latestPrice")
    except (KeyError, ValueError) as e:
        print(e, f" - does the stock {stock} exist?")
        return 0.00


def get_batch_current_prices(stocks):
    try:
        query = ','.join(map(lambda s: s.upper(), stocks))
        api_url = api_batch_quote.format(query)
        return requests.get(api_url).json()
    except (ValueError | JSONDecodeError):
        return []


def get_stock_data(query) -> object:
    try:
        stock_symbol = query.split("=")[-1]
        return requests.get(api_stats_call.format(stock_symbol.upper())).json()
    except JSONDecodeError:
        return "<br>Error loading stock research data."


def get_chart_data(stock) -> object:
    try:
        json_data = requests.get(api_chart_call.format(stock)).json()
        return json_data
    except JSONDecodeError:
        return None


def get_symbols():
    if not list_of_symbols:
        get_symbols_from_api()
    return list_of_symbols
