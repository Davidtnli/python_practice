import selenium as slm
from bs4 import BeautifulSoup as bs
import requests as re
import lxml
import cssselect as cs
import json

res = re.get("https://tw.stock.yahoo.com/rank/volume?exchange=TAI")
soup = bs(res.text, 'lxml')
stock_names = soup.find_all("div", "Lh(20px) Fw(600) Fz(16px) Ell")
stock_urls = soup.find_all("a", "Pos(a) W(100%) H(100%) T(0) Start(0) Z(0)")
stock_num = soup.find_all("span", 'Fz(14px) C(#979ba7) Ell')
stock_list = []


for i in range(len(stock_names)):
   try:
       stock_dict = {}
       stock_dict['stockName'] = stock_num[i].text.strip() + " " + stock_names[i].text.strip()      # .strip捨去多餘的空白、換行等
       stock_dict['url'] = stock_urls[i].get("href")
       stock_list.append(stock_dict)
   except:
       continue

print(stock_list)
