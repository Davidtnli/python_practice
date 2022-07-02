import selenium
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import time,random
from bs4 import BeautifulSoup as bs
import requests as re
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options

chrome_driver_path = "chromedriver.exe"

ua = UserAgent()
options = Options()
# options.add_argument('--headless')
# options.add_argument('user-agent=' + ua.chrome)
# driver = webdriver.Chrome(chrome_driver_path, options=options)
driver = webdriver.Chrome(chrome_driver_path)
driver.implicitly_wait(10)
url = "https://www.python.org/"
driver.get(url)
Q = "list"

keyword = driver.find_element_by_css_selector("#id-search-field")
#fakebox-input
keyword.clear()
time.sleep(random.uniform(2, 3))
keyword.send_keys(Q)
keyword.send_keys(Keys.ENTER)
time.sleep(3)

#google
# //*[@id="rso"]/div[1]/div[1]/div/div[1]/div/div[2]/div/div[1]/a/h3/span
# //div[@class='yuRUbf']/a/h3[@class='LC20lb MBeuO DKV0Md']
items_title = driver.find_elements_by_xpath('//*[@id="content"]/div/section/form/ul/li/h3/a')
items_content = driver.find_elements_by_xpath('//*[@id="content"]/div/section/form/ul/li/p')
python_search_list = []

for i in range(len(items_title)):
   python_search_list_dict = {}
   python_search_list_dict["title"] = items_title[i].text
   python_search_list_dict["content"] = items_content[i].text
   python_search_list.append(python_search_list_dict)

print(python_search_list)
driver.quit()
