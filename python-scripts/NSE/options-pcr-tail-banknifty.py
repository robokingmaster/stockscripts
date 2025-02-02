# Libraries
from nselib import *
from tabulate import tabulate
import os

expiry_date = "28-Sep-2023"
strike_price = 20150
trail_time_min = 5

# Valiable To Hold Data
strikeprice_pcrdata = []

def print_strikeprice_pcr(strike_price):
    set_header(url_indices)
    try:
        while True: 
            os.system('cls') 
            
            print('\033c')    
            print_hr()
            print(strPurple(' Nifty Trailing PCR Value For Strike Price =>').ljust(12," "), strike_price, strLightPurple(" Expiry Date: ") + strBold(expiry_date), strLightPurple(" Refresh Time (Min): ") + strBold(trail_time_min) )        
            print_hr()
                        
            strikeprice_pcrdata.append(get_strikeprice_pcr(strike_price,url_bnf,expiry_date))  
            print(tabulate(strikeprice_pcrdata, headers=data_array_header))
            time.sleep(trail_time_min*60)
    except KeyboardInterrupt:
        print("Press Ctrl-C to terminate!!")
        pass
    

if __name__ == '__main__': 
    print_strikeprice_pcr(strike_price,)
