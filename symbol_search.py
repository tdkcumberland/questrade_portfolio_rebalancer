from questrade_api.questrade import Questrade

q = Questrade()

symbol = "PFIX"

search_symbol = q.symbols_search(prefix = symbol, offset = 0)

if search_symbol['symbols']:
    symbol_search_result = q.markets_quote(search_symbol['symbols'][0]['symbolId'])
else:
    raise ValueError("The symbol " + symbol + " is not found!!!")
