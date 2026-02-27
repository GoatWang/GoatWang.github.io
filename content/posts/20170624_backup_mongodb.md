---
title: Backup mlab Mongodb To Local Peroidically by C#
date: '2017-06-24T17:26:27+00:00'
draft: false
categories:
- Tools & DevOps
summary: Introduction At first, I try to use mlab built-in backup system. However,
  it's not include in its free 500mb program. As a result, I wrote a C# program to
  back up by myself.more Use cmd to backup mlab...
---

# Introduction

At first, I try to use mlab built-in backup system. However, it's not include in its free 500mb program. As a result, I wrote a C# program to back up by myself.more

# Use cmd to backup mlab

![](/images/posts/20170624_backup_mongodb/d6fe950d-5a67-4de9-b326-60eb5f46ee00.jpeg)

If you have a mlab account, you can find this in the first page after you login. The way to backup the whole database to your local client is to use code under export Database:

mongodump -h ds155841.mlab.com:55841 -d -u -p -o

Once you succeed, you will get:

![](/images/posts/20170624_backup_mongodb/7072eb3e-5ee3-4c1a-9826-d4fdfa94f77d.jpeg)

And you can go to the dircetory you define as output directory. And foreach collection, you will get two output dump file "collectionName.bson" and "collectionName.metadata.json"

# Use C# to manipulate cmd

First, Open a console project. {% asset\_img 2VsConsoleProj.JPG Open Console Project%}

Second, input codes below in the Main thread

```json
using System.Diagnostics;

static void Main(string[] args)
{
    //This ProcessStartInfo class define the environment in which you want to open the cmd prompt
    ProcessStartInfo startInfo = new ProcessStartInfo
    {
        //Right under this directory, You will have to find MongoDump Directory
        WorkingDirectory = "D:\\<Yoru working directory>",  
        //The program you want to execute. Because you have added mongodump.exe to your environment path, you don't have to give the cmd line absolute path to find the executable.
        FileName = "mongodump",
        Arguments = "-h ds155841.mlab.com:55841 -d <databaseName> -u <user> -p <password> -o MongoDump\\" + DateTime.Now.ToString("yyyyMMddhhmm"),
        //CreateNoWindow = true,  //Once I set the process started by windows schedule, the prompt window will not show. If you have this problem you can try to set this parameter. 
        UseShellExecute = false,
        RedirectStandardOutput = true
    };

    Its a class to manipulate cmd line
    using (Process exeProcess = Process.Start(startInfo))
    {
        if (exeProcess != null) exeProcess.WaitForExit();
        //We don't need any return words, therefore you can ignore the code below.
        while (!exeProcess.StandardOutput.EndOfStream)
        {
            string line = exeProcess.StandardOutput.ReadLine();
            // do something with line
            Console.WriteLine("This Line is written by me" + line);
        }
    }
}
```

Third, set build type to be "release", then build the program.

![](/images/posts/20170624_backup_mongodb/43741cf3-fce4-4734-aa51-7004a844e9a2.jpeg)

![](/images/posts/20170624_backup_mongodb/bd3b11bd-30f4-48f2-a0f6-143b21b87418.jpeg)

Fourth, check the directory of your console project, and find "\\bin\\Release\\YourProjName.exe". Once you execute this exeutable file, you will start the same process with using cmd to dump. In this way, you have successfully manipulated cmd by C#.

# Use Windows10 task schedulor to execute this program autometically

this you can directly refer to [this video](https://www.youtube.com/watch?v=w2PiUmhQ6-A)
