# BlackfellShell

A Python module runner & Implant management tool. Capable of cross-compliling and managing agents on Linux and Windows 10 (framework side); dropper exectuables can be run on various versions of Linux and Windows.

![BlackfellShell Demo Gif](https://blackfell.net/assets/images/posts/BlackfellShell/BlackfellShell.gif)

# What it do?

BlackfellShell is a Python framework deisgned to run and manage Python modules for CTFs and Pen Testing like activities. BlackfellShell drops you into an interactive prompt, which will let you configure and run Python scripts, with built in Agent functionality being the main function of the framework.

## Agents?

The main reason BlackfellShell was written was to run Agents; an Agent is a combination of a Listener and Dropper, the Dropper runs on a target machine and a Listener communicates with it and tells it that to do. You can set up a Listener, run a Dropper on a target machine, then start sending modules from Listener to Dropper down an encrypted link, loading extra functionality into the target.

# Installation

BlackfellShell was written on Linux, but is designed to run on Windows too. Start by cloning or downloading this repository:

```
git clone https://github.com/Blackfell/BlackfellShell
```

Next, for easy install, run the install script for your platform. The main reason you may want to run the install scripts is to allow you to cross complile your droppers; this requires wine or WSL on Windows 10.

## The No-Installer way

If you just want to skip the scripts, you already have a Wine or WSL environment set up, you can run a simple install as follows:

```
python -m pip install -r requirements.txt
```

### On linux

Install wine, using whatever pakage manager you like and get a Windows Python installer; if you're on a 64 bit system, [Version 3.8.2](https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe) has been tested and works well (remember to always verify your downloads!). Next step is to install wine correctly for cross-compliation:

```
wine ./python-3.8.2-amd64.exe
```

Will install Python, follow all the prompts on the installer. Then configure Python:

```
wine py -3.8 -m pip install -r requirements.txt
```

Now you're ready to go!

### On Windows

Cross compilation uses Windows Subsystem for Linux, so cross-compilation only works on Windows 10, where this is enabled.

If cross compiling isn't a concern for you, simply running:

```
PS C:\> python -m pip install -r requirements.txt
```

Will get you all the setup required for Windows to Windows compilation.

If you'd still like to cross-compile, it's possible to run the framework if you already have WSL enabled adn the Ubuntu package installed and configured. Ubuntu will need a Python3 installation and Python3-pip. If you meet these requirements already, simply running:

```
PS C:\> ubuntu -c 'python3 -m pip install -r requirements.txt'
```

Will allow you to cross-compile on Windows to Linux, without needing the setup script.

## On windows

Setup is handled via a small PowerShell script. The script will chack (and install if missing) Python, Windows Subsystem For Linux, Ubuntu Bash and Python dependencies. It will speed up install significantly if you already have a WSL Ubuntu environment installed; you may wish to do this manually before you start, but it's not required.

To run the setup script, you'll first need to make sure you can run PowerShell scripts on your system; the following often works for a one-off script:

```
PS C:\> powershell -ExecutionPolicy ByPass
Windows PowerShell
Copyright (C) Microsoft Corporation. All Rights Reserved.

PS C:\>
```

After you're in a powershell script enabled prompt, simply type:

```
PS C:\> ./setup.ps1
```

Then follow each prompt, installing Windows Subsystem For Linux, if you're interested in cross-compiling. The script will install the Ubuntu distribution and configure Python for you, you'll still have to do a fair bit of clicking through etc. and set up your Ubuntu environment once installed.

The setup script will walk you through.

## On Linux


Setup is managed via a bash scripts, The script will chack (and install if missing) Python, Wine and Python dependencies. It will speed up install significantly if you already have a wine and associated python environment installed; you may wish to do this manually before you start, but it's not required.

To check and install required tools, simply run the setup script:

```
~$ ./setup.sh
```

Then follow each prompt, installing Wine and Python, if you're interested in cross-compiling.

## Done?

When you use the BlackfellShell, it will test and report on installation state, so if you have any problems, you'll be told!

# How I use it?

You can get started in BlackfellShell by simply running:

```
~$ blackfell.py

```

Which will drop you into the interpreter. From there, type:

```
BS > help
```

To get general help, or:

```
BS > help <command>
```

To get help on a specific command.

## How about a demo?

There is a built in demo command in the home menu; if you run this command, you'll get a simple walkthrough of the very fundamentals of modules and how they're supposed to work.

```
BS > demo
```

You'll be walked through an example module, why not run it yourself once you've done?

## Just get me started

There is also an example resource file, packaged with the repo 'example.bs'; resource files are intended to function in a similar way to metasploit resource files - they allow you to automate the BlackfellShell at startup. You can call the BlackfellShell with the example resource file like this:

```
~$ blackfell.py -r example.bs
```

Once this file runs, you'll have a Windows and Linux Dropper that are both configured to talk to a localhost listener. If you run this dropper within 60 seconds of creation, the resource file will also automatically activate and interact with your agents.

From there, hit help and remember tab completion!

# How it work?

Droppers and Listeners are special modules  in the BlackfellShell, a Listener listens and a Dropper calls back to its Listener and runs commands the Listener gives it. This means you can create a Listener, generate a load of Droppers for it, then drop them on target machines.

Listeners need to be created first, they run as a thread, and when a Dropper connects, an Agent thread is started to manage that individual session. Agents can be interacted with from the agents menu, where they can be listed and activated. Once activated, typing 'interact' will allow you to interact with any active agents.

```
BS >
BS > agents

BS : Agents > list

[-] Agents:

Name                           Activated  Listener             Status     Info                          
====================================================================================================
agt-lnr-1-1                    False      lnr-1                Alive      192.168.235.1:48398           
agt-lnr-1-2                    False      lnr-1                Alive      192.168.235.159:50501         

BS : Agents > activate agt-lnr-1-1
[-] - Activating: agt-lnr-1-1
BS : Agents > interact
[+] - Interacting with 1 active agents
BS : Interacting - 1 Agents > info
[-] Acting on agent: agt-lnr-1-1, which is alive: True
BS : Interacting - 1 Agents >
```

Once you're interacting with agents, help commands will get you much of the way. Good luck!

# I want Moar

This project is very much in development; its posted on GitHub to allow people to review and feedback. If you have a suggestion, feature, complaint, funny story, write to: info@blackfell.net.
