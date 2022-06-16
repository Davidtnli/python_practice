import requests as re
import json
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time, random, warnings
from fake_useragent import UserAgent                       # pip install fake_useragent
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager   # pip install webdriver_manager
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud  # conda install -c conda-forge wordcloud
import jieba                     # pip install jieba
import numpy as np
from collections import Counter
from datetime import datetime
from elasticsearch import Elasticsearch    # pip install "elasticsearch<7.14"
import mysql.connector                     # pip install mysql.connector


#利用request爬取google map 輸入統整好的txt檔
def google_spider(filename):

    output_ = filename.replace('.txt', '_{}.json')   #將檔名修改以便輸出

    with open(filename, 'r') as f:                   #開啟統整好的連結txt檔
        urls = f.read().split('\n')

    count = 1
    for url in urls:

        print('正在爬取第{}家分店'.format(count))

        #準備檢查最新資料的檔案，若是第一次爬取則創一個測試用的，以便程式不報錯最後會刪掉
        try:
            with open(output_.format(count), 'r', encoding="utf-8") as f:
                j = f.read()
            j = "[" + j + "]"
            wrong_text = '}\n\n {'
            if wrong_text in j:
                j = j.replace(wrong_text, '}\n,\n {')
            for_check = json.loads(j)
        except:
            for_check = [{'name':'test','time':'1990-01-01'}]

        page = 0
        all_content = []
        pretext = ')]}\''

        #利用無窮迴圈爬取資料

        status = 1
        while (status == 1):
            ua = UserAgent()
            headers = {'user-agent': str(ua.random)}
            time.sleep(random.randint(5, 10))
            res = re.get(url.format(page), headers=headers)
            text = res.text.replace(pretext, '')
            soup = json.loads(text)
            conlist = soup[2]
            print(f'正在爬取第{page + 1}到第{page + 10}筆評論')

            #如果沒有資料會報錯，所以用try來控制，無資料則跳出迴圈
            try:
                for i in conlist:
                    a = {}
                    a['name'] = i[0][1]
                    timeStamp = int(i[27])/1000
                    a['time'] = datetime.utcfromtimestamp(timeStamp).isoformat()
                    if a['name'] == for_check[0]['name'] and a['time'] == for_check[0]['time']:     #檢查最新資料
                        status = 0
                        print(f'第{count}家分店無新評論')
                        break
                    if a['time'][:4] == '2020':                                                     #只取2021到現在的資料
                        status = 0
                        break
                    a['content'] = str(i[3]).strip('')
                    a['star'] = i[4]
                    all_content.append(a)
            except TypeError:
                status = 0

            page += 10
            time.sleep(random.randint(1,3))

        #若無新資料則跑下一個連結
        if all_content == []:
            count += 1
            continue
        else:
            final = json.dumps(all_content, ensure_ascii=False, indent=1).strip('[]')
            if for_check[0]['name'] == 'test':
                for_check = []
            tmp = json.dumps(for_check, ensure_ascii=False, indent=1).strip('[]')
            final = final + tmp
            with open(output_.format(count), 'w', encoding="utf-8") as f:
                f.write(final)

            count += 1


#將所有分店資料整理為同一json，輸入檔案名跟數量 ex: ('Thaitown_google',62) 不需要後面的數字
def merge_all_branch(filename, amount):

    tmp = ""
    for i in range(amount):
        with open(filename + '_{}.json'.format(i + 1), 'r', encoding="utf-8") as f:
            j = f.read()
            tmp += j + ','
    tmp = tmp.strip(',')

    with open(filename + '_final.json', 'w', encoding="utf-8") as f:
        f.write(tmp)

