from questrade_api.questrade import Questrade

import pandas as pd

symbol = "PFIX"

class Symbol():
    def __init__(self, symbol: str, refresh_token: None) -> None:
        self.questrade_client = Questrade(refresh_token = refresh_token) if refresh_token else Questrade()
        self.search(symbol=symbol)

    def search(self, symbol: str):

        self.search_symbol = self.questrade_client.symbols_search(prefix = symbol, offset = 0)

        if self.search_symbol['symbols']:
            self.symbol_search_result = self.questrade_client.markets_quote(self.search_symbol['symbols'][0]['symbolId'])
            print(self.symbol_search_result['quotes'][0])
            df = pd.DataFrame(self.symbol_search_result['quotes'][0], index = ['symbol'])
            print(df.T)
        else:
            raise ValueError("The symbol " + symbol + " is not found!!!")