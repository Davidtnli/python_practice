import selenium as slm
from bs4 import BeautifulSoup as bs
import requests as re
import lxml
from lxml import cssselect as cs
import json
from lxml import html


'''民報取即時新聞之EID'''

#https://www.peoplemedia.tw/resource/gallerylists/TOPRANKING?_=1649580278542
res = re.get("https://www.peoplemedia.tw/resource/lists/NEWS?filterselect=true&_=1649580278544")
realtime_json = res.json()
print(realtime_json.keys())
eid_list =[]
for i in realtime_json["data_list"]:
    eid_list.append(i["EID"])
print(eid_list)


'''鉅亨網即時頭條取tilte'''

res = re.get("https://api.cnyes.com/media/api/v1/newslist/category/headline?startAt=1648656000&endAt=1649606399&limit=30")
topnews_json = res.json()
print(topnews_json.keys())
title_list =[]
for i in topnews_json["items"]["data"]:
    title_list.append(i["title"])
title_list =[t["title"] for t in topnews_json["items"]["data"]]
print(title_list)


'''自由時報'''

res = re.get("https://news.ltn.com.tw/ajax/breakingnews/all/1")
topnews_json = res.json()
print(topnews_json.keys())
title_list =[]
# for i in topnews_json["items"]["data"]:
#     title_list.append(i["title"])
title_list =[t["title"] for t in topnews_json["data"]]
print(title_list)

#自由時報取第2頁以後不同關鍵字
Itn_outline_list = []
res = re.get(f'https://news.ltn.com.tw/ajax/breakingnews/all/3')
Itn_news_json = res.json()

for i in Itn_news_json["data"].keys():
   Itn_outline_list.append(Itn_news_json["data"][i]["title"])


Itn_news_outline = json.dumps(Itn_outline_list, ensure_ascii=False, indent=2)
# 輸出json檔可以有中文與換行

with open("Itn_news.json", "w", encoding='utf-8') as output:
  output.write(Itn_news_outline)


'''聯合報'''

res = re.get("https://udn.com/api/more?page=0&channelId=2&type=subcate_articles&cate_id=6638&sub_id=120940&totalRecNo=168&is_paywall=0&is_bauban=0&is_vision=0")
udn_news_json = res.json()
udn_outline_list =[]
for i in udn_news_json["lists"]:
udn_outline_list.append(i)
udn_news_outline = json.dumps(udn_outline_list, ensure_ascii=False, indent = 2)
# 輸出json檔可以有中文與換行
with open("udn_news.json", "w") as output:
   output.write(udn_news_outline)

'''蘋果日報'''
res = re.get("https://tw.appledaily.com/home/")
soup = bs(res.text, 'lxml')
tree = html.fromstring(res.text)    # 轉化成樹
# tree.getchildren()
# tree.xpath('//*[@id="main-container"]/div[2]/div/div/a')
lists1 = []
lists2 = []
for i, x in enumerate(tree.xpath('//div[2]/div[2]/span')):
   print(i, x.text)
   lists1.append(x.text)

for i, x in enumerate(tree.cssselect(".headline")):
   print(i, x.text)
   lists2.append(x.text)

uni_set1 = set(lists1)
uni_set2 = set(lists2)
uni_list1 = list(uni_set1)
uni_list2 = list(uni_set2)
#去除重複
for i, x in enumerate(uni_list1):
   print(i, x)

for i, x in enumerate(uni_list2):
   print(i, x)
   
   
'''中時新聞網'''

res = re.get("https://www.chinatimes.com/?chdtv")
soup = bs(res.text, 'lxml')
tree = html.fromstring(res.text)    # 轉化成樹
# tree.getchildren()
# tree.xpath('//*[@id="main-container"]/div[2]/div/div/a')
for i in tree.xpath('//*[@id="news-pane-1-1"]/section/ul/li/h4/a'):
   print(i.text)

for i in tree.cssselect("#news-pane-1-1 > section > ul > li > h4 > a"):
   print(i.text)
