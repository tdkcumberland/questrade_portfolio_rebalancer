from numpy import double, nan
from questrade_api.questrade import Questrade
import pandas as pd
from portfolio_helper import asset_class, target_composition, target_percent

class Portfolio():
    def __init__(
        self, 
        account_type:str, 
        cash_injection: float=0., 
        cash_injection_cad: bool=False, 
        refresh_token:str=None,
        no_cash_mode:bool=False
        ):

        pd.set_option('display.float_format', '{:.2f}'.format)
        print("Retrieving account position")
        self.questrade_client = Questrade(refresh_token = refresh_token) if refresh_token else Questrade()
        self.no_cash_mode=no_cash_mode
        self.account = self.get_account(self.questrade_client.accounts,account_type)
        self.account_positions: pd.DataFrame = pd.DataFrame.from_dict(self.questrade_client.account_positions(self.account)['positions'])
        self.account_balances: pd.DataFrame = pd.DataFrame.from_dict(self.questrade_client.account_balances(self.account)['combinedBalances'])
        print("Clearing recently liquidated position")
        self.clear_recently_liquidated_position()
        self.account_balances = self.account_balances.set_index('currency')
        self.exchange_rate_USD_CAD = self.account_balances.loc['CAD', 'totalEquity']/self.account_balances.loc['USD', 'totalEquity']
        print("Retrieving acount's cash")
        self.cash_row = self.get_cash_as_account_row(cash_injection=cash_injection, cash_injection_cad=cash_injection_cad)
        print("Calculating...")
        self.account_calculations()
        self.over_allocation = self.get_overall_allocation()
        self.final_output = self.account_positions[['openQuantity', 'averageEntryPrice','averagePrice', 'totalCost','currentMarketValue','openPnl','%PnL','%portfolio','%target_portfolio', 'balancer', 'balancer-CAD', 'buy-sell', 'shares-count']]
        self.final_output = self.final_output.sort_values('%PnL', ascending=True)
        print("Balance check (should be zero): {:.2f}".format(self.account_positions['balancer'].sum()))
        print("Target composition check (should be 100): {:.2f}".format(self.account_positions['%target_portfolio'].sum()))

    def clear_recently_liquidated_position(self):
        # recently liquidated position has NaN in the dataframe which can cause errors during downstream calculation
        # filter out rows with zero open quantity > 0
        self.account_positions = self.account_positions.loc[
            (self.account_positions['openQuantity'] > 0) & 
            (self.account_positions['totalCost'].notnull())
            ]

    def get_overall_allocation(self):
        _ = self.account_positions.groupby(['assetClass']).sum(numeric_only=False)
        _['%PnL'] = _['openPnl']/_['totalCost']*100
        return _

    def search_for_last_trade_price_by_symbol(self, symbol:str):
        _ = self.questrade_client.symbols_search(prefix = symbol, offset = 0)
        if _['symbols']:
            symbol_search_result = self.questrade_client.markets_quote(_['symbols'][0]['symbolId'])
            return (_['symbols'][0]['symbolId'], symbol_search_result['quotes'][0]['lastTradePrice'])
        else:
            raise ValueError("The symbol " + symbol + " is not found!!!")

    def balance_positions_based_on_target_comp(self):
        for index, _ in self.account_positions.iterrows():
            self.account_positions.loc[index, 'assetClass'] = asset_class().get(index[0])
            self.account_positions.loc[index, 'balancer'] = self.account_balances.loc['USD', 'totalEquity']*self.account_positions.loc[index, '%target_portfolio']/100 - self.account_positions.loc[index, 'currentMarketValue']
            self.account_positions.loc[index, 'buy-sell'] = "BUY" if self.account_positions.loc[index, 'balancer'] >= 0 else "SELL"
            self.account_positions.loc[index, 'shares-count'] = divmod(self.account_positions.loc[index, 'balancer'], self.account_positions.loc[index, 'averagePrice'])[0] if self.account_positions.loc[index, 'averagePrice'] >0 else 0
            
        #convert the amount to balance to CAD
        self.account_positions['balancer-CAD'] = self.account_positions['balancer']*self.exchange_rate_USD_CAD

    def get_account(self, accounts : dict,  type : str) -> str:
        for acct in accounts['accounts']:
            if acct['type'] == type:
                return acct['number']

    def get_quote_by_symbol(self, symbol: str):
        return self.questrade_client.symbols_search(prefix = symbol, offset = 0)
    
    def assign_target_composition(self):
        current_composition = []
        for symbol, _ in self.account_positions.index:
            current_composition.append(symbol)
        
        for target in target_composition():
            # if the symbol is not in the current positions, find it and add it the relevant info as row into the df
            if target not in current_composition:
                target_id, target_last_trade_price = self.search_for_last_trade_price_by_symbol(symbol= target)
                row = pd.Series({
                                'openQuantity': 0,
                                'openPnl': 0,
                                'totalCost': 0,
                                'currentMarketValue': 0,
                                'averageEntryPrice': 0,
                                'averagePrice': target_last_trade_price,
                                '%PnL': 0,
                                '%portfolio': 0,
                                'closedQuantity': 0,
                                'currentPrice': target_last_trade_price,
                                'assetClass': '',
                                '%target_portfolio': target_percent().get(target),
                                'balancer': 0,
                                'buy-sell': '',
                                'shares-count': 0,
                                'balancer-CAD': 0,
                                },name=(target,target_id))
                self.account_positions = self.account_positions._append(row)
            else:
                self.account_positions.loc[target, '%target_portfolio'] = target_percent().get(target)

    def get_cash_as_account_row(self, cash_injection:float=0., cash_injection_cad:bool=False):
        if self.no_cash_mode:
            self.cash_value = 0
            self.account_balances.loc['USD', 'totalEquity'] = self.account_balances.loc['USD', 'totalEquity'] - self.account_balances.loc['USD', 'cash']
        elif cash_injection != 0:
            cash_injection_in_USD = cash_injection if not cash_injection_cad else cash_injection/self.exchange_rate_USD_CAD
            self.cash_value = cash_injection_in_USD + self.account_balances.loc['USD', 'cash']
            self.account_balances.loc['USD', 'totalEquity'] = self.account_balances.loc['USD', 'totalEquity'] + cash_injection_in_USD
        else:
            self.cash_value = self.account_balances.loc['USD', 'cash']
        return pd.Series({
                        'openQuantity': 1,
                        'openPnl': 0,
                        'totalCost': self.cash_value,
                        'currentMarketValue': self.cash_value,
                        'averageEntryPrice': self.cash_value,
                        'averagePrice': self.cash_value,
                        '%PnL': 0,
                        '%portfolio': 0,
                        'closedQuantity': 0,
                        'currentPrice': self.cash_value,
                        'assetClass': '',
                        '%target_portfolio': 0,
                        'balancer': 0,
                        'buy-sell': '',
                        'shares-count': 0,
                        'balancer-CAD': 0,
                        },name=('Cash',-1))

    def account_calculations(self):
        self.account_positions = self.account_positions.groupby(['symbol','symbolId'])[['openQuantity','openPnl','totalCost','currentMarketValue']].sum()
        self.account_positions['averageEntryPrice'] = self.account_positions['totalCost']/self.account_positions['openQuantity']
        self.account_positions['averagePrice'] = self.account_positions['currentMarketValue']/self.account_positions['openQuantity']
        self.account_positions['%PnL'] = (self.account_positions['currentMarketValue'] - self.account_positions['totalCost'])/self.account_positions['totalCost']*100
        
        self.account_positions = self.account_positions.sort_values(by='openPnl', ascending=False)
        
        # append cash row and a bunch more empty columns
        cash_flow_df = pd.DataFrame(self.cash_row)
        self.account_positions = pd.concat([self.account_positions, cash_flow_df.T])
        self.account_positions['assetClass'] = nan
        self.account_positions['%target_portfolio'] = nan
        self.account_positions['balancer'] = nan
        self.account_positions['buy-sell'] = ""
        self.account_positions['shares-count'] = nan

        self.assign_target_composition()

        self.account_positions['%portfolio'] = self.account_positions['currentMarketValue']/(self.account_balances.loc['USD', 'totalEquity'])*100
        self.balance_positions_based_on_target_comp()