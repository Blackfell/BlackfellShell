
def main(self):
    """Example function to print hello in the implant"""

    print("TEST")
    print("Hi, {}, you're now in implant".format(self.args))
    self.resp = "Hi {}, you're now in the implant: {}".format(self.args, self.name)

def helper(self):
    return str(self.cmd)
