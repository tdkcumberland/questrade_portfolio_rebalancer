from numpy import double

GOLD_CASH = ['Cash', 'BAR']
CRYPTO = ['BTC']
COMMODITY = ['DBC', 'JJE', 'JJM', 'JJA', 'COW', 'GRN', 'URA']
FIXED_INCOME = ['RYLD', 'QYLD', 'XYLD', 'SVOL']
EQUITY = ['SPYC', 'SCHH','FTEC','EBLU','XHB','FHLC','FSTA','FUTY','FIDU','FNCL','FMAT','FDIS','FENY','FCOM','CNRG']
LONG_VOL = ['PFIX', 'IVOL']

TARGET_COMPOSITION = ["Cash", "XYLD", "RYLD", "SVOL", "SPYC", 
                      "YMAG", "MAGS"]
TARGET_PERCENT = [0, 6, 6, 6, 24, 24, 34]

TARGET_PERCENT = dict(zip(TARGET_COMPOSITION,TARGET_PERCENT))

def asset_class() -> dict[str, str]:
    hm_dict = dict(zip(GOLD_CASH, ['GOLD_CASH']*len(GOLD_CASH)))
    comm_dict = dict(zip(COMMODITY, ['COMMODITY']*len(COMMODITY)))
    fi_dict = dict(zip(FIXED_INCOME, ['FIXED_INCOME']*len(FIXED_INCOME)))
    eq_dict = dict(zip(EQUITY, ['EQUITY']*len(EQUITY)))
    lv_dict = dict(zip(LONG_VOL, ['LONG_VOL']*len(LONG_VOL)))
    btc_dict = dict(zip(CRYPTO, ['CRYPTO']*len(CRYPTO)))
    library = hm_dict | comm_dict | fi_dict | eq_dict | lv_dict | btc_dict
    return library

def target_composition() -> list[str]:
    return TARGET_COMPOSITION

def target_percent() -> dict[str, double]:
    return TARGET_PERCENT