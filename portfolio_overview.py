from questrade_helper import Portfolio

OUTPUT = Portfolio(account_type='RRSP', cash_injection=0.00, cash_injection_cad=True)

print(OUTPUT.final_output.T)
