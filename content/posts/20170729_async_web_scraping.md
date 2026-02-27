---
title: 多執行緒搭配非同步技術網頁爬取
date: '2017-08-22T11:58:13+00:00'
draft: false
categories:
- Web Scraping
summary: '概述 在開始看這篇文章之前，非常建議大家先熟悉個別的技術: 非同步技術以及多執行緒網頁爬取技術。以下，我想針對「他們的差別」以及在「多執行緒的技術理解焦點」兩個部分進行簡單的說明。
  more 首先，關注到他們的差別。所謂的非同步技術，指得是我們每發出一個requests都要等待server端的回應，而非同步技術可以充分利用這個等待時間，同時再發出其他requests，直到server成功回應時，才...'
cover:
  image: /images/posts/20170729_async_web_scraping/c501fafe-bb59-4904-854a-f8623d4f9e09.png
---

# 概述

在開始看這篇文章之前，非常建議大家先熟悉個別的技術: [非同步技術](https://goatwang.github.io/2017/07/29/%E9%9D%9E%E5%90%8C%E6%AD%A5%E7%9A%84%E7%B6%B2%E9%A0%81%E7%88%AC%E5%8F%96%E6%8A%80%E8%A1%93/)以及[多執行緒網頁爬取技術](http://blog.thepythontutor.com/2017/07/multithreading-web-scraping-with-python.html?m=1)。以下，我想針對「他們的差別」以及在「多執行緒的技術理解焦點」兩個部分進行簡單的說明。 more

首先，關注到他們的差別。所謂的非同步技術，指得是我們每發出一個requests都要等待server端的回應，而非同步技術可以充分利用這個等待時間，同時再發出其他requests，直到server成功回應時，才開始用同一個執行緒出處理回應回來的資料。必須注意的是，他並不會占用到多的CPU核心數，只是充分利用在同一個核心上的運算量而已。承接著，上面這段解釋，大家應該很好想像，多執行緒在做的實情，無非就是，使用多個CPU核心去處理事情，這邊要比較注意的是，假設你的CPU核心不夠，硬是將執行緒的數量開的比核心數多，將可能會被強制終止某些執行緒。

再來，必須關注到「多執行緒的技術理解焦點」，如果還沒碰過這個技術，大家可以看完這一段落之後再開始學習多執行緒，相信會大有幫助。我想大家在理解這個技術的時候，可以先建一個手動的多執行緒，也就是把一個要跑回圈的data list，拆成三段或四段，在不同的terminal針對每一段data list執行同一支的程式。在這過程中，你會關注到一些麻煩，像是要怎麼裁切data list、或者裁切了之後會不會有些執行緒很快執行完，有些執行緒則處理很久。

因此，在面臨到這些狀況時，python內建了一個非常方便的類別queue，這個queue跟list很像，除了使用上有一些小差異之外(list的append、queue用put，list的讀取一般用for迴圈，queue則直接使用get配上while迴圈)。其中最大的差別在，list使用for迴圈可以被重複使用， 但是queue中的data只要get出來之後，就會從queue裡面消失。而也正是因為這個特性，上多執行緒在取出queue的data的時候，完全不用煩惱前一個執行緒執行到哪，也不需要等待執行完才能執行下一個data，只要持續地從queue取出要處理的data即可，直到取完最後一個queue中的data。如此來上述問題也就被解決了。

# 專案

* 說明: 這個專案中的每一個執行緒，將先上Bing檢索一間公司的公司名稱，然後透過非同步技術對Bing回應的第一頁的所有連結送出requests，並將美個網頁中的純文字取出，最後將所頁面的純文字寫入同一份純文字檔案。
    
* 原始碼專案: [Github Repository](https://github.com/GoatWang/MultiAsyncCrawler)
    
* 建議: 使用虛擬環境，在clone下整個專案之後，在專案的資料夾目錄中打開terminal，執行以下指令
    

```bash
pip install virtualenv
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
python MultiAsync.py
```

# 主要程式碼

```bash
import aiohttp
import asyncio
import async_timeout

import queue
import threading

from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

import string
import json
import os


## 1. Build Queue
input_companies = queue.Queue()
fail_log = queue.Queue()

## 2. Search query list
companies = [
        "Agilysys, Inc.",
        "ASEC International Corporation",
        "Beijing Oriental Jicheng Co Ltd",
        "Chander Electronics Corp.",
        "Dragon Group International Limited",
        "Euro Tech Holdings Company Ltd",
        "Howteh Technology Co., Ltd.",
        "Kyokuto Boeki Kaisha, Ltd.",
        "Leeport (Holdings) Limited",
        "Makus, Inc.",
        "MEIJI ELECTRIC INDUSTRIES CO., LTD.",
        "Naito & Co Ltd",
        "OSAKA KOHKI CO LTD",
        "Premier Farnell plc",
        "Rexel SA",
        "Solomon Technology Corporation",
        "TAKACHIHO KOHEKI CO., LTD.",
        "TOMITA CO., LTD.",
        "Uematsu Shokai Co., Ltd.",
        "Unitron Tech Co Ltd",
        "Vitec Holdings Co Ltd",
        "WPG Holdings Limited",
        "Wuhan P&S Information Technology Co Ltd",
        "Yleiselektroniikka Oyj"
        ]

## 3. transfer list into queue
for company in companies:   
    input_companies.put("{} product".format(company))

class newBingCrawler:
    def __init__(self):
        ## init a new event loop for this threading(That is, one threading one event loop)
        policy = asyncio.get_event_loop_policy()
        self.loop = policy.new_event_loop()
        asyncio.set_event_loop(self.loop)

    ## 8.run into call function
    def __call__(self):
        async def fetch_coroutine(client, url):
            with async_timeout.timeout(10):
                try: 
                    async with client.get(url) as response:
                        assert response.status == 200
                        ## get purer text in every html file
                        if 'html' in str(response.content_type).lower():
                            html = await response.text()
                            soup = BeautifulSoup(html ,'lxml')
                            [x.extract() for x in soup.findAll('script')]
                            [x.extract() for x in soup.findAll('style')]
                            [x.extract() for x in soup.findAll('nav')]
                            [x.extract() for x in soup.findAll('footer')]
                            self.companyInfo += soup.text
                        return await response.release()
                except:
                    self.failLinks.append(url)

        ## 7. run into main function
        async def main(loop):
            ## go to bing, input query and submit 
            driver = webdriver.PhantomJS()
            url = "https://www.bing.com/"
            driver.get(url)
            elem = driver.find_element_by_xpath('//*[@id="sb_form_q"]')
            elem.send_keys(self.query)
            elem = driver.find_element_by_xpath('//*[@id="sb_form_go"]')
            elem.submit()
            html = driver.page_source
            driver.close()

            soup = BeautifulSoup(html, 'lxml')
            Links = soup.find_all('a')

            # Find links in first page in Bing Search Engine
            Goodlinks = []
            for link in Links:
                linkstr = str(link)
                if (('http' in linkstr) and ('href' in linkstr) and (not 'href="#"' in linkstr) and (not 'href="http://go.microsoft' in linkstr)and (not 'microsofttranslator' in linkstr)):
                    Goodlinks.append(link)
            urls = [link['href'] for link in Goodlinks]

            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
            async with aiohttp.ClientSession(loop=loop, headers=headers, conn_timeout=5 ) as client:
                tasks = [fetch_coroutine(client, url) for url in urls]
                await asyncio.gather(*tasks)
        
        ## 5. start async requests from a threading
        while True:
            try:
                ## get data from queue
                self.query = input_companies.get(timeout=1)   ##Build self.query
            except:
                break
            
            ## build self attribute
            self.companyInfo = ""  ##Build self.companyInfo
            exclude = set(string.punctuation)
            companyName = self.query.replace(" product", "")
            companyName = ''.join(p for p in companyName if p not in exclude)
            self.companyName = companyName.replace(" ", "_").lower()  ##Build self.companyName
            self.failLinks = []  ##Build self.failLinks

            ## 6. start running loop
            self.loop.run_until_complete(main(self.loop))

            ## 9. After loop
            fail_log.put({self.companyName:self.failLinks})
            

            ##if no such directory, creat one
            if not os.path.isdir("comapnyEmbedding"):
                os.mkdir("comapnyEmbedding")

            file = open("comapnyEmbedding/" + self.companyName, 'w', encoding='utf8')
            file.write(self.companyInfo)
            file.close()

            print("ThreadingID: " + str(id(self)) + ", " + companyName + " success")


## 4. count of threadings you want to build  
threads = []
for i in range(4):
    newthread = threading.Thread(target=newBingCrawler())
    newthread.start()
    threads.append(newthread)

## 10. join all threadings' result
for thread in threads:
    thread.join()

## 11. writing logs
logs = []
while True:
    try:
        logLi = fail_log.get(timeout=1)
        if logLi != []:
            logs.append(logLi)
    except:
        break

with open("FailLinks.log",'w', encoding='utf8') as fp:
    json.dump(logs, fp)
```
