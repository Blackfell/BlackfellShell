def main(self, greet):
    """Example function to print hello in the agent"""
    
    print("Hello, {}, you're now in {}".format(greet , helper(self)))
    self.command = 'test ' + greet
    self.send_command()
    self.recv_command()

def helper(self):
    return "Agent {}".format(self.name)
