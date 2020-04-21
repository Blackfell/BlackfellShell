
from os import getcwd

def main(dropper, args=None):
    try:
        dropper.send("Current directory:\n{}".format(getcwd()))
    except Exception as e:
        dropper.send("ERROR - {} can't get working directory because : {}".format(dropper.name, args, e))
