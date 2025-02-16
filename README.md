A portfolio rebalancing tools using Questrade API python wrapper.

Online tools are alright but it's lacking currency conversion as well as the access to near realtime price as well as how many shares should be bought/sold.
This makes rebalancing easier and more mechanical to execute; taking the emotions out of the process and aiding investing discipline.

Questrade API python wrapper: https://pypi.org/project/questrade-api/

# Usage

Set up your virtual environment, install the necessary libraries outlined in requirements.txt

After installing Questrade API, you'll need to log on to Questrade and register an authorized app and pull the refresh token. Using this token and initiate an questrade api client will automatically set up the API's info for you.

For this you'll need the app to have the access to query market prices not just accounts positions/balances.

Starting with `portfolio_helper.py`, define your target composition.

```
TARGET_COMPOSITION = ["Cash", "XYLD", "RYLD", "SVOL", "SPYC", "YMAG", "MAGS"]
TARGET_PERCENT = [0, 6, 6, 6, 24, 24, 34]
```

Then in `portfolio_overview.py` you can checkout how all input arguments and their usage's explainations.

```
$ python portfolio_overview.py 
Required at least one argument please see usage below
=====================================================
usage: portfolio_overview.py [-h] [-t ACCOUNT_TYPE] [-c CASH_INJECTION] [-e CASH_INJECTION_CAD] [-r REFRESH_TOKEN] [-s SYMBOL_SEARCH] [-n NO_CASH_MODE]

Retrieve a QT account by type then calculates the target composition delta and provide automatic balancing figures

options:
  -h, --help            show this help message and exit
  -t ACCOUNT_TYPE, --type ACCOUNT_TYPE
                        define account type
  -c CASH_INJECTION, --cash CASH_INJECTION
                        define the additional cash injection on top of what's available in the account
  -e CASH_INJECTION_CAD, --exchange CASH_INJECTION_CAD
                        define what the cash injection's currency is, true = CAD, false = USD
  -r REFRESH_TOKEN, --refresh-token REFRESH_TOKEN
                        refresh token for API
  -s SYMBOL_SEARCH, --symbol SYMBOL_SEARCH
                        symbol or ticker to perform a search
  -n NO_CASH_MODE, --no-cash-mode NO_CASH_MODE
                        the account is treated as if there's no cash in the account, a pure re-balance
```

If a stocks/etf is not already within the account, the code will automatically poll the stock's last traded price and do the necessary calculations.
The table will give you BUY/SELL decision (in USD and CAD) and how many shares to reach the target composition at near realtime price.

There's also a balance/composition check to make sure no input mistakes.

Balance check should be zero or near zero since the the amount of buying & selling has to equal.
Target composition has to be 100%.

Below is an example usage to balance a TFSA account. 

```
$ python portfolio_overview.py -r pKt6RGYGdi6ld5iM8sdBMxvwGzH7b0 -t TFSA
Retrieving account position
Clearing recently liquidated position
Retrieving acount's cash
Calculating...
Balance check (should be zero): 6.09
Target composition check (should be 100): 100.00
                        RYLD      SVOL      YMAG      XYLD      Cash      MAGS      SPYC
                    25565377  35984375  52704509  24215496 -1         47659830  32080031
openQuantity             255       201       886       100         1       436       448
averageEntryPrice      19.46     24.02     20.29     44.96    975.03     41.23     29.04
averagePrice           16.75     21.48     18.20     42.77    975.03     55.28     39.04
totalCost            4962.24   4828.91  17972.69   4496.13    975.03  17976.39  13012.04
currentMarketValue   4272.52   4316.48  16125.20   4277.50    975.03  24102.08  17489.92
openPnl              -689.71   -512.44  -1847.49   -218.63         0   6125.69   4477.88
%PnL                  -13.90    -10.61    -10.28     -4.86         0     34.08     34.41
%portfolio              5.97      6.03     22.53      5.98      1.36     33.68     24.44
%target_portfolio       6.00      6.00     24.00      6.00      0.00     34.00     24.00
balancer               21.36    -22.59   1050.36     16.39   -975.03    229.96   -314.36
balancer-CAD           30.57    -32.32   1502.85     23.45  -1395.07    329.03   -449.79
buy-sell                 BUY      SELL       BUY       BUY      SELL       BUY      SELL
shares-count            1.00     -2.00     57.00      0.00     -1.00      4.00     -9.00
Current exchange rate USD to CAD: 1.4308
```

You won't need to provide a fresh refresh token for every subsequent calls. However, the TTL for the token is 1800 seconds so not long. Passing this time without invoking the API again will throw an exception getting the accounts, i.e. it returned an error and an empty array. Thus, you'll need to provide a new refresh token. 

Cash injection:

For most of the investment's lifetime, there will regular cash deposit as part of the saving/investment/retirement plan. Two extra params have been added to aid this.

cash_injection: the amount of cash injected into the account

cash_injection_cad: specify whether the cash injected is dinominated in CAD or USD

Below is example of a cash injection usage where $50,000.00 CAD is added to the TFSA account.

```
$ python portfolio_overview.py -t FHSA -c 50000.00
Retrieving account position
Clearing recently liquidated position
Retrieving acount's cash
Calculating...
Balance check (should be zero): 0.99
Target composition check (should be 100): 100.00
                        YMAG      SVOL      Cash      RYLD      XYLD      SPYC      MAGS
                    52704509  35984375 -1         25565377  24215496  32080031  47659830
openQuantity             157        37         1        45        17        79        77
averageEntryPrice      19.88     21.99  35820.30     16.05     40.70     36.85     42.56
averagePrice           18.20     21.48  35820.30     16.75     42.77     39.04     55.28
totalCost            3120.92    813.76  35820.30    722.31    691.87   2911.54   3277.32
currentMarketValue   2857.40    794.58  35820.30    753.98    727.17   3084.16   4256.56
openPnl              -263.52    -19.18         0     31.67     35.30    172.62    979.24
%PnL                   -8.44     -2.36         0      4.38      5.10      5.93     29.88
%portfolio              5.92      1.65     74.17      1.56      1.51      6.39      8.81
%target_portfolio      24.00      6.00      0.00      6.00      6.00     24.00     34.00
balancer             8733.43   2103.13 -35820.30   2143.73   2170.53   8506.67  12163.79
balancer-CAD        12495.80   3009.16 -51251.68   3067.25   3105.60  12171.35  17403.95
buy-sell                 BUY       BUY      SELL       BUY       BUY       BUY       BUY
shares-count          479.00     97.00     -1.00    127.00     50.00    217.00    220.00
Current exchange rate USD to CAD: 1.4308
```
