---
title: 非同步的網頁爬取技術
date: '2017-07-29T23:30:23+00:00'
draft: false
categories:
- Web Scraping
summary: 概述 在網頁的取得上，因為每次去要求server回傳html檔時，都要等待回應一段時間，此時client端(也就是你的電腦)其實是沒有在運算的，因此若能夠使用這段時間，發出其他要求，將可大大增加爬取的速度。不過，非同步技術的概念其實相當複雜，甚至牽涉到一些硬體的知識，比較主要的難點在於與「多執行續」的差異解釋，這裡就不多加解釋，有興趣可以自行google。
  more 程式碼 在看這隻程式碼時，建議...
cover:
  image: /images/posts/20170822_multithread_async_scraping/0aa2666e-6118-4946-ace9-cf9f2d2b5aab.png
---

# 概述

在網頁的取得上，因為每次去要求server回傳html檔時，都要等待回應一段時間，此時client端(也就是你的電腦)其實是沒有在運算的，因此若能夠使用這段時間，發出其他要求，將可大大增加爬取的速度。不過，非同步技術的概念其實相當複雜，甚至牽涉到一些硬體的知識，比較主要的難點在於與「多執行續」的差異解釋，這裡就不多加解釋，有興趣可以自行google。 more

# 程式碼

在看這隻程式碼時，建議由最下面往上看，首先建立loop物件，然後透過run\_until\_complete方法執行Main function，再整理並打包執行多次「呼叫fetch\_coroutine function」的tasks。其中比較需要注意的是，要以非同步的方式執行的function，都必須在def前面寫上async，然後呼叫非同步方法時，等待回應須加上await。

```bash
import aiohttp
import asyncio
import async_timeout
import time
from bs4 import BeautifulSoup
 
 
async def fetch_coroutine(client, url):
    with async_timeout.timeout(10):
        async with client.get(url) as response:
            assert response.status == 200  ## 如果server端成功回應
            html = await response.text()  ##  取得html檔
            soup = BeautifulSoup(html ,'lxml')  ## 透過bs解析html
            As = soup.find_all('a')
            for a in As:
                try:
                    print(a)
                except:
                    print("----------------------------------Error------------------------------------")
            return await response.release()
 
 
async def main(loop):

    urls = ['http://python.org',
            'http://python.org',
            'http://python.org',
            'http://python.org',
            'http://python.org']

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
 
    async with aiohttp.ClientSession(loop=loop, headers=headers, conn_timeout=5 ) as client:
        tasks = [fetch_coroutine(client, url) for url in urls]  ##整理要執行的task(執行很多次fetch_coroutine function)
        await asyncio.gather(*tasks)  ## 把所有task打包
 
 
if __name__ == '__main__':  ## 如果這支程式是自己直接被執行，而不是透過其他python程式來呼叫，
    startTime = time.time()
    loop = asyncio.get_event_loop()  ## 首先建立一個loop物件
    loop.run_until_complete(main(loop))  ## 透過run_until_complete方法執行Main function
    finishTime = time.time()
    print(finishTime - startTime)
```

# 比較

上面那段程式碼(非同步)，我的電腦執行時間約是5~7秒不等，而執行以下的程式碼，執行時間約是15秒，約可以節省2/3的時間。

```bash
import requests
from bs4 import BeautifulSoup
import time

urls = ['http://python.org',
        'http://python.org',
        'http://python.org',
        'http://python.org',
        'http://python.org']

startTime = time.time()

for url in urls:
    re = requests.get(url)
    soup = BeautifulSoup(re.text, 'lxml')
    As = soup.find_all('a')
    for a in As:
        try:
            print(a)
        except:
            print("----------------------------------Error------------------------------------")
finishTime = time.time()
print(finishTime - startTime)
```
