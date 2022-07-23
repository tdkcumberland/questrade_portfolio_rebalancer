from questrade_helper import Portfolio
import argparse

def main():
    parser = argparse.ArgumentParser(description="Retrieve a QT account by type then calculates the target composition delta and provide automatic balancing figures")
    parser.add_argument('-t', '--type', dest="account_type", type=str, help="define account type")
    parser.add_argument('-c', '--cash', dest="cash_injection", type=float, help="define the additional cash injection on top of what's available in the account", default=0.0 )
    parser.add_argument('-r', '--refresh-token', dest='refresh_token', type=str, help="refresh token for API")
    args = parser.parse_args()

    OUTPUT = Portfolio(account_type=args.account_type, cash_injection=args.cash_injection, cash_injection_cad=True, refresh_token=args.refresh_token)
    print(OUTPUT.final_output.T)

if __name__=="__main__":
    main()