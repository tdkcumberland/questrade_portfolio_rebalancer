from numpy import double, nan
from questrade_api.questrade import Questrade
import pandas as pd
from portfolio_helper import asset_class, target_composition, target_percent

class Portfolio():
    def __init__(self, account_type:str, refresh_token:str=None):
        self.questrade_client = Questrade(refresh_token = refresh_token) if refresh_token else Questrade()
        self.account = self.get_account(self.questrade_client.accounts,account_type)
        self.account_positions: pd.DataFrame = pd.DataFrame.from_dict(self.questrade_client.account_positions(self.account)['positions'])
        self.account_balances: pd.DataFrame = pd.DataFrame.from_dict(self.questrade_client.account_balances(self.account)['combinedBalances'])
        self.account_balances = self.account_balances.set_index('currency')
        self.exchange_rate_USD_CAD = self.account_balances.loc['CAD', 'totalEquity']/self.account_balances.loc['USD', 'totalEquity']
        self.cash_row = self.get_cash_as_account_row()
        self.account_calculations()
        self.over_allocation = self.get_overall_allocation()
        self.final_output = self.account_positions[['openQuantity', 'averageEntryPrice','averagePrice', 'totalCost','currentMarketValue','openPnl','%PnL','%portfolio','%target_portfolio', 'balancer', 'balancer-CAD', 'buy-sell', 'shares-count']]

        print("Balance check (should be zero): " + str(self.account_positions['balancer'].sum()))
        print("Target composition check (should be 100): " + str(self.account_positions['%target_portfolio'].sum()))

    def get_overall_allocation(self):
        _ = self.account_positions.groupby(['assetClass']).sum()
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
            # if the symbol is not in the curret positions, find it and add it the relevant info as row into the df
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
                self.account_positions = self.account_positions.append(row)
            else:
                self.account_positions.loc[target, '%target_portfolio'] = target_percent().get(target)

    def get_cash_as_account_row(self):
        return pd.Series({
                        'openQuantity': 1,
                        'openPnl': 0,
                        'totalCost': self.account_balances.loc['USD', 'cash'],
                        'currentMarketValue': self.account_balances.loc['USD', 'cash'],
                        'averageEntryPrice': self.account_balances.loc['USD', 'cash'],
                        'averagePrice': self.account_balances.loc['USD', 'cash'],
                        '%PnL': 0,
                        '%portfolio': 0,
                        'closedQuantity': 0,
                        'currentPrice': self.account_balances.loc['USD', 'cash'],
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
        self.account_positions = self.account_positions.append(self.cash_row)
        self.account_positions['assetClass'] = nan
        self.account_positions['%target_portfolio'] = nan
        self.account_positions['balancer'] = nan
        self.account_positions['buy-sell'] = ""
        self.account_positions['shares-count'] = nan

        self.assign_target_composition()

        self.account_positions['%portfolio'] = self.account_positions['currentMarketValue']/(self.account_balances.loc['USD', 'totalEquity'])*100
        self.balance_positions_based_on_target_comp()