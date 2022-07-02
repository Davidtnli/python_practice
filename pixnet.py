import requests as re
import json
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import time, random, warnings
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud  #conda install -c conda-forge wordcloud
import jieba
import numpy as np
from collections import Counter
from datetime import datetime
from elasticsearch import Elasticsearch #pip install "elasticsearch<7.14"

#檢查多餘逗號
def check_com(str_):

    #檢查特殊錯誤
    if ',,,,,' in str_:
        pretext = ',,,,,'
        str_ = str_.replace(pretext, ',')
        return str_
    elif ',,' in str_:
        pretext = ',,'
        str_ = str_.replace(pretext, ',')
        return str_
    else:
        return

#爬取內文連結
def pix_cra(keyword, filename):

    with open(f'{filename}_raw.json', 'r', encoding="utf-8") as f:
        j = f.read()
    j = "[" + j + "]"
    for_check = json.loads(j)

    ua = UserAgent()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('user-agent=' + ua.chrome)
    driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)

    url = f"https://www.pixnet.net/tags/{keyword}"
    driver.get(url)
    temp_height = 0
    articles = []

    #無限滾動
    while True:

        driver.execute_script("window.scrollBy(0,1000)")

        driver.implicitly_wait(10)
        soup = bs(driver.page_source, 'lxml')
        datas = soup.select("section#anchor-article > section > div > h3 > a")
        t = soup.select("section#anchor-article > section > header > div > p")

        for i, j in zip(t, datas):
            content = {}
            content['title'] = j.string.strip()
            content['date'] = i.text
            content['url'] = j.get("href")
            content['content'] = ""
            articles.append(content)
        time.sleep(random.uniform(1, 5))

        #檢查是否為最新文章
        if articles[0]['title'] == for_check[0]['title']:
            articles = []
            break

        check_height = driver.execute_script("return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")

        if check_height == temp_height:
            break
        temp_height = check_height
    driver.quit()
    if articles == []:
        print('無新資料')
        return None

    tmp = json.dumps(articles, ensure_ascii=False, indent=1)
    result = tmp.strip('[]')
    with open(f'{filename}_raw.json', 'a', encoding="utf-8") as f:
        f.write(result + ',')

#利用pandas去除重複
def drop_depl(filename):

    #先改成可讀的json檔
    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read().strip(',')
    j = "[" + j + "]"
    j = check_com(j)

    data = json.loads(j)
    df = pd.DataFrame(data)
    # 去除重複
    df = (df[(df[['title', 'date', 'url']].duplicated()) == False])
    output_ = filename.replace('raw', 'drop_depl')
    with open(output_, 'w', encoding="utf-8") as f:
        result = df.to_json(orient='records', force_ascii=False, indent=2)
        f.write(result)

#取得文章內文
def pix_get_arti(filename):

    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read()
    raw = json.loads(j)

    err_url = []
    for i in range(len(raw)):
        url = raw[i]['url']
        ua = UserAgent()
        headers = {'user-agent': str(ua.random)}
        time.sleep(20)

        #測試是否有失效的連結，並另外儲存

        try:
            res = re.get(url, headers=headers)
            res.encoding = 'utf-8'
            soup = bs(res.text, 'lxml')
            contents = soup.find_all("div", class_='article-content-inner')
            content = contents[0].getText().strip('').replace('\n', '')
            raw[i]['content'] = content

        except:
            print(f'第{i + 1}筆資料無法讀取')
            content = {}
            content['title'] = raw[i]['title']
            content['url'] = url
            err_url.append(content)
            raw[i]['content'] = ""

    output1 = filename.replace('drop_depl', 'result')
    tmp1 = json.dumps(raw, ensure_ascii=False, indent=1)
    result1 = tmp1.strip('[]')
    with open(output1, 'w', encoding="utf-8") as f:
        f.write(result1)

    output2 = filename.replace('drop_depl', 'error_urls')
    tmp2 = json.dumps(err_url, ensure_ascii=False, indent=1)
    result2 = tmp2.strip('[]')
    with open(output2, 'w', encoding="utf-8") as f:
        f.write(result2)

#將時間格式改成有利於ELK之ISO格式
def change_time_type(filename):

    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read()
        j = "[" + j + "]"
    dict = json.loads(j)

    for i in dict:
        if "年" not in i['date']:
            i['date'] = "2022年" + i['date']
        i['date'] = i['date'].replace('年', "-")
        i['date'] = i['date'].replace('月', "-")
        i['date'] = i['date'].replace('日', "")
        i['date'] = datetime.strptime(i['date'], "%Y-%m-%d %H:%M").isoformat()

    output_ = filename.replace('result','final')
    tmp = json.dumps(dict, ensure_ascii=False, indent=1)
    result = tmp.strip('[]')
    with open(output_, 'w', encoding="utf-8") as f:
        f.write(result)

#將json轉為csv
def change_data_to_csv(filename):

    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read().strip(',')
    j = "[" + j + "]"

    data = json.loads(j)
    df = pd.DataFrame(data)
    output_ = filename.replace('.json', '.csv')
    df.to_csv(output_, encoding='utf_8_sig', index=False)  #使用utf-8會亂碼，改成utf_8_sig即可

#創建文字雲
def wordcloud_result(filename, picture):

    #將所有內文整理成一個字串
    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read()
        j = "[" + j + "]"
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

#進入ELK
def to_elk(filename, index, ip):

    hosts = f"http://{ip}:9200/"

    es = Elasticsearch(hosts=hosts)

    with open(filename, 'r', encoding="utf-8") as f:
        j = f.read()
        j = "[" + j + "]"
    data = json.loads(j)
    li_bulk = []
    for row_dict in data:
        li_bulk.append({"index": {"_index": index}})
        li_bulk.append(row_dict)
    es.bulk(body=li_bulk)