---
title: Deploy Indri on Window 10 using Visual Studio
date: '2017-05-17T20:23:03+00:00'
draft: false
categories:
- Information Retrieval
summary: Introduction Indri is a powerful IR tool. For more information, you can go
  to their home page. To be mentioned in this article, although they assert that it
  can be set up on Windows, it is quite a har...
---

# Introduction

Indri is a powerful IR tool. For more information, you can go to their [home page](https://www.lemurproject.org/indri/). To be mentioned in this article, although they assert that it can be set up on Windows, it is quite a hard work. As a result, I wnat to write down the process about how to set it up on windows. more

However, I still recommend you to use Indri through Linux system if it is possible. It is very convenient to set up a virtual machine, and installing Ubuntu is just a piece of cake nowadays. If you still insist in using it in windows like me, below I will show you how to deal with all troubles when using Visual Studio to build the solution in Indri directory.

Tobe mentioned, if you use linux, tou can just run the scripts below to set it up. To check if you set up successfully, you can directly jump to [this part](#Finally)

```plaintext
sudo apt-get update
sudo apt-get install libz-dev
sudo apt-get install g++ 
sudo apt-get install zlib1g-dev

wget https://sourceforge.net/projects/lemur/files/lemur/indri-5.11/indri-5.11.tar.gz
tar xzvf indri-5.11.tar.gz
cd indri-5.11
./configure
make
sudo make install
```

# Download and unzip Indri

1. download: From [this page](https://sourceforge.net/projects/lemur/?source=typ_redirect), You can download indri-5.11.tar.gz.
    
2. unzip: The tool I use is [7-zip](http://www.developershome.com/7-zip/). To be mentioned, it is recommended to open 7-zip first and use browser in 7-zip to change your directory to where you download Indri and then unzip it.
    
    ![](/images/posts/20170517_deploy_indri_windows/02b32f50-93a2-40d0-9745-136e6c2ad707.png)
    
3. Then You can get this folder, and use Visual Studio to open indri-VS2012.sln.(I have tried both VS2015 and VS2017 can deal with this solution file)  
    
    ![](/images/posts/20170517_deploy_indri_windows/714d9f78-1e2e-4bb0-9e3f-ef0b45f27cf5.png)
    

# Build in Visual Studio

1. When going in to VS, you will first be called to update some packages, and just click yes.Then you'll get Program Manager window below.
    
    ![](/images/posts/20170517_deploy_indri_windows/e9d54160-db4c-4973-aa97-a178fa4f1e34.png)
    
    ![](/images/posts/20170517_deploy_indri_windows/1c5ab2df-494a-4b7b-8030-f4891dc93bd6.png)
    
2. (You can ignore this paragraph) If you are interested in how to debug of this solution, you can first rebuild all solution first. Just right click on solution'Indri-VS2012'(15 Projects) and click rebuild. Then you'll get three kinds of bugs in the following files.
    
    * (clarity)lemur-compat.hpp and (dist)SequentialReadBuffer.hpp
        
    * (dist)hash\_set or hash\_map
        
    * (swig) indri\_jni.cpp  
        
        ![](/images/posts/20170517_deploy_indri_windows/03d1089e-cd54-4f78-a525-c8c7dd3fa871.png)
        
        ![](/images/posts/20170517_deploy_indri_windows/064f2a33-fc42-4b38-97eb-5b57f7cd5a61.png)
        

# Solutions to three kinds of bugs

1. go to lemur-compat.hpp and SequentialReadBuffer.hpp, on the Top of the file add "#include &lt;algorithm&gt;"
    
    ![](/images/posts/20170517_deploy_indri_windows/d141bab9-072c-4fa8-a768-0c29ae04e0f4.png)
    
2. In the Program Manager window: Right click dist &gt;property &gt;c++ &gt;preprocessor definition&gt; add "\_SILENCE\_STDEXT\_HASH\_DEPRECATION\_WARNINGS=1;" befor all words.
    
    ![](/images/posts/20170517_deploy_indri_windows/e9fc4b3e-dba9-4f32-9041-c567a012e5e6.png)
    
3. Add your java sdk path to: Right click swig &gt;property &gt;C++ &gt;Other include directories. Remember to add two path: one is \\jdkxxx\\include, another is jdkxxx\\include\\win32.(If you haven't install java sdk, you have to deal withh the problem yourself)
    
    ![](/images/posts/20170517_deploy_indri_windows/295af377-1905-4d5a-bb38-6deea2efe324.png)
    

# Finally

1. Rebuild all Solution
    
2. use command line to test if it is set up successfully. you can type in: $ dumpindex and you'll get:
    
    ![](/images/posts/20170517_deploy_indri_windows/ad476738-8e21-48d0-82d4-d0eeb6e52c07.jpeg)
