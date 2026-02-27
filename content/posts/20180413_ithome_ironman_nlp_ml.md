---
title: 玩轉資料與機器學習-以自然語言處理為例（ithome鐵人競賽）
date: '2018-04-13T00:00:00+00:00'
draft: false
categories:
- Machine Learning
tags:
- machine-learning
- nlp
- ithome
- ironman
summary: 2017 ithome鐵人競賽：包含網路爬蟲、Pandas、自然語言處理、資訊檢索、機器學習等主題的30天文章索引。
---

# Introduction

1. Github: <https://github.com/GoatWang/ithome_ironman>
2. Reader Feedback: 
   > Hi, I see your article on Iron Man  
   > Feel very good writing, although I am now a Web Developer  
   > But the data chain that I studied at the institute previously also uses Python to handle ML, data mining, etc.  
   > Your article made me impulsive and wanted to return to Python, and looked at your article to return to practice  
   > Hope to establish a relationship with you:)

![Reader Feedback](/images/posts/20180413_ithome_ironman_nlp_ml/encourage.JPG "Reader Feedback")

# Table of Content

* Roadmap
  + [Roadmap for Data Analyst](https://ithelp.ithome.com.tw/articles/10190849)
  + [Roadmap for Data Analyst(Cont.)](https://ithelp.ithome.com.tw/articles/10190859)
* Web Crawling
  + [Web Crawling Day1 - Introduction](https://ithelp.ithome.com.tw/articles/10190994)
  + [Web Crawling Day2 - Html File Obtaining and General Problems](https://ithelp.ithome.com.tw/articles/10191161)
  + [Web Crawling Day3 - Html File Obtaining and General Problems(Cont.)](https://ithelp.ithome.com.tw/articles/10191165)
  + [Web Crawling Day4 - Html File Analysis](https://ithelp.ithome.com.tw/articles/10191259)
  + [Web Crawling Day5 - Advaced: Async Carwling](https://ithelp.ithome.com.tw/articles/10191401)
  + [Web Crawling Day5 - Advaced: Async Carwling and Multithread](https://ithelp.ithome.com.tw/articles/10191405)
* Database
  + [Interaction between Python and MongoDB](https://ithelp.ithome.com.tw/articles/10191408)
* Pandas
  + [Pandas(Excel in Python) Day1 - Data Type and File Reading and Writing](https://ithelp.ithome.com.tw/articles/10191291)
  + [Pandas(Excel in Python) Day2 - DataFrame Data Description and Attributes](https://ithelp.ithome.com.tw/articles/10191588)
  + [Pandas(Excel in Python) Day3 - DataFrame Indexing and Updating](https://ithelp.ithome.com.tw/articles/10191616)
  + [Pandas(Excel in Python) Day4 - DataFrame Insert, Delete and Loop](https://ithelp.ithome.com.tw/articles/10191774)
* Natural Language Processing
  + [English NLP Basics](https://ithelp.ithome.com.tw/articles/10191922)
  + [Chinese NLP Basics](https://ithelp.ithome.com.tw/articles/10192043)
* Information Retrieval
  + [IR Basics - Theory](https://ithelp.ithome.com.tw/articles/10192323)
  + [IR Basics - Implementing LineBot Retrieval Engine](https://ithelp.ithome.com.tw/articles/10192645)
  + [Evaluation of Information Retrieval](https://ithelp.ithome.com.tw/articles/10192869)
* Preprocessing
  + [Preprocessing](https://ithelp.ithome.com.tw/articles/10191069)
  + [Preprocessing(Cont.)](https://ithelp.ithome.com.tw/articles/10193022)
* Machine Learning
  + [Machine Learning Introduction](https://ithelp.ithome.com.tw/articles/10193749)
  + [Clustering Algorithm Theory](https://ithelp.ithome.com.tw/articles/10193760)
  + [Clustering Algorithm Implementation - Distinguishing Between Different Algorithm](https://ithelp.ithome.com.tw/articles/10194172)
  + [Product Label Clustering - Word2Vec](https://ithelp.ithome.com.tw/articles/10194369)
  + [Classification Theory - Traditional Algorithm](https://ithelp.ithome.com.tw/articles/10194690)
  + [Classification Theory - SVM and XGB+CV](https://ithelp.ithome.com.tw/articles/10194824)
  + [Classification Implementation - LineBot Project](https://ithelp.ithome.com.tw/articles/10195030)
* Conclusion
  + [2017 Data Analyst Practice](https://ithelp.ithome.com.tw/articles/10195825)
* Weekend Special
  + [Weekend Special - iThome Ironman Articles Analysis](https://ithelp.ithome.com.tw/articles/10191848)
  + [Weekend Special - iThome Ironman Articles Analysis(Cont.)](https://ithelp.ithome.com.tw/articles/10193103)
  + [Weekend Special - Predict Top 10 Days Browse Count for iThome Competition Articles](https://ithelp.ithome.com.tw/articles/10195967)

# 中文原文索引

* 學習之路
  + [資料分析師的學習之路](https://ithelp.ithome.com.tw/articles/10190849)
  + [資料分析師的學習之路(續)](https://ithelp.ithome.com.tw/articles/10190859)
* 網路爬蟲
  + [網路爬蟲Day1-概述](https://ithelp.ithome.com.tw/articles/10190994)
  + [網路爬蟲Day2-html檔的取得及常見問題](https://ithelp.ithome.com.tw/articles/10191161)
  + [網路爬蟲Day3-html檔的取得及常見問題(續)](https://ithelp.ithome.com.tw/articles/10191165)
  + [網路爬蟲Day4-html檔的解析](https://ithelp.ithome.com.tw/articles/10191259)
  + [網路爬蟲Day5-爬蟲進階:非同步爬蟲程式的撰寫](https://ithelp.ithome.com.tw/articles/10191401)
  + [網路爬蟲Day6-爬蟲進階:非同步爬蟲配上多執行續](https://ithelp.ithome.com.tw/articles/10191405)
* 資料庫
  + [Python與MongoDB的互動](https://ithelp.ithome.com.tw/articles/10191408)
* Pandas
  + [Pandas(Python中的Excel)Day1-資料類型與讀寫檔案](https://ithelp.ithome.com.tw/articles/10191291)
  + [Pandas(Python中的Excel)Day2-DataFrame的資料描述與屬性](https://ithelp.ithome.com.tw/articles/10191588)
  + [Pandas(Python中的Excel)Day3-DataFrame的索引與更新](https://ithelp.ithome.com.tw/articles/10191616)
  + [Pandas(Python中的Excel)Day4-DataFrame的新增、迴圈與刪除](https://ithelp.ithome.com.tw/articles/10191774)
* 自然語言處理
  + [英文自然語言處理基礎](https://ithelp.ithome.com.tw/articles/10191922)
  + [中文自然語言處理基礎](https://ithelp.ithome.com.tw/articles/10192043)
* 文件檢所
  + [文件檢索概述-理論](https://ithelp.ithome.com.tw/articles/10192323)
  + [文件檢索概述-實作出LineBot檢索引擎](https://ithelp.ithome.com.tw/articles/10192645)
  + [文件檢索的評價](https://ithelp.ithome.com.tw/articles/10192869)
* 前處理
  + [資料前處理](https://ithelp.ithome.com.tw/articles/10191069)
  + [資料前處理(續)](https://ithelp.ithome.com.tw/articles/10193022)
* 機器學習
  + [機器學習系列概述](https://ithelp.ithome.com.tw/articles/10193749)
  + [分群演算法理論](https://ithelp.ithome.com.tw/articles/10193760)
  + [分群演算法實作-區辨不同演算法的意義](https://ithelp.ithome.com.tw/articles/10194172)
  + [產品標籤分群實作-Word2Vec](https://ithelp.ithome.com.tw/articles/10194369)
  + [分類演算法理論-傳統演算法](https://ithelp.ithome.com.tw/articles/10194690)
  + [分類演算法理論-SVM及XGB+CV](https://ithelp.ithome.com.tw/articles/10194824)
  + [分類演算法實作-LineBot專案](https://ithelp.ithome.com.tw/articles/10195030)
* 總結
  + [2017資料分析師的練成之路](https://ithelp.ithome.com.tw/articles/10195825)
* 周末特別節目
  + [周末特別節目-iThome鐵人文章分析](https://ithelp.ithome.com.tw/articles/10191848)
  + [周末特別節目-iThome鐵人文章分析(續)](https://ithelp.ithome.com.tw/articles/10193103)
  + [周末特別節目-預測文章頭十天的瀏覽人次(限iThome鐵人文章)](https://ithelp.ithome.com.tw/articles/10195967)
