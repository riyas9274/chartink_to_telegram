import requests
import pandas as pd
from bs4 import BeautifulSoup

# ====== CHARTINK Configuration =======
Charting_Link = "https://chartink.com/screener/"
Charting_url = 'https://chartink.com/screener/process'

Condition = "( {cash} ( latest close = latest high and latest close > latest open and latest close > 1 day ago close and latest volume > latest sma ( volume, 26 ) ) ) "

def GetDataFromChartink(payload):
    payload = {'scan_clause': payload}
    
    with requests.Session() as s:
        r = s.get(Charting_Link)
        soup = BeautifulSoup(r.text, "html.parser")
        csrf = soup.select_one("[name='csrf-token']")['content']
        s.headers['x-csrf-token'] = csrf
        r = s.post(Charting_url, data=payload)

        df = pd.DataFrame()
        for item in r.json()['data']:
            df = pd.concat([df, pd.DataFrame([item], index=[0])], ignore_index=True)
    return df

# ====== FETCH DATA =======
print("Fetching data from Chartink...")
data = GetDataFromChartink(Condition)

# ====== SAVE EXCEL =======
excel_path = "chartink_output.xlsx"
if not data.empty:
    data.to_excel(excel_path, index=False)
    print("Excel file saved.")
else:
    print("No data to save.")

# ====== SEND TO TELEGRAM =======
bot_token = "7257895245:AAFSp_G4-3y_TcatCMCO61ZVMTLAdu0BX8M"
chat_id = "-1002526959615"

if not data.empty:
    with open(excel_path, "rb") as file:
        telegram_response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendDocument",
            data={"chat_id": chat_id},
            files={"document": file}
        )
    if telegram_response.status_code == 200:
        print("Sent to Telegram ✅")
    else:
        print("Telegram send failed:", telegram_response.text)