def wordcloud_result(filename, picture):

    #將所有內文整理成一個字串
    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read()
        j = "[" + j + "]"
    wrong_text = '}\n\n {'
    if wrong_text in j:
        j = j.replace(wrong_text, '}\n,\n {')
    data = json.loads(j)
    content_arr = []
    for i in data:
        content_arr.append(i['content'].replace(" ", ""))
    content = "".join(content_arr)

    #創建文字雲
    with open('stopword.txt', 'r', encoding='utf-8') as f:  # 設定停用詞
        stops = f.read().split('\n')
    jieba.set_dictionary('dict.txt.big.txt')
    terms = []  # 儲存字詞
    for t in jieba.cut(content, cut_all=False):  # 拆解句子為字詞
        if t not in stops:  # 不是停用詞
            terms.append(t)
    diction = Counter(terms)

    font = "c:\\WINDOWS\\FONTS\\kaiu.ttf"  # 設定字型(標楷)
    mask = np.array(Image.open(picture))  # 設定文字雲形狀
    wordcloud = WordCloud(background_color="white", mask=mask, font_path=font)  # 背景顏色預設黑色,改為白色
    wordcloud.generate_from_frequencies(frequencies=diction)  # 產生文字雲

    plt.figure(figsize=(6, 6))
    plt.imshow(wordcloud)
    plt.axis("off")

    output_ = filename.replace('final.json', 'wordcloud.png')
    wordcloud.to_file(output_)


#以三星為準，區分好壞聲量
def divide_by_star(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read()
        j = "[" + j + "]"
    wrong_text = '}\n\n {'
    if wrong_text in j:
        j = j.replace(wrong_text, '}\n,\n {')

    data = json.loads(j)
    good = []
    bad = []
    for i in data:
        if int(i['star']) <= 3:
            bad.append(i)
        else:
            good.append(i)

    tmp1 = json.dumps(good, ensure_ascii=False, indent=1)
    result1 = tmp1.strip('[]')
    output1 = filename.replace('final', 'good_final')
    with open(output1, 'w', encoding="utf-8") as f:
        f.write(result1)

    tmp2 = json.dumps(bad, ensure_ascii=False, indent=1)
    result2 = tmp2.strip('[]')
    output2 = filename.replace('final', 'bad_final')
    with open(output2, 'w', encoding="utf-8") as f:
        f.write(result2)


#連接 SQL
def db_init():
    mydb = mysql.connector.connect(
        host="resanalyze.onthewifi.com",
        port=3306,
        user="alldatainhere",
        password="SiDs5hPRSC/Vq[W1",
        database='MYDB',
        charset='utf8mb4'
    )
    cursor = mydb.cursor()
    return mydb, cursor

#寫入 SQL
def write_into_sql(group_ ,brand_, filename):

    mydb, cursor = db_init()
    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read()
        j = "[" + j + "]"
    wrong_text = '}\n\n {'
    if wrong_text in j:
        j = j.replace(wrong_text, '}\n,\n {')
    data = json.loads(j)


    cursor.execute(f"CREATE TABLE IF NOT EXISTS `{brand_}` (`id` INT AUTO_INCREMENT PRIMARY KEY,`date` DATE,`content` VARCHAR(10000),`brand` VARCHAR(50),`src` VARCHAR(50));")
    cursor.execute(f'ALTER TABLE `{brand_}` CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
    count = 1
    for i in data:
        print(f"正在匯入{brand_}的第{count}筆資料")
        sql = f"INSERT INTO {brand_} (`date`, `content`, `brand`,`src`) VALUES (%s,%s,%s,%s)"
        list_ = [i['time'], i['content'], group_, 'google']
        cursor.execute(sql, list_)
        count += 1
    mydb.commit()

def change_data_to_csv(filename):

    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read()
        j = "[" + j + "]"
    wrong_text = '}\n\n {'
    if wrong_text in j:
        j = j.replace(wrong_text, '}\n,\n {')
    data = json.loads(j)
    for i in data:
        i['time'] = i['time'][:10].replace('-', '/')

    df = pd.DataFrame(data)
    output_ = filename.replace('.json', '.csv')
    df.to_csv(output_, encoding='utf_8_sig', index=False)