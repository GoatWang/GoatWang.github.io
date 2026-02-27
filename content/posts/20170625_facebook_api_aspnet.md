---
title: Use Facebook API to login Asp.Net Identity
date: '2017-06-25T07:42:19+00:00'
draft: false
categories:
- Web Development
summary: Introduction Due to facebook api's change on its query string. The built-in
  connecting system to facebook has some error. Unlike google authencation, you only
  have to input the ClientId, ClientSecret ...
---

# Introduction

Due to facebook api's change on its query string. The built-in connecting system to facebook has some error. Unlike google authencation, you only have to input the ClientId, ClientSecret and set down the google end app, then you can successfully connect to google Api. However, you have to redefine the querystring in facebook authencation.more To be mentioned, you can only get emails of users in default setting in both all approach of authencation. If you want to get username, some code have to be edit more complicatedly. Nevertheless, even if you know how to edit code to get more information of users from facebook(or google), the port of Asp.Net Indentity to third party authencation system can only allow you to ask for name and email. This is restricted by Identity class. You can only get access to other private information by editing this calss' inner code. This is quit different from other program language because Identity is supported by Microsoft. And other language's methods to connect to third party api are often supported by third party.

# Tools on Facebook Api

There are two tools on facebook api for you to do authencation process: "Facebook Login" and "Account Kit". And this article focus on the second method.

![](/images/posts/20170625_facebook_api_aspnet/5ee95de9-2d29-4c7e-b2d6-d1805d0d21aa.jpeg)

| Item | connecting method | what you will get? | advantage |
| --- | --- | --- | --- |
| facebook login | Front end(View) connection\* | name | easy |
| Account Kit | Server end(Controller) connection | name, email, and other\*\* | flexible |

*\*This way is quit easy. If you have some basic knowledge of javascript, you will successfully connect your view to facebook by reading its instruction. And you don't have to use Identity class in this way.*

*\*\*If you want more information, first you have to modify the inner code of Identity calss to fit facebook api's requirement. second, you have to apply to facebook for asking agreement to other facebook users for more information. Third, every time a new user login your website through fb, they will be ask for authorization. Once they reject, you can get information they agree to give to you.*

# Notice

By the way, the way to apply for a fb developer account is quit easy. And a lot of articles have complete this part. As a result, I don't want to waist time and space to write again. So this article assume you have an fb developer account and you have got AppId and AppSecret from facebook.

# Open Project and prepare utility for Identity class to use

## Open an MVC project with idntity

![](/images/posts/20170625_facebook_api_aspnet/ff963aba-75c7-406e-b140-bb6919cde7b1.jpeg)

## **Create FacebookBackChannelHandler.cs class file in fb directory**

![](/images/posts/20170625_facebook_api_aspnet/0027829f-7c2a-4844-aff2-9cb3b52408fb.jpeg)

![](/images/posts/20170625_facebook_api_aspnet/5cd4bdc8-103d-4426-a13b-4d060435c412.jpeg)

![](/images/posts/20170625_facebook_api_aspnet/79553006-0bcd-4643-8c96-fb938d21fdc0.jpeg)

```json
    public class FacebookBackChannelHandler : HttpClientHandler
    {
        protected override async System.Threading.Tasks.Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, System.Threading.CancellationToken cancellationToken)
        {
            if (!request.RequestUri.AbsolutePath.Contains("/oauth"))
            {
                //Because fb has changed it querysteing format, so you have to redefine this to achieve its requirement.
                //Original: https://graph.facebook.com/v2.4/me?access_token=ABC
                //Now: https://graph.facebook.com/v2.4/me?fields=id,name,email&access_token=ABC
                request.RequestUri = new Uri(request.RequestUri.AbsoluteUri.Replace("?access_token", "&access_token"));
            }

            var result = await base.SendAsync(request, cancellationToken);
            if (!request.RequestUri.AbsolutePath.Contains("/oauth"))
            {
                return result;
            }

            var content = await result.Content.ReadAsStringAsync();
            var facebookOauthResponse = JsonConvert.DeserializeObject<FacebookOauthResponse>(content);

            var outgoingQueryString = HttpUtility.ParseQueryString(string.Empty);
            outgoingQueryString.Add("access_token", facebookOauthResponse.access_token);
            outgoingQueryString.Add("expires_in", facebookOauthResponse.expires_in + string.Empty);
            outgoingQueryString.Add("token_type", facebookOauthResponse.token_type);
            var postdata = outgoingQueryString.ToString();

            var modifiedResult = new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(postdata)
            };

            return modifiedResult;
        }
    }

    public class FacebookOauthResponse
    {
        public string access_token { get; set; }
        public string token_type { get; set; }
        public int expires_in { get; set; }
    }
```

## Modify Startup.Auth

![](/images/posts/20170625_facebook_api_aspnet/b5455daa-5933-4a9d-9cab-d63268a48fa3.jpeg)

![](/images/posts/20170625_facebook_api_aspnet/011c0dca-d1d8-4f51-b4a0-524188a5fdaf.jpeg)

```json
            var facebookOptions = new FacebookAuthenticationOptions()
            {
                AppId = "{{Your AppId}}",
                AppSecret = "{{Your AppSecret}}",
                //The class you have defined beforehand
                BackchannelHttpHandler = new FacebookBackChannelHandler(),
                //You can difine facebook version yourdself(VX.X below)
                UserInformationEndpoint = "https://graph.facebook.com/v2.4/me?fields=id,name,email"
            };
            app.UseFacebookAuthentication(facebookOptions);
```

## Build your project

ctrl + shift + b

# Model and ViewModel

## Edit database column and IdentityModel.cs

See notice in the tail of this article

