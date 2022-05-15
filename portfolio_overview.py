from questrade_helper import Portfolio

TFSA = Portfolio(account_type='TFSA')

print(TFSA.final_output.T)
