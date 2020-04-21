# BlackfellShell

A Python module runner & Implant management tool.

# What it do?

BlackfellShell is a Python framework deisgned to run and manage Python modules for CTFs and Pen Testing like activities. BlackfellShell drops you into an interactive prompt, which will let you configure and run Python scripts, with built in Agent functionality being the main function of the framework.

## Agents?

The main reason BlackfellShell was written was to run Agents; an Agent is a combination of a Listener and Dropper, the Dropper runs on a target machine and a Listener communicates with it and tells it that to do. You can set up a Listener, send a Dropper to a target machine, then start sending modules down an encrypted link, to load extra functionality into the target.

# Installation

BlackfellShell is designed to run on Linux, but is not intentionally designed as such; it should be possible to run most funcitonality on Windows too. Start by cloning or downloading this repository:

```
git clone https://github.com/Blackfell/BlackfellShell
```

Next, run the install script for your platform. The main reason you need to run the install scripts is to allow you to cross complile your droppers from Linux for Windows; this requires wine, which should 'just work' on Pen Testing Linux distributions like Kali Linux; the installer script will check! If you skip the scripts, you can run:

```
python -m pip install -r requirements.txt
```

But be warned, your cross-compiling may fail.

## On windows

Run the setup script:

```
PS C:\> ./setup.bat
```

Then follow each prompt, installing Windows Subsystem For Linux, if you're interested in cross-compiling.

## On Linux


Run the setup script:

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
