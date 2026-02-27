---
title: Linebot 2.0 with Django Complete Tutorial — Echo Bot, Saving Userprofile, Two-Page
  Richmenu
date: '2020-02-12T04:15:02+00:00'
draft: false
categories:
- Web Development
summary: 'Introduction There are four parts in this tutorial. The Github repo is at
  https://github.com/GoatWang/LinebotTutorial. Create Line Official Account: Line
  official account is different from general lin...'
cover:
  image: /images/posts/20200212_linebot_django_tutorial/93a7bceb-6223-45bb-9bae-5b241c9a3a09.png
---

### Introduction

There are four parts in this tutorial. The Github repo is at [https://github.com/GoatWang/LinebotTutorial](https://github.com/GoatWang/LinebotTutorial).

1.  **Create Line Official Account**: Line official account is different from general line account. Line official account will be shown as an independent username & picture in line.
2.  **Build Django Backend Website (Echo Bot)**: In this part, the communication structure between user, line server and the website will be explained. Also, this tutorial will go through every step to build this website and deploy on to the heroku.
3.  **Write Logic of the Bot (Saving Userprofile)**: The concept of Event, LineBotApi, Message and Action will be explained. Dealing with different types of Events, Sending different types of Messages, Embedding different types of Actions in the Message is the main point of this section. In the implementation tutorial, we are going to save the user profile into the database when the user add the account as a friend.
4.  **RichMenu and RichMessage (Two-Page Richmenu**)**:** It is common to use self-defined images as button in Line nowadays. This part will describe how to produce this kind of image and the location of buttons. Also, we are going to make a two-page RichMenu in the implementation tutorial.

### **Create Line Official Account**

#### Intro: Linebot Management Official Websites

There are two main websites to manage your bot: [Line Business ID](https://account.line.biz/login?redirectUri=https%3A%2F%2Fmanager.line.biz%2F) and [Line Developer](https://developers.line.biz/zh-hant/). There are two things to be noticed:

1.  Even most of the settings can be set in both sites, **some settings can be managed only in one site**. For example, developer “*Roles”* can only be managed in [Line Developer](https://developers.line.biz/zh-hant/), while “*Rich menus”* can only be designed in [Line Business ID](https://account.line.biz/login?redirectUri=https%3A%2F%2Fmanager.line.biz%2F).
2.  [Line Business ID](https://account.line.biz/login?redirectUri=https%3A%2F%2Fmanager.line.biz%2F) is for Linebot 2.0, while Line@ Manager is for Linebot 1.0. **If you don’t know what is Line@ Manager, just forget it.** you can not log in to Line@ Manager if you don’t have any bot in Linebot 1.0. Do not confuse any of them with each other.

#### Step1: Allow your line account to log through other platforms.

![](/images/posts/20200212_linebot_django_tutorial/6b2cb6ad-c132-4f01-8fc0-51dbf9d9a2a7.jpeg)

#### Step2: Log in [Line Developer](https://developers.line.biz/zh-hant/)

![](/images/posts/20200212_linebot_django_tutorial/4dba2ea9-b05a-4dc4-9fbf-fd33096ddea6.png)

#### Step3: Create a new Provider

![](/images/posts/20200212_linebot_django_tutorial/ba5caaa5-e272-4e4e-b74a-57caa87b9c2b.png)

#### Step4: Select Channel Type: Messaging API Channel

![](/images/posts/20200212_linebot_django_tutorial/f07644ee-f2f1-49cd-b39b-1e6edce5c56a.png)

#### Step5: Create Messaging API channel

![](/images/posts/20200212_linebot_django_tutorial/bbe88905-bf8d-4e0c-995a-0763f52f0217.png)

#### Step6: other operations

1.  disable the Auto-reply messages
2.  issue a secret token

![](/images/posts/20200212_linebot_django_tutorial/3aa19ee5-08a6-4ce4-b2e0-683b097dd85c.png)

### **Build Django Backend Website**

#### Intro: the communication structure between user, line server and the website.

There are two kinds of interaction mode in Line Messaging API: reply and push. In reply mode, the reply message will be sent only when the user questioned. In push mode, however, the push message will be sent automatically whenever you want. **To be noticed, there is no limitation on the number of reply messages but only 500 user \* message can be sent at line’s free-tier price plan.** That is to say, once you have more than 500 friends, you cannot use push message function at line’s free-tier price plan.

The image below shows the interaction chain of user client, line server and your server. In reply mode, message will first from sent from user client to line server, then your server (left-to-right). This is followed by the backward response (right-to-left). In push mode, only the backward direction interaction (right-to-left) will happen. Anyway, we are going to build a django server as an echo bot in the section.

#### Step1: Install prerequisite

1.  Install Python3.6 ( [https://www.python.org/downloads/release/python-365/](https://www.python.org/downloads/release/python-365/))
2.  packages: django, virtualenv

\>>> pip install django virtualenv

#### Step2: Create a project

Once Django is successfully installed in your python, you can run *django-admin startproject <project\_name>* to create a new project.

\>>> django-admin startproject LinebotTutorial

This command will create a directory with a structure like this.

│   manage.py  
│  
└───LinebotTutorial  
    │   settings.py  
    │   urls.py  
    │   wsgi.py  
    └   \_\_init\_\_.py

#### Step2: Create an app

An application can be imagined as an independent module of the whole website. If we only want to create linebot server, one application is enough. Be sure to change directory to the project directory. Then run *python manage.py startapp <app\_name>* to create a new application. **To be mentioned, its recommended not to set *app\_name* as names that will appear in the packages used by the project such as “linebot” or “app”.**

\>>> cd LinebotTutorial  
\>>> python manage.py startapp tutorialbot

This command will create a directory called tutorialbot. The whole structure will be like this.

│   manage.py  
│  
├───LinebotTutorial  
│   │   settings.py  
│   │   urls.py  
│   │   wsgi.py  
│   └   \_\_init\_\_.py  
└───tutorialbot  
    │   admin.py  
    │   apps.py  
    │   models.py  
    │   tests.py  
    │   views.py  
    │   \_\_init\_\_.py  
    │  
    └───migrations  
            \_\_init\_\_.py

#### Step3: Build a virtual environment

Virtual environment is generally used in python to build an independent environment that can help to avoid the conflicts between packages. Virtual environment is also helpful for coping an environment from PC to server.

\>>> virtualenv venv # create the env  
\>>> venv\\Scripts\\activate  #activate the env  
\>>> pip install django line-bot-sdk #install packages

#### Step4: write the response function and set the route

*   in tutorialbot\\views.py

from django.http import HttpResponse

def index(request):  
    return HttpResponse("test!!")

*   create tutorialbot\\urls.py

from django.urls import path  
from . import views

urlpatterns = \[  
    path('', views.index, name='index'),  
\]

*   in LinebotTutorial\\urls.py

from django.contrib import admin  
from django.urls import include, path

urlpatterns = \[  
    path('tutorialbot/', include('tutorialbot.urls')),  
    path('admin/', admin.site.urls),  
\]

#### Step5: test runserver locally

Run the server locally using the following script, and go to [http://127.0.0.1:8000/tutorialbot/](http://127.0.0.1:8000/tutorialbot/). If you can see “test!!”, you successfully run the server locally.

\>>> python manage.py runserver

#### Steps6: Deployment of the website

Be sure that the url of the website should be https which is limited by line official. Once you don’t have https server, it is recommended to use heroku. Heroku is a free resource to deploy your website. The only drawback is that the server will sleep when it receives no web traffic in a 30-minute. It will wake up when receiving a new request, but it takes about 30 seconds to wake up. The Django deploy [tutorial](https://devcenter.heroku.com/articles/django-app-configuration) is issued by heroku.

*   install [heroku-cli](https://devcenter.heroku.com/articles/getting-started-with-python#set-up)
*   [create heroku account](https://id.heroku.com/login)
*   prepare prerequisite files

\# prepare requirements.txt in the project root directory  
`>>> pip install gunicorn  
>>> pip install django-heroku  
`\>>> pip freeze > requirements.txt

\# in the LinebotTutorial\\settings.py  
`# at the top of settings.py  
import django_heroku`  
`# at the bottom of settings.py  
`django\_heroku.settings(locals()) #Activate Django-Heroku.

\# create Procfile (no extension) in the project root directory  
web: gunicorn LinebotTutorial.wsgi

*   prepare the project as a git repo

Write .gitignore in the project root to avoid venv directory to be uploaded since it is quite fat. And we are going to use requirements.txt to copy the venv in the server.

#just write these lines in .gitignore  
venv   
staticfiles  
\_\_pycache\_\_

initialize a git repo

\>>> git init   
\>>> git add .  
\>>> git commit -m "my first commit"

*   login to heroku & create the app & deploy the website

\>>> heroku login   
\>>> heroku create # create the heroku app  
\>>> `git push heroku master # deploy the code on to the heroku server  
`\>>> heroku ps:scale web=1 # call the server to run the Procfile  
\>>> heroku open # open the website url. you can add "/tutorialbot/" at the end of the url, then you will see the test!! again

#### Step7: Write CHANNEL\_ACCESS\_TOKEN and CHANNEL\_SECRET

write LINE\_CHANNEL\_ACCESS\_TOKEN and LINE\_CHANNEL\_SECRET, which is from Line Business ID website, at the bottom of LinebotTutorial\\settings.py. If you are going to push this to the cloud server such as Github, it is recommended to store the token and the secret in the environment variables and call them through *os.environ\[‘<env\_name>’\]*

LINE\_CHANNEL\_ACCESS\_TOKEN = "<your LINE\_CHANNEL\_ACCESS\_TOKEN>"  
LINE\_CHANNEL\_SECRET = "<your LINE\_CHANNEL\_SECRET>"

#### Step8: Write response function

This code is modified from [line-bot-sdk](https://github.com/line/line-bot-sdk-python) git repository. It is used to receive the requests from line server and give the same text response back to line.

in tutorialbot/views.py

from django.conf import settings # calls the object written in settings.py  
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse  
from django.views.decorators.csrf import csrf\_exempt  
from linebot import LineBotApi, WebhookHandler  
from linebot.exceptions import InvalidSignatureError  
from linebot.models import MessageEvent, TextMessage, TextSendMessage

line\_bot\_api = LineBotApi(settings.LINE\_CHANNEL\_ACCESS\_TOKEN)  
handler = WebhookHandler(settings.LINE\_CHANNEL\_SECRET)

\# this is for testing  
def index(request):  
    return HttpResponse("test!!")

\# this is code is modeified from [https://github.com/line/line-bot-sdk-python](https://github.com/line/line-bot-sdk-python)  
[@csrf\_exempt](http://twitter.com/csrf_exempt "Twitter profile for @csrf_exempt") # this is used for avoid csrf request from line server  
def callback(request):  
    if request.method == "POST":  
        # get X-Line-Signature header value  
        signature = request.META\['HTTP\_X\_LINE\_SIGNATURE'\]  
        global domain  
        domain = request.META\['HTTP\_HOST'\]  
          
        # get request body as text  
        body = request.body.decode('utf-8')

        # handle webhook body  
        try:  
            handler.handle(body, signature)  
        except InvalidSignatureError:  
            return HttpResponseBadRequest()

        return HttpResponse()  
    else:  
        return HttpResponseBadRequest()

\# this function is used for process TextMessage from users  
[@handler](http://twitter.com/handler "Twitter profile for @handler").add(MessageEvent, message=TextMessage)  
def handle\_message(event):  
    line\_bot\_api.reply\_message(  
        event.reply\_token,  
        TextSendMessage(text=event.message.text))

in tutorialbot/urls.py

urlpatterns = \[  
    path('', views.index, name='index'),  
    path('callback/', views.callback, name='callback'), # add this line  
\]

in the INSTALLED\_APP part in SLinebotTutorial/settings.py

INSTALLED\_APPS = \[  
    'tutorialbot.apps.TutorialbotConfig', # add this line  
    ...  
    'django.contrib.messages',  
    'django.contrib.staticfiles',  
\]

deploy the app

\>>> git add .  
\>>> git commit -m "callback function"  
\>>> git push heroku master

#### Step9: Set Webhook url on Line Developers

Fill in your heroku url , which can get from “heroku open”. Remember to add “/LinebotTutorial/callback/” at the tail of the url. After editing the url, be careful to check the “Use webhook” button.

![](/images/posts/20200212_linebot_django_tutorial/b770e3d2-8e65-4126-9210-bea09633c726.png)

#### Step10: add your bot as a friend and check its status

![](/images/posts/20200212_linebot_django_tutorial/d00fd41c-9b25-489b-8b7a-0f8602af841d.jpeg)

### **Write Logic of the Bot**

#### Intro: Event, LineBotApi, Message and Action

The basic concept of line-bot-sdk is composed of Event, Message, LineBotApi, SendMessage and Action objects. Once the bot receives an **Event** (e.g. MessageEvent) with a Message (**TextMessage**), the bot server should use **LineBotApi** to reply\_message. Then **SendMessage** type (e.g. TextSendMessage) should be selected. If some buttons is embedded in the **SendMessage** (e.g. TemplateSendMessage), the **Action** (e.g. UriAction)should be defined when the button is clicked. All types of **Event**, **Message , SendMessage** and **Action** and all functions of **LineBotApi** are described in detail in the repo of [line-bot-sdk](https://github.com/line/line-bot-sdk-python). Some generally used objects of [line-bot-sdk](https://github.com/line/line-bot-sdk-python) are listed below.

*   Event Types: MessageEvent, FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent, PostbackEvent…
*   Message Types: TextMessage, ImageMessage, LocationMessage, FileMessage…
*   LineBotApi Functions: reply\_message, push\_message, get\_profile…
*   SendMessage Types: TextSendMessage, ImageSendMessage, LocationSendMessage, StickerSendMessage, ImagemapSendMessage, TemplateSendMessage…
*   Action Types: URIAction, PostbackAction, MessageAction…

#### Intro: Deal with the FollowEvent

In this section, I am going to use FollowEvent as example to illustrate the method to use Event, LineBotApi, Message and Action objects in Django. As a result, we are going to experience the following steps:

1.  the user adds the bot as a friend, and the bot receives the **FollowEvent** without Message.
2.  the bot use **get\_profile** to get the user profile and save it to the database.
3.  the bot send a **TemplateSendMessage** with a button to ask the user if he/she wants to receive sales promotion messages.
4.  When the button is clicked, the **PostbackAction** will be triggered and bot will receive a **PostbackEvent** and update the database**.**

#### Step1: Disable Greeting Message from line

![](/images/posts/20200212_linebot_django_tutorial/7933b1f4-e924-43c7-8afc-9b080cc1dcd4.png)

#### Step2: Open Userprofile schema in Database

Although Django have built a User model for us, the schema is not matched with the information provided by line. As a result, we should design a new schema to save information provided by **get\_profile** function. To be mentioned, sqlite3 is used as the default database by Django, which can be changed by editing settings.py.

*   in tutorialbot/models.py

from django.db import models  
from django.contrib.auth.models import User

\# Create your models here.  
class UserProfile(models.Model):  
    # get from line  
    user = models.OneToOneField(User, on\_delete=models.CASCADE) #OneToOneField is used to extend the original User object provided from Django.  
    line\_id = models.CharField(max\_length=50, primary\_key=True, verbose\_name="LineID")  
    line\_name = models.CharField(max\_length=100, verbose\_name="Line名稱")  
    line\_picture\_url = models.URLField(verbose\_name="Line照片網址")  
    line\_status\_message = models.CharField(max\_length=100, blank=True, null=True, verbose\_name="Line狀態訊息")

    # generated by system  
    unfollow = models.BooleanField(default=False, verbose\_name="封鎖")  
    create\_time = models.DateTimeField(auto\_now=True, verbose\_name="創建時間")

    # other  
    promotable = models.BooleanField(default=False, verbose\_name="promotable")

*   update the database

\>>> python manage.py makemigrations # generate the sql code   
\>>> python manage.py migrate # apply the sql code to local DB

#### Step3: Handle FollowEvent Function

*   at the top of tutorialbot/views.py

from django.contrib.auth.models import User  
from tutorialbot.models import UserProfile  
from linebot.models import (  
    MessageEvent, FollowEvent,   
    TextMessage,   
    PostbackAction,  
    TextSendMessage, TemplateSendMessage,   
    ButtonsTemplate  
    )

*   at the bottom of tutorialbot/views.py

[@handler](http://twitter.com/handler "Twitter profile for @handler").add(FollowEvent)  
def handle\_follow(event):  
    line\_id = event.source.user\_id  
    profile = line\_bot\_api.get\_profile(line\_id)  
    profile\_exists = User.objects.filter(username=line\_id).count() != 0  
    if profile\_exists:  
        user = User.objects.get(username = line\_id)  
        user\_profile = UserProfile.objects.get(user = user)  
        user\_profile.line\_name = profile.display\_name  
        user\_profile.line\_picture\_url = profile.picture\_url  
        user\_profile.line\_status\_message = profile.status\_message  
        user\_profile.unfollow = False  
        user\_profile.save()  
    else:  
        user = User(username = line\_id)  
        user.save()  
        user\_profile = UserProfile(  
            line\_id = line\_id,  
            line\_name = profile.display\_name,  
            line\_picture\_url = profile.picture\_url,  
            line\_status\_message=profile.status\_message,  
            user = user  
        )  
        user\_profile.save()

    buttons\_template\_message = TemplateSendMessage(  
        alt\_text='Product Promotion',  
        template=ButtonsTemplate(  
            title="Product Promotion",  
            text='Do you want to receive the promotion messages?',  
            actions=\[  
                PostbackAction(  
                    label='yes',  
                    display\_text='yes',  
                    data='promotion=true'  
                ),  
            \]  
        )  
    )

    line\_bot\_api.reply\_message(  
        event.reply\_token,  
        \[  
            TextSendMessage(text="Hello\\U0010007A"),  
            buttons\_template\_message,  
        \]  
    )

*   deploy to heroku

\>>> git add .  
\>>> git commit -m "handle FollowEvent"  
\>>> git push heroku master  
\>>> `heroku run python manage.py migrate` \# apply the sql code to heroku DB

#### Step4: Test in line

Unfollow the account first, then follow it again.

![](/images/posts/20200212_linebot_django_tutorial/76caa198-526e-4516-a070-3f43750d63fb.jpeg)

#### Step5: Test in Heroku

*   ssh to heroku server & run Django shell

```
>>> heroku run python manage.py shell
```

*   show all UserProfile

\>>> from tutorialbot.models import UserProfile  
\>>> user\_profiles = UserProfile.objects.all()  
\>>> for u in user\_profiles:  
...     print(u.line\_name, u.create\_time)

Then, “<user\_line\_name> <create\_time>” will be printed.

#### Step6: Handle PostbackEvent Function

*   at the top of tutorialbot/views.py

from linebot.models import (  
    MessageEvent, FollowEvent, PostbackEvent,  
    TextMessage,   
    PostbackAction,  
    TextSendMessage, TemplateSendMessage,   
    ButtonsTemplate  
    )

*   at the bottom of tutorialbot/views.py

[@handler](http://twitter.com/handler "Twitter profile for @handler").add(PostbackEvent)  
def handle\_postback(event):  
    if event.postback.data == "promotion=true":  
        line\_id = event.source.user\_id  
        user\_profile = User.objects.get(username=line\_id)  
        user\_profile.promotable= True # set promotable to be True  
        user\_profile.save()

*   push to heroku server

\>>> git add .  
\>>> git commit -m "handle PostbackEvent"  
\>>> git push heroku master

#### Step7: Test in Heroku

*   ssh to heroku server & run Django shell

```
>>> heroku run python manage.py shell
```

*   show all UserProfile

\>>> from tutorialbot.models import UserProfile  
\>>> user\_profiles = UserProfile.objects.all()  
\>>> for u in user\_profiles:  
...     print(u.line\_name, u.promotable, u.create\_time)

Then, “<user\_line\_name> <promotable> <create\_time>” will be printed.

### **Rich Menu and Message**

#### Intro: we are going to implement…

In the section, I draw two images. There is a button to go to the next page in the first image, while there is a button to go to the previous page in the second image. The icon of my company is just an url to go to the home website of Thinktron.

![](/images/posts/20200212_linebot_django_tutorial/b1aff08a-c990-41a6-888b-21e032d3c82f.jpeg)

![](/images/posts/20200212_linebot_django_tutorial/ce7d9a18-616d-4c68-ad26-5c90a819e12f.jpeg)

#### step1: prepare the images

There is a limitation on the images’ size. **The size should be in 2500x1686, 2500x843, 1200x810, 1200x405, 800x540 or 800x270, which is from** [**here**](https://developers.line.biz/en/reference/messaging-api/#create-rich-menu)**.** To make this kind of image, I use an online tool called [pixlr](https://pixlr.com/). It is possible to create any size of canvas and draw any image on to the canvas, which can help to generate the required images.

#### step2: write the script to define the location of buttons

There are two ways to define the location and area of buttons. First is [Line Business ID](https://manager.line.biz/). Its drawback is you can design the RichMenu only by templates provided by line. Also, the postback action cannot be set on the website.

![](/images/posts/20200212_linebot_django_tutorial/e3706c3a-543a-48cc-ab8d-9169399407bd.png)

where to design richmenu

![](/images/posts/20200212_linebot_django_tutorial/98ea5e5b-eae1-4fd9-8bbe-4f12ce60a7e5.png)

templates provided by line

![](/images/posts/20200212_linebot_django_tutorial/aab84283-76dd-4d94-96ec-166b2e7f448a.png)

No postback action

The second way to design RichMenu is sand a post request to line server. It is more complicated but more flexible. You have to define the absolute start location (x and y) and the area (height and width) for each button. It is possible that you want to put many buttons on your RichMenu and they are all in the arbitrary location and area. It’s recommended to use [Bot Designer](https://developers.line.biz/en/services/bot-designer/) to design it, the tool provides a convenient GUI.

What we are going to is just split the image into two parts (left and right). As a result, we can just divide the width of the image by 2 to get the width of the button.

![](/images/posts/20200212_linebot_django_tutorial/4935f682-9528-4a03-8e41-0eed6687b47c.png)

*   create a new directory called RichMenu in the project root
*   create a new directory called images in the RichMenu directory
*   put the image in the images directory (if you want to use the same image with this project, download by [here](https://drive.google.com/drive/folders/1jfnH0ZLckSeP4goT77ExNKL47v3F98ae?usp=sharing). The size of the image is 800 \* 540)
*   create two .py files called create\_firstpage.py & create\_secondpage.py
*   (optional) create a .py files called list\_richmenus.py

![](/images/posts/20200212_linebot_django_tutorial/e88b5690-55ad-4609-842a-af6ba2fd1838.png)

*   remember to add RichMenu directory in .gitignore file

venv  
.vscode  
staticfiles  
\_\_pycache\_\_  
RichMenu # add this line

*   in create\_firstpage.py

Notice the RichMenuBounds of the first area, the start location is (0, 0), width is 400(half of the image width) and height is 540 (same with the image). **The RichMenu id will be printed, which should be kept and used in the postback event handler in views.py.**

import os  
import requests  
from linebot import LineBotApi  
from linebot.models import (  
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds,   
    URIAction, PostbackAction  
    )  
LINE\_CHANNEL\_ACCESS\_TOKEN = "<your LINE\_CHANNEL\_ACCESS\_TOKEN>"  
line\_bot\_api = LineBotApi(LINE\_CHANNEL\_ACCESS\_TOKEN)

\# create rich menu  
\# from [https://developers.line.biz/en/reference/messaging-api/#create-rich-menu](https://developers.line.biz/en/reference/messaging-api/#create-rich-menu)  
rich\_menu\_to\_create = RichMenu(  
    size=RichMenuSize(width=800, height=540), #2500x1686, 2500x843, 1200x810, 1200x405, 800x540, 800x270  
    selected=True,  
    name="NextPage",  
    chat\_bar\_text="See Menu",  
    areas=\[  
        RichMenuArea(  
            bounds=RichMenuBounds(x=0, y=0, width=400, height=540),  
            action=URIAction(label='Thinktron', uri='[https://www.thinktronltd.com/'](https://www.thinktronltd.com/%27))),  
        RichMenuArea(  
            bounds=RichMenuBounds(x=400, y=0, width=400, height=540),  
            action=PostbackAction(label='Next Page', data='action=nextpage')),  
        \]  
)  
rich\_menu\_id = line\_bot\_api.create\_rich\_menu(rich\_menu=rich\_menu\_to\_create)  
print("rich\_menu\_id", rich\_menu\_id)

\# upload image and link it to richmenu  
\# from [https://developers.line.biz/en/reference/messaging-api/#upload-rich-menu-image](https://developers.line.biz/en/reference/messaging-api/#upload-rich-menu-image)  
with open(os.path.join('images', 'firstpage.jpg'), 'rb') as f:  
    line\_bot\_api.set\_rich\_menu\_image(rich\_menu\_id, 'image/jpeg', f)

\# set as default image  
url = "[https://api.line.me/v2/bot/user/all/richmenu/](https://api.line.me/v2/bot/user/all/richmenu/)"+rich\_menu\_id  
requests.post(url, headers={"Authorization": "Bearer "+LINE\_CHANNEL\_ACCESS\_TOKEN})

*   in create\_secondpage.py

import os  
import requests  
from linebot import LineBotApi  
from linebot.models import (  
    RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds,   
    URIAction, PostbackAction  
    )  
LINE\_CHANNEL\_ACCESS\_TOKEN = "<your LINE\_CHANNEL\_ACCESS\_TOKEN>"  
line\_bot\_api = LineBotApi(LINE\_CHANNEL\_ACCESS\_TOKEN)

\# create rich menu  
\# from [https://developers.line.biz/en/reference/messaging-api/#create-rich-menu](https://developers.line.biz/en/reference/messaging-api/#create-rich-menu)  
rich\_menu\_to\_create = RichMenu(  
    size=RichMenuSize(width=800, height=540), #2500x1686, 2500x843, 1200x810, 1200x405, 800x540, 800x270  
    selected=True,  
    name="PreviousPage",  
    chat\_bar\_text="See Menu",  
    areas=\[  
        RichMenuArea(  
            bounds=RichMenuBounds(x=0, y=0, width=400, height=540),  
            action=PostbackAction(label='Previous Page', data='action=previouspage')),  
        RichMenuArea(  
            bounds=RichMenuBounds(x=400, y=0, width=400, height=540),  
            action=URIAction(label='Thinktron', uri='[https://www.thinktronltd.com/'](https://www.thinktronltd.com/%27))),  
        \]  
)  
rich\_menu\_id = line\_bot\_api.create\_rich\_menu(rich\_menu=rich\_menu\_to\_create)  
print("rich\_menu\_id", rich\_menu\_id)

\# upload image and link it to richmenu  
\# from [https://developers.line.biz/en/reference/messaging-api/#upload-rich-menu-image](https://developers.line.biz/en/reference/messaging-api/#upload-rich-menu-image)  
with open(os.path.join('images', 'secondpage.jpg'), 'rb') as f:  
    line\_bot\_api.set\_rich\_menu\_image(rich\_menu\_id, 'image/jpeg', f)

*   (optional) in list\_richmenus.py

from pprint import pprint  
from linebot import LineBotApi

LINE\_CHANNEL\_ACCESS\_TOKEN = "<your LINE\_CHANNEL\_ACCESS\_TOKEN>"  
line\_bot\_api = LineBotApi(LINE\_CHANNEL\_ACCESS\_TOKEN)

rich\_menu\_list = line\_bot\_api.get\_rich\_menu\_list()  
pprint(rich\_menu\_list)

\# delete all richmenus  
\# for rm in rich\_menu\_list:  
\#     line\_bot\_api.delete\_rich\_menu(rm.rich\_menu\_id)

*   run create\_firstpage.py & create\_secondpage.py to create rich menu

\>>> cd RichMenu  
\>>> python create\_firstpage.py  
\>>> python create\_secondpage.py

*   at the bottom of tutorialbot\\views.py

Modify your handle\_postback function. You should fill in the id for each RichMenu. Once you forget it you can use list\_richmenus.py to find it.

[@handler](http://twitter.com/handler "Twitter profile for @handler").add(PostbackEvent)  
def handle\_postback(event):  
    line\_id = event.source.user\_id  
    if event.postback.data == "promotion=true":  
        user\_profile = UserProfile.objects.get(line\_id=line\_id)  
        user\_profile.promotable = True  
        user\_profile.save()

line\_bot\_api.reply\_message(  
            event.reply\_token,  
            \[  
                TextSendMessage(text="Thanks\\U0010007A"),  
            \]  
        )  
    elif event.postback.data == "action=nextpage":  
        line\_bot\_api.link\_rich\_menu\_to\_user(line\_id, "<firstpage richmenu id>")  
    elif event.postback.data == "action=previouspage":  
        line\_bot\_api.link\_rich\_menu\_to\_user(line\_id, "<secondpage richmenu id>")

*   evaluate the result

![](/images/posts/20200212_linebot_django_tutorial/5340984a-8b97-4fad-9ad3-ee9f869ee3ef.png)
