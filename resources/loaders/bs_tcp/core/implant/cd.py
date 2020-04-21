from os import chdir, getcwd

def main(dropper, args=None):
    if args:
        try:
            if '~' in args:
                print("DEBUG - scrubbing tildae from listing:")
                args = re.sub('~', getenv('HOME'), args)
            chdir(args) # changing the directory
            dropper.send("{} changed directory to : {}".format(dropper.name, getcwd()))
        except Exception as e:
            dropper.send("ERROR - {} failed to cd to {} because : {}".format(dropper.name, args, e))
    else:
        try:
            dropper.send("Current directory:\n{}".format(getcwd()))
        except Exception as e:
            dropper.send("ERROR - {} can't get working directory because : {}".format(dropper.name, args, e))
