from questrade_helper import Portfolio

OUTPUT = Portfolio(account_type='TFSA', cash_injection=4000.00, cash_injection_cad=True)

print(OUTPUT.final_output.T)
