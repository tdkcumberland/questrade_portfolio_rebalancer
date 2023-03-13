from questrade_helper import Portfolio
from symbol_search import Symbol
import argparse

def main():
    parser = argparse.ArgumentParser(description="Retrieve a QT account by type then calculates the target composition delta and provide automatic balancing figures")
    parser.add_argument('-t', '--type', dest="account_type", type=str, help="define account type")
    parser.add_argument('-c', '--cash', dest="cash_injection", type=float, help="define the additional cash injection on top of what's available in the account", default=0.0 )
    parser.add_argument('-e', '--exchange', dest="cash_injection_cad", type=str2bool, help="define what the cash injection's currency is, true = CAD, false = USD", default=True )
    parser.add_argument('-r', '--refresh-token', dest='refresh_token', type=str, help="refresh token for API")
    parser.add_argument('-s', '--symbol', dest="symbol_search", type=str, help="symbol or ticker to perform a search")
    args = parser.parse_args()

    if args.account_type and not args.symbol_search:
        OUTPUT = Portfolio(account_type=args.account_type, cash_injection=args.cash_injection, cash_injection_cad=args.cash_injection_cad, refresh_token=args.refresh_token)
        print(OUTPUT.final_output.T)
        
        print("Current exchange rate USD to CAD: {:.4f}".format(OUTPUT.exchange_rate_USD_CAD))
    elif args.symbol_search and not args.account_type:
        Symbol(symbol = args.symbol_search, refresh_token = args.refresh_token)
    else:
        raise argparse.ArgumentError("Either an account type full portfolio overview or a symbol looking up is required")

def str2bool(value: str):
    if isinstance(value, bool):
        return value
    if value.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

if __name__=="__main__":
    main()