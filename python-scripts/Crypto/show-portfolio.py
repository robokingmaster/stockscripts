import coinswitchapi
import json
import sys
from tabulate import tabulate
from decimal import * 

sys.set_int_max_str_digits(10002)

# colored text and background
def strRed(skk):         return "\033[91m {}\033[00m".format(skk)
def strGreen(skk):       return "\033[92m {}\033[00m".format(skk)
def strYellow(skk):      return "\033[93m {}\033[00m".format(skk)
def strLightPurple(skk): return "\033[94m {}\033[00m".format(skk)
def strPurple(skk):      return "\033[95m {}\033[00m".format(skk)
def strCyan(skk):        return "\033[96m {}\033[00m".format(skk)
def strLightGray(skk):   return "\033[97m {}\033[00m".format(skk)
def strBlack(skk):       return "\033[98m {}\033[00m".format(skk)
def strBold(skk):        return "\033[1m {}\033[0m".format(skk)

  
if __name__ == '__main__': 
    portfolio_data = coinswitchapi.getPortfolio()
    portfolio_json = json.loads(portfolio_data.text)
    # portfolio_json = sorted(portfolio_json, key=lambda k: k['data']['invested_value'], reverse=True)
    
    data_array = []
    data_array_header = ['NAME','CODE','UNITS','BUY-AVG-PRICE \u20B9','INVESTMENT-VALUE \u20B9','CURR-PRICE \u20B9','CURRENT-VALUE \u20B9','PROFIT-LOSS \u20B9','PROFIT-LOSS-%']
    for item in portfolio_json['data']: 
        profit_loss = Decimal(item["current_value"]) - Decimal(item["invested_value"]) 
        profit_loss_per = 100 - (Decimal(item["current_value"]) * 100)/Decimal(item["invested_value"])
        if(profit_loss > 0):
            profit_loss = strGreen(profit_loss)
            profit_loss_per = strGreen(profit_loss_per)
        else:
            profit_loss = strRed(profit_loss)
            profit_loss_per = strRed(profit_loss_per)
        
        row_data = [item["name"],
                    item["currency"],
                    item["main_balance"],
                    Decimal(item["buy_average_price"]),
                    Decimal(item["invested_value"]),
                    item["sell_rate"],
                    Decimal(item["current_value"]),
                    profit_loss,
                    profit_loss_per                  
                ]
                
        data_array.append(row_data)

    print(tabulate(data_array, headers=data_array_header, floatfmt=".2f"))