## AccountViewModel.cs(get username from view)

![](/images/posts/20170625_facebook_api_aspnet/8c3ad974-e850-4186-b95e-0aa260d4ca7c.jpeg)

![](/images/posts/20170625_facebook_api_aspnet/6826da80-2049-4097-8214-c21dfc22111d.jpeg)

```json
    public class ExternalLoginConfirmationViewModel
    {
        [Required]
        [Display(Name = "電子郵件")]
        public string Email { get; set; }
        [Required]
        [Display(Name = "姓名")]
        public string Name { get; set; }
    }
```

# Controller

## AccountController.cs(get username from fb)

![](/images/posts/20170625_facebook_api_aspnet/a92e51ac-6d36-45bd-ae5c-b53299e025b3.jpeg)

### ExternalLoginCallback Action

![](/images/posts/20170625_facebook_api_aspnet/5125d6e3-0ec7-4bb1-9fac-d01374bcd350.jpeg)

```json
        [AllowAnonymous]
        public async Task<ActionResult> ExternalLoginCallback(string returnUrl)
        {
            var loginInfo = await AuthenticationManager.GetExternalLoginInfoAsync();
            if (loginInfo == null)
            {
                return RedirectToAction("Login");
            }

            var result = await SignInManager.ExternalSignInAsync(loginInfo, isPersistent: false);
            switch (result)
            {
                case SignInStatus.Success:
                    return RedirectToLocal(returnUrl);
                case SignInStatus.LockedOut:
                    return View("Lockout");
                case SignInStatus.RequiresVerification:
                    return RedirectToAction("SendCode", new { ReturnUrl = returnUrl, RememberMe = false });
                case SignInStatus.Failure:
                default:
                    ViewBag.ReturnUrl = returnUrl;
                    ViewBag.LoginProvider = loginInfo.Login.LoginProvider;
                    return View("ExternalLoginConfirmation", new ExternalLoginConfirmationViewModel { Email = loginInfo.Email, Name=loginInfo.DefaultUserName });
            }
        }
```

### ExternalLoginConfirmation Action

![](/images/posts/20170625_facebook_api_aspnet/1bc71e70-f59c-40da-bcd4-335d49ef69d7.jpeg)

```json
        [HttpPost]
        [AllowAnonymous]
        [ValidateAntiForgeryToken]
        public async Task<ActionResult> ExternalLoginConfirmation(ExternalLoginConfirmationViewModel model, string returnUrl)
        {
            if (User.Identity.IsAuthenticated)
            {
                return RedirectToAction("Index", "Manage");
            }

            if (ModelState.IsValid)
            {
                var info = await AuthenticationManager.GetExternalLoginInfoAsync();
                if (info == null)
                {
                    return View("ExternalLoginFailure");
                }
                var user = new ApplicationUser { UserName = model.Name, Email = model.Email };
                var result = await UserManager.CreateAsync(user);
                if (result.Succeeded)
                {
                    result = await UserManager.AddLoginAsync(user.Id, info.Login);
                    if (result.Succeeded)
                    {
                        await SignInManager.SignInAsync(user, isPersistent: false, rememberBrowser: false);
                        return RedirectToLocal(returnUrl);
                    }
                }
                AddErrors(result);
            }

            ViewBag.ReturnUrl = returnUrl;
            return View(model);
        }
```

# View

## ExternalLoginConfirmation.cshtml

![](/images/posts/20170625_facebook_api_aspnet/482aba6c-f584-4a96-abbb-5ed6e3b35fea.jpeg)

![](/images/posts/20170625_facebook_api_aspnet/123dc2b9-79d1-44a7-b518-9db4629bd48c.jpeg)

```json
    <div class="form-group">
        @Html.LabelFor(m => m.Name, new { @class = "col-md-2 control-label" })
        <div class="col-md-10">
            @Html.TextBoxFor(m => m.Name, new { @class = "form-control" })
            @Html.ValidationMessageFor(m => m.Name, "", new { @class = "text-danger" })
        </div>
    </div>
```

# Usage

## Login.cshtml

![](/images/posts/20170625_facebook_api_aspnet/e2147f5a-841c-473f-aa55-f98add553d76.jpeg)

## ctrl + F5

![](/images/posts/20170625_facebook_api_aspnet/c5119fb2-644d-4088-baf4-c9750d4f9d3d.jpeg)

# Database

![](/images/posts/20170625_facebook_api_aspnet/6ed41bc7-ff12-4861-b426-9a5bfcbb5b96.jpeg)

![](/images/posts/20170625_facebook_api_aspnet/10e8874f-c9cc-4592-b581-c549507c5679.jpeg)

![](/images/posts/20170625_facebook_api_aspnet/612e9ed2-463b-422f-942c-8f211284ebcd.jpeg)

# Notice

## Database Column Issue

***If you want to truely use this in your website, I suggest you to add a column to your database. This will ask you to learn some code first database generation techniques which use datacase migration to done this work. There are two reasons for you to do that. First, email as login username is more rememberable. Second, If you want mix Identity inner-built login system, you also have to moidify general login code to write the match the column and user input***

## Database Storage Issue

***Originally, its default path to database is app\_Data built in your project. If you want to move to other place. you have first to modify the connecting string in web.config(in the bottom of your project manager). Then start your first login. If you have loggged in before. you had better delete all your migration log, then start migration mechanism.***

## Publish on Azure

***Even if I tried several times, I can't get authorization from facebook Some times once I publish on azure. However, sometimes it works. I am still deal with this problem***

![](/images/posts/20170625_facebook_api_aspnet/7b18f243-db34-45f0-a3b8-cba6ba97ec84.jpeg)
