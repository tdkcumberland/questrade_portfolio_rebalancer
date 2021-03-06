A portfolio rebalancing tools using Questrade API python wrapper.

Online tools are alright but it's lacking currency conversion as well as the access to near realtime price as well as how many shares should be bought/sold.
This makes rebalancing easier and more mechanical to execute; taking the emotions out of the process and aiding investing discipline.

Questrade API python wrapper: https://pypi.org/project/questrade-api/

# Usage
After installing Questrade API, you'll need to log on to Questrade and register an authorized app and pull the refresh token. Using this token and initiate an instant of questrade api client will automatically set up the API's info for you.

For this you'll need the app to have the access to query market prices not jsut accounts positions/balances.

```
from questrade_api.questrade import Questrade
refresh_token = "your-refresh-token"
q = Questrade(refresh_token = refresh_token)
```


Starting with `portfolio_helper.py`, define your target composition. Here, I am attempting to build Chris Cole's Dragon Portfolio (https://www.artemiscm.com/artemis-dragon).

If curious you can see the performance here: (https://app.composer.trade/symphony/ny7Aa66MTBwleruPIvqZ)

```
TARGET_COMPOSITION = ["Cash","DBC", "BAR", "IVOL", "PFIX", "XYLD", "RYLD", "SVOL", "SPYC", "RTYD"]
TARGET_PERCENT = [0, 18, 19, 10.5, 10.5, 6, 6, 6, 12, 12]
```

Then in `portfolio_overview.py`  provide the account type you want to review and balance.
You can also get a full list of your current accounts with `q.accounts()`

```
from questrade_helper import Portfolio

TFSA = Portfolio(account_type='TFSA')

# print and transpose the output matrix
print(TFSA.final_output.T)
```

Below is an example correspond to my defined composition. If a stocks/etf is not already within the account, the code will automatically poll the stock's last traded price and do the necessary calculations.
The table will give you BUY/SELL decision (in USD and CAD) and how many shares to reach the target composition at near realtime price.

There's also a balance/composition check to make sure no input mistakes.

Balance check should be zero since the the amount of buying & selling has to equal.
Target composition has to be 100%.

![SPEM](https://github.com/tdkcumberland/questrade_portfolio_rebalancer/blob/main/Example.PNG)


Cash injection:

For most of the investment's lifetime, there will regular cash deposit as part of the saving/investment/retirement plan. Two extra params have been added to aid this.

cash_injection: the amount of cash injected into the account

cash_injection_cad: specify whether the cash injected is dinominated in CAD or USD

```
from questrade_helper import Portfolio

OUTPUT = Portfolio(account_type='RRSP', cash_injection=0.00, cash_injection_cad=True)

print(OUTPUT.final_output.T)
```